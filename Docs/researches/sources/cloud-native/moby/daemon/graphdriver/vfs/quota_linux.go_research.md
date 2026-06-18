# sources/cloud-native/moby/daemon/graphdriver/vfs/quota_linux.go

Purpose: Linux quota support adapter for the VFS driver.

Important APIs and control flow: `driverQuota` stores a `quota.Control` and desired `quota.Quota`. `setupDriverQuota` attempts `quota.NewControl(driver.home)` and stores it, logging non-not-supported setup errors. `setQuotaOpt`, `getQuotaOpt`, `setupQuota`, and `quotaSupported` manage the configured size and apply quotas to layer directories through `quotaCtl.SetQuota`.

State, dependencies, and risks: state is per-driver quota control and option size. Dependencies include daemon internal quota support and logging. Risks include quota setup silently unavailable when unsupported, later size options returning quota errors, and filesystem-specific quota behavior. `vfs_test.go` uses `DriverTestSetQuota` with quota not required, so unsupported environments skip rather than fail.
