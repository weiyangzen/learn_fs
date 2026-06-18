# sources/cloud-native/cri-o/internal/config/node/sysctl_linux.go

Purpose: validates Linux sysctl state needed for CRI-O mount cleanup behavior.

Important APIs/types/functions: package variable `checkFsMayDetachMountsErr`; function `checkFsMayDetachMounts() bool`.

Control flow: reads `/proc/sys/fs/may_detach_mounts` through `os.ReadFile`. On read failure it stores the error and returns false. If the trimmed value is not `"1"`, it records an explanatory error and returns false. Otherwise it returns true.

State and persistence behavior: records the last error in a package global but does not cache with `sync.Once`; each call rereads the procfs value.

Dependencies/integration points: used by `node.ValidateConfig` as a fatal Linux startup validation item.

Risks: hard-fails startup when the sysctl is missing or disabled; this is correct for expected CRI-O mount semantics but may be problematic in constrained or unusual kernels. The global error can be overwritten by repeated calls.

Test signals: no direct tests.
