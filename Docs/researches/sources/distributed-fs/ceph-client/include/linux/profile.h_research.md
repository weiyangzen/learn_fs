# sources/distributed-fs/ceph-client/include/linux/profile.h

Purpose: declares the legacy kernel profiling hooks for CPU, scheduler, and KVM profiling, including procfs exposure when profiling and procfs are enabled.

Important APIs and types: profiling type bits are `CPU_PROFILING`, `SCHED_PROFILING`, and `KVM_PROFILING`. `prof_on` gates profiling. APIs include `profile_init()`, `profile_setup()`, `profile_tick()`, `setup_profiling_timer()`, `profile_hits()`, and inline `profile_hit()`. `create_proc_profile()` creates procfs output when both relevant configs are enabled.

Control flow: boot/setup config enables a profiling type, periodic or event paths call `profile_tick()` / `profile_hit()`, and `profile_hit()` fast-paths out unless `prof_on` matches the event type. Multiple hits can be accumulated through `profile_hits()`.

State and persistence: profiling data is in-memory diagnostic state, optionally visible through procfs. It is not persistent across boot.

Dependencies and integration points: depends on kernel init, cache annotations, procfs, timer setup, scheduler/tick paths, and optional KVM profiling users.

Risks and test signals: risks include hot-path overhead when disabled, incorrect `prof_on` type matching, procfs exposure mismatches, and timer multiplier errors. Test enabled and disabled profiling configs, proc profile creation, boot parameter parsing, and event accounting under CPU and scheduler load.
