# sources/distributed-fs/ceph-client/tools/sched_ext/scx_qmap.c

Purpose: user-space loader, option parser, and monitor for the qmap sched_ext example.

Important APIs/functions: parses options for slice, error/stall injection, infinite-loop trigger, dispatch batch, DSQ/event printing, debug messages, high-priority boosting, sub-cgroup path, disallowed PID, exit dump length, dump suppression, partial switching, always-enqueue-immediate, immediate stress, verbosity, and help. Uses `SCX_OPS_OPEN()`, `SCX_OPS_LOAD()`, `SCX_OPS_ATTACH()`, `UEI_EXITED()`, `UEI_REPORT()`, and `__COMPAT_has_ksym()`.

Control flow: open skeleton, set default `slice_ns`, parse options into rodata/bss/struct_ops fields, resolve `-c` cgroup path with `stat()` and store inode as sub-cgroup ID, set flags for partial switching and always-immediate modes, load and attach, then print scheduler counters and optional cpuperf statistics once per second until signal or UEI exit. It detaches, reports, destroys, and exits without hotplug restart because qmap implements CPU online/offline callbacks.

State and persistence: no filesystem persistence. Runtime state is the skeleton, struct_ops link, signal flag, and BPF maps/globals exposed through skeleton fields.

Dependencies and integration: generated skeleton, libbpf, sched_ext common headers, `sys/stat.h` for cgroup inode lookup, and optional cpuperf ksym.

Risks: many options intentionally enable failure or pathological behavior. `-c` uses `st_ino` as cgroup ID and assumes the supplied path is a cgroup. Counters are read locklessly from BPF globals, so monitoring is approximate.

Test signals: option parsing coverage, cgroup sub-scheduler attachment with `-c`, stats output, cpuperf output only when ksym exists, signal cleanup, and expected no-restart behavior on CPU hotplug.
