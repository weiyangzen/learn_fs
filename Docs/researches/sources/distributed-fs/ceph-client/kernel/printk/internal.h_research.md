# sources/distributed-fs/ceph-client/kernel/printk/internal.h

## Purpose

`internal.h` is the private interface shared by printk implementation files. It centralizes build-dependent stubs, console flushing policy, nbcon hooks, message buffer structures, printk ringbuffer accessors, sysctl hooks, and cross-file state flags.

## Important APIs, types, and macros

Important declarations include `printk_sysctl_init()`, `devkmsg_sysctl_set_loglvl()`, `con_printk()`, `force_legacy_kthread()`, `PRINTK_PREFIX_MAX`, `PRINTK_MESSAGE_MAX`, `PRINTKRB_RECORD_MAX`, `enum printk_info_flags`, `vprintk_store()`, `vprintk_default()`, printk-safe enter/exit helpers, `printk_parse_prefix()`, console lock handover helpers, nbcon sequence/allocation/kthread/flush functions, and `printk_get_next_message()`.

`struct console_flush_type` describes which output paths to use: `nbcon_atomic`, `nbcon_offload`, `legacy_direct`, and `legacy_offload`. `printk_get_console_flush_type()` computes the flush strategy from nbcon priority, registered console classes, boot console presence, kthread state, panic state, deferred legacy policy, and irq-work availability. `struct printk_buffers` and `struct printk_message` define the shared out/scratch buffers and a formatted message container.

## Control flow

Most callers store a record, call `printk_get_console_flush_type()`, then either flush nbcon consoles atomically, wake nbcon kthreads, run the legacy loop directly, or defer to irq work/legacy kthread. Panic and emergency contexts move `nbcon_get_default_prio()` away from normal priority and narrow the permitted output paths. When `CONFIG_PRINTK` is disabled, stubs preserve API availability while returning no work.

## State and persistence behavior

The header declares cross-file global state owned mostly by `printk.c`: `prb`, `printk_kthreads_running`, `printk_kthreads_ready`, `debug_non_panic_cpus`, `have_boot_console`, `have_nbcon_console`, `have_legacy_console`, `legacy_allow_panic_sync`, `console_irqwork_blocked`, and `printk_shared_pbufs`. These flags persist for runtime and drive both console registration and output decisions.

## Dependencies and integration points

It depends on console core types, sysctl declarations, `enum nbcon_prio`, rcuwait, task command sizes under execution-context support, and the printk ringbuffer type. This header is the contract between `printk.c`, `nbcon.c`, `index.c`, `sysctl.c`, `printk_safe.c`, and ringbuffer support. It also bridges external console driver callbacks by defining the buffers and ownership checks that nbcon write callbacks use.

## Risks and test signals

Flush policy changes are high risk because they affect panic visibility, PREEMPT_RT behavior, boot consoles that may share hardware with real consoles, and scheduler-context logging. The disabled-`CONFIG_PRINTK` stubs must remain ABI-compatible with enabled declarations. Coverage should include normal boot, boot-console handoff, nbcon-only, legacy-only, mixed boot/nbcon, PREEMPT_RT, panic flushing, emergency sections, `CONFIG_PRINTK=n`, and sysctl-enabled builds.
