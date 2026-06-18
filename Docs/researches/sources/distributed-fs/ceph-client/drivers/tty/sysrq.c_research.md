# Research: sources/distributed-fs/ceph-client/drivers/tty/sysrq.c

## Purpose

`sysrq.c` implements Linux Magic SysRq handling for the tty/input subsystem. It maps SysRq keys to privileged emergency operations, exposes registration APIs for modules, handles `/proc/sysrq-trigger`, manages the `/proc/sys/kernel/sysrq` sysctl mask, and, when input support is enabled, filters keyboard input to detect Alt-SysRq combinations and optional reset key sequences.

## Important APIs, Types, and Functions

Global configuration is held in `sysrq_enabled` and `sysrq_always_enabled`. `sysrq_mask`, `sysrq_toggle_support`, `handle_sysrq`, `__handle_sysrq`, `register_sysrq_key`, and `unregister_sysrq_key` are the primary external interfaces. `sysrq_key_table` maps digits and letters to `struct sysrq_key_op` handlers. Built-in handlers cover loglevel, SAK, unraw keyboard mode, crash, reboot, sync, timer display, remount read-only, lock display, CPU backtraces, register display, task state, blocked tasks, ftrace dump, memory display, SIGTERM/SIGKILL to user tasks, manual OOM, filesystem thaw, RT task normalization, and console log replay.

With `CONFIG_INPUT`, `struct sysrq_state` stores per-input-device filter state: input handle, reinjection work, pressed-key bitmaps, active Alt/SysRq state, shift state, reset-sequence state, and reset timer. The input path uses `sysrq_filter`, `sysrq_handle_keypress`, `sysrq_reinject_alt_sysrq`, `sysrq_connect`, and `sysrq_disconnect`. Reset-sequence configuration is provided by device tree (`/chosen/linux,sysrq-reset-seq`) and module parameters `reset_seq` and `sysrq_downtime_ms`.

## Control Flow

At device init time, `sysrq_init` creates `/proc/sysrq-trigger` when procfs is enabled and registers the input handler if SysRq is enabled. A separate `subsys_initcall` registers the sysctl table for `kernel.sysrq`. The `sysrq_always_enabled` boot option bypasses normal mask disabling.

Programmatic handling enters `handle_sysrq`, which checks `sysrq_on` and delegates to `__handle_sysrq` with mask checking. `/proc/sysrq-trigger` calls `__handle_sysrq` without mask checks; when the first written byte is `_`, it processes all following bytes as a bulk sequence. `__handle_sysrq` temporarily unsuppresses printk, enters RCU SysRq context, forces console printing for feedback, looks up the operation, enforces the enable mask if requested, runs the handler, or prints one help entry for each unique registered operation.

The input path registers on devices with `EV_KEY` and `KEY_LEFTALT`. `sysrq_filter` suppresses or passes events. `sysrq_handle_keypress` tracks Alt, Shift, and SysRq; once Alt-SysRq is active, the next non-repeat key is translated through `sysrq_xlate`, optionally uppercased by Shift, and passed to `__handle_sysrq`. If Alt-SysRq was pressed without a command, `sysrq_reinject_alt_sysrq` simulates the original key chord so normal PrintScreen behavior can still occur. Reset-sequence tracking runs when SysRq is inactive and calls `orderly_reboot` or falls back to SysRq reboot after configured key hold timing.

## State and Persistence Behavior

State is kernel-resident and lasts until reboot or module lifetime. The sysctl changes `sysrq_enabled` at runtime and registers or unregisters the input handler when the effective enabled state changes. Registered key operations mutate `sysrq_key_table` under `sysrq_key_table_lock` and use `synchronize_rcu` to prevent module text from being freed while a concurrent handler is running. Each input device gets separate `sysrq_state`; timers and work are torn down on disconnect.

## Dependencies and Integration Points

The file integrates with printk/console control, RCU, reboot/panic paths, emergency sync/remount/thaw, OOM, scheduler diagnostics, lockdep, ftrace, perf debug, VT keyboard support, input core, procfs, sysctl, device tree, and module parameter handling. It exports SysRq registration and dispatch symbols to other kernel code.

## Risks and Edge Cases

SysRq handlers are intentionally powerful and include crash, reboot, process kill, OOM, and remount operations; incorrect enable-mask configuration has direct system-availability impact. Some handlers run from constrained contexts, so the code schedules work for operations such as SAK, manual OOM, and remote CPU backtraces when direct execution is unsafe. Input reinjection uses memory barriers around `reinjecting`; regressions there could either leak Alt-SysRq events or suppress normal keyboard input. Key-table mutation relies on exact old-op matching, so unregistering with the wrong pointer fails. `/proc/sysrq-trigger` intentionally bypasses the sysctl operation mask, so access mode and ownership are the relevant control.

## Test Signals

Useful tests include sysctl toggling of `kernel.sysrq`, direct `handle_sysrq` calls from kernel tests, `/proc/sysrq-trigger` single and bulk writes, registration/unregistration of a temporary key op, input-event simulation for Alt-SysRq with and without a command key, reset sequence parsing through module parameters/device tree, and config-matrix builds for `CONFIG_INPUT`, `CONFIG_VT`, `CONFIG_LOCKDEP`, `CONFIG_SMP`, `CONFIG_TRACING`, `CONFIG_BLOCK`, and `CONFIG_PROC_FS`.
