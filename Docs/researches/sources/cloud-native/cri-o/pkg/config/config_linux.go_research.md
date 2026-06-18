# sources/cloud-native/cri-o/pkg/config/config_linux.go

Purpose: Linux-specific CRI-O config defaults and validation helpers for SELinux, `pinns`, and recursive read-only mount kernel support.

Important APIs/types/functions: constants for default runtime `crun`, runtime type/root, default monitor cgroup `system.slice`, bind image volume type, and pause image. Functions `selinuxEnabled`, `RuntimeConfig.ValidatePinnsPath`, `checkKernelRROMountSupport`, `validateKernelRROVersion`, and `validateKernelRROMount`; package vars cache RRO support through `sync.Once`.

Control flow: SELinux queries the host library. `ValidatePinnsPath` resolves or stats the executable via shared `validateExecutablePath`. RRO support first checks kernel version >= 5.12; if too old, it performs a live tmpfs mount and `unix.MountSetattr(... AT_RECURSIVE, MOUNT_ATTR_RDONLY)` probe to detect backported support, caching the result.

State and persistence: RRO validation creates a temporary directory, mounts tmpfs, unmounts it, and removes the directory; result is cached in package globals. `ValidatePinnsPath` mutates `RuntimeConfig.PinnsPath`.

Dependencies/integration: used by `config.go` runtime validation and runtime feature gating. Depends on opencontainers SELinux, containers/storage kernel parser, `x/sys/unix`, and logrus.

Risks: the live mount probe requires privileges/capabilities and can fail for environmental reasons unrelated to kernel capability. `sync.Once` means the first result persists for process lifetime, even if test environment or privileges change. Cleanup logs but cannot recover failed unmount/removal. `pinns` validation is execution-path dependent.

Test signals: best covered with unit tests for version comparison using fakes and integration tests for mount probing under privileged Linux; normal unprivileged tests may need to avoid the live probe.
