# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/bus_lock.c

## Purpose
`bus_lock.c` implements x86 split-lock and bus-lock detection policy. It discovers whether the processor safely supports split-lock detection, parses `split_lock_detect=`, configures `MSR_TEST_CTRL` and `MSR_IA32_DEBUGCTLMSR`, handles user and guest split-lock traps, rate-limits bus-lock traps, and exposes `/proc/sys/kernel/split_lock_mitigate` when sysctl is enabled.

## Important APIs, Types, and Functions
`enum split_lock_detect_state` defines `off`, `warn`, `fatal`, and `ratelimit`. Global state includes `sld_state`, cached `msr_test_ctrl_cache`, `cpu_model_supports_sld`, `bld_ratelimit`, `sysctl_sld_mitigate`, and `buslock_sem`. Public integration points are `sld_setup()`, `split_lock_init()`, `bus_lock_init()`, `handle_guest_split_lock()`, `handle_user_split_lock()`, and `handle_bus_lock()`.

`split_lock_setup()` validates model/MSR support and enables `X86_FEATURE_SPLIT_LOCK_DETECT`. `sld_state_setup()` parses the boot parameter. `sld_update_msr()` toggles split-lock detection from the cached MSR value. `split_lock_warn()` provides the mitigation by delaying, serializing progress through `buslock_sem`, scheduling delayed re-enable work, and temporarily disabling split-lock detection on the current CPU.

## Control Flow
Early CPU identification calls `sld_setup(c)` from `common.c`. That probes known CPU models or `MSR_IA32_CORE_CAPS`, verifies `MSR_TEST_CTRL` writes, parses the command line, and prints selected behavior. Per-CPU initialization calls `split_lock_init()`: in rate-limit mode it disables split-lock #AC detection so bus locks are handled by #DB; otherwise it enables or disables split-lock detection according to `sld_state`.

Normal operation splits by trap type. `handle_user_split_lock()` handles #AC for user split locks and either returns false for fatal/alignment-check cases or warns and resumes. `handle_guest_split_lock()` lets KVM convert guest split locks into warn or SIGBUS behavior. `handle_bus_lock()` handles #DB bus-lock traps and applies warn, fatal, or rate-limit policy. `bus_lock_init()` programs `DEBUGCTLMSR_BUS_LOCK_DETECT` when bus-lock detection should be used.

## State and Persistence
The selected mode and cached MSR value are `__ro_after_init`; runtime state is the sysctl mitigation switch, per-task `reported_split_lock`, delayed works, ratelimit bucket, and semaphore. Split-lock MSR state is per core but treated per CPU; offline callback `splitlock_cpu_offline()` unconditionally re-enables detection to avoid sibling CPUs being left with detection disabled.

## Dependencies and Integration Points
The file depends on CPUID/CPU model matching, command-line parsing, MSR helpers, trap handling, workqueues, CPU hotplug, sysctl, ratelimit, and KVM exports. It is called by `common.c` during CPU identification and by trap/KVM paths when #AC or #DB events occur.

## Risks
`MSR_TEST_CTRL` must only be touched on known-safe CPUs; the file explicitly warns that unsupported writes can be unsafe. The temporary disable/re-enable path is sensitive to CPU hotplug and HT sibling behavior. Rate-limit parsing allows `ratelimit:N` only in 1..1000, so invalid input silently falls back to default. `sysctl_sld_mitigate=0` removes the semaphore/sleep mitigation and allows more concurrent bus-locked progress.

## Test Signals
Boot with `split_lock_detect=off|warn|fatal|ratelimit:N` and inspect dmesg for #AC/#DB policy. Trigger user split locks to verify warning, SIGBUS, or rate limiting. Exercise KVM guest split-lock handling via `handle_guest_split_lock()`. Toggle `/proc/sys/kernel/split_lock_mitigate` and hotplug CPUs while delayed re-enable work is pending.
