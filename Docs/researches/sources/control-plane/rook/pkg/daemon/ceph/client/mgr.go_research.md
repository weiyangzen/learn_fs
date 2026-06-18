# sources/control-plane/rook/pkg/daemon/ceph/client/mgr.go

Purpose: wraps Ceph manager module status, module enable/disable, balancer configuration, and minimum client compatibility commands.

Important APIs: `CephMgrMap()` and `CephMgrStat()` parse `mgr dump` and `mgr stat` into types defined elsewhere in the package. `MgrEnableModule()`, `MgrDisableModule()`, `ConfigureBalancerModule()`, and helper functions `enableModule()`, `enableDisableBalancerModule()`, `setBalancerMode()`, `setMinCompatClient()`, `mgrSetBalancerMode()`, and `desiredMinCompatClientVersion()` implement module changes. Constants define read/upmap-read balancer modes and a mutable retry wait duration.

Control flow and state: `MgrEnableModule()` retries up to five times, skips enabling `balancer` because Ceph treats it differently, and sleeps `moduleEnableWaitTime` between failures. `MgrDisableModule()` maps balancer to `ceph balancer off`; other modules use `mgr module disable`. `ConfigureBalancerModule()` chooses a min compat client version, sets it, then sets balancer mode with retries. `desiredMinCompatClientVersion()` requires Ceph v19+ for `read` and `upmap-read`, returning `reef`; other modes use `luminous`.

Dependencies and integration: depends on Ceph version comparison, shared command execution, and manager map/stat structs from other package files. Risks include mutable package retry duration in tests, version-gate correctness as Ceph evolves, enabling/disabling modules without first checking current state, and the error text in `enableModule()` always saying "enable" even for disable. Tests cover retry behavior, module command construction, balancer on/off, mode setting, and version gating.
