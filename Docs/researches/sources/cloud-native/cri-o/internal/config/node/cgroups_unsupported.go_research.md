# sources/cloud-native/cri-o/internal/config/node/cgroups_unsupported.go

Purpose: provides non-Linux stubs for cgroup detection functions.

Important APIs/types/functions: `CgroupIsV2`, `CgroupHasMemorySwap`, `CgroupHasHugetlb`, and `CgroupHasPid` all return false.

Control flow: no host probing is performed.

State and persistence behavior: no state and no filesystem access.

Dependencies/integration points: selected by `!linux` builds to preserve shared call sites in config validation and container resource generation.

Risks: non-Linux callers that rely on positive cgroup capabilities will never see them, so Linux-only resource behavior is disabled.

Test signals: no direct tests; stub behavior is trivial.
