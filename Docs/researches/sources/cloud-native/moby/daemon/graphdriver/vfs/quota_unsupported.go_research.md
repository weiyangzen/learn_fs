# sources/cloud-native/moby/daemon/graphdriver/vfs/quota_unsupported.go

Purpose: non-Linux quota adapter for VFS that reports quota unsupported.

Important APIs and control flow: `driverQuota` is empty. `setupDriverQuota` is a no-op, `setQuotaOpt` and `setupQuota` return `quota.ErrQuotaNotSupported`, `getQuotaOpt` returns zero, and `quotaSupported` returns false.

State, dependencies, and risks: no state. It ensures VFS builds on non-Linux without quota primitives while giving callers deterministic unsupported errors for size options. A minor integration oddity is the no-op `setupDriverQuota` signature differs from the Linux helper but callers ignore its return value. Build and driver option tests provide the signal.
