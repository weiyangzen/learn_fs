<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/jiffies.h -->
# sources/distributed-fs/ceph-client/include/vdso/jiffies.h

Purpose: defines vDSO-safe tick duration constants derived from `HZ`.

Important APIs and types: `TICK_NSEC` computes nanoseconds per scheduler tick using `NSEC_PER_SEC` and `HZ`.

Control flow: low-resolution time helpers use `TICK_NSEC` to report clock resolution.

State and persistence: no state; compile-time constant.

Dependencies and integration points: depends on `asm/param.h` for `HZ` and `vdso/time64.h` units. It feeds `vdso/ktime.h`.

Risks and test signals: risks include rounding expectations for unusual `HZ` values. Test low-resolution clock_getres outputs across configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/jiffies.h -->
