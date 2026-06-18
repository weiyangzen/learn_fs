# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/user_exit_info.bpf.h

Purpose: BPF-side definitions for sharing sched_ext exit status, message, and debug dump data with user space.

Important APIs/macros: `UEI_DEFINE(name)` declares a resizable dump array, dump length rodata, and `struct user_exit_info` in `.data`. `UEI_RECORD(name, ei)` copies `reason`, `msg`, and `dump` from `struct scx_exit_info`, conditionally records `exit_code`, and publishes `kind` with an atomic compare-and-swap as a memory barrier.

Control flow: BPF schedulers call `UEI_RECORD()` from their `.exit` callback. User space polls the shared data through the skeleton.

State and persistence: BPF `.data` holds the exit info and dump buffer for the lifetime of the loaded scheduler.

Dependencies and integration: includes `vmlinux.h`, `bpf_core_read.h`, and `user_exit_info_common.h`. All sched_ext examples in this subset use `UEI_DEFINE(uei)` and record exit information.

Risks: dump size must be set correctly from user space or defaults are used. Atomic publication assumes readers observe `kind` after reason/message/dump have been copied.

Test signals: force normal exit, BPF error exit, and dump-producing exit; verify `UEI_EXITED()` and `UEI_REPORT()` in user space observe complete data.
