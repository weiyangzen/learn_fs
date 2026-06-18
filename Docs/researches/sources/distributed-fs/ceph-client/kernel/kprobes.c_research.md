# sources/distributed-fs/ceph-client/kernel/kprobes.c

## Purpose
`kprobes.c` implements dynamic instrumentation for kernel text. It registers and unregisters kprobes and kretprobes, manages breakpoint or ftrace-based arming, aggregates multiple probes at one address, allocates executable out-of-line instruction slots, performs optional jump optimization, maintains blacklists, tracks module lifetime, and exports debugfs/sysctl controls.

## Important APIs, Types, And Functions
The main exported APIs are `register_kprobe()`, `unregister_kprobe()`, batch variants, `enable_kprobe()`, `disable_kprobe()`, `register_kretprobe()`, `unregister_kretprobe()`, `kprobe_on_func_entry()`, `kprobe_flush_task()`, and blacklist/kallsyms helpers. Core state includes `kprobe_table[]`, `kprobe_mutex`, per-CPU `kprobe_instance`, `kprobes_all_disarmed`, `kprobe_blacklist`, and optimization lists. Architecture hooks provide instruction preparation, arming, disarming, relocation, optimized probes, ftrace handlers, and exception notification.

## Control Flow
`register_kprobe()` canonicalizes symbol/address/offset, rejects reserved text, takes module references, and calls `__register_kprobe()`. If a probe already exists at the address, `register_aggr_kprobe()` creates or reuses an aggregator and chains handlers; otherwise it prepares the instruction, inserts into the hash table, arms it, and attempts optimization. Unregistration disables/disarms under `kprobe_mutex`, removes hash/list entries, synchronizes RCU, and frees architecture slots. Kretprobes install a normal entry kprobe whose pre-handler allocates a return instance and hooks the return path through either objpool/trampoline or rethook.

## State And Persistence
Registered probes persist in the static hash table until unregistered or killed by module/init-memory teardown. Instruction slots live in executable pages and are mark-and-sweep reclaimed after RCU grace periods. Optimization queues persist until the `kprobe-optimizer` kthread processes them. Debugfs exposes `/sys/kernel/debug/kprobes/list`, `enabled`, and `blacklist`; sysctl `debug/kprobes-optimization` toggles optimization when enabled.

## Dependencies And Integration Points
This file integrates with kallsyms, modules, ftrace, perf ksymbol events, static calls, jump labels, CPU hotplug locks, text patching via `text_mutex`, debugfs, sysctl, exception notifiers, RCU/tasks-RCU, rethook/objpool, and architecture-specific probe code.

## Risks And Edge Cases
Risks are high because the code modifies live kernel text. It must avoid blacklisted/noinstr/CFI/jump-label/static-call/BUG/gate areas, handle module `.init.text` and unloading, preserve RCU safety while breakpoint handlers traverse tables, avoid optimizer deadlocks with CPU hotplug and `text_mutex`, and prevent ftrace IPMODIFY conflicts. Kretprobe pools can miss returns under pressure, incrementing `nmissed`.

## Test Signals
Signals include registering by symbol and address, duplicate-address aggregation, enable/disable and global debugfs toggling, optimization sysctl on/off, ftrace-backed probes, module load/unload cleanup, blacklist contents, kretprobe return handling and maxactive exhaustion, concurrent registration/unregistration stress, and architecture kprobe selftests.
