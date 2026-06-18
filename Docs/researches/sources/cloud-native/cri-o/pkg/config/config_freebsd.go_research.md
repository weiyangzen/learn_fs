# sources/cloud-native/cri-o/pkg/config/config_freebsd.go

Purpose: FreeBSD-specific CRI-O config defaults and platform stubs.

Important APIs/types/functions: constants for CNI paths, socket/config/version/clean-shutdown paths, default runtime `ocijail`, runtime root/type, monitor cgroup, `ImageVolumesBind = "nullfs"`, and FreeBSD pause image. Functions `selinuxEnabled`, `checkKernelRROMountSupport`, and `RuntimeConfig.ValidatePinnsPath`.

Control flow: SELinux always returns false; RRO support returns not implemented; `ValidatePinnsPath` is a no-op.

State and persistence: supplies path defaults used by `DefaultConfig` and runtime validation on FreeBSD. No mutable state.

Dependencies/integration: imports CRI-O `errdefs` for not-implemented RRO. Complements `config_linux.go` under build selection.

Risks: feature support intentionally differs from Linux: no SELinux, no pinns validation, no RRO support. FreeBSD-specific pause image and paths must be maintained separately from Linux defaults.

Test signals: compile/test on FreeBSD should confirm defaults and no-op validation; Linux-only RRO/pinns tests should not assume these functions behave the same.
