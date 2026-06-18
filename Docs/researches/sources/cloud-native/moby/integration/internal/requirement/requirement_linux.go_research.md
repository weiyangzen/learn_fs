# sources/cloud-native/moby/integration/internal/requirement/requirement_linux.go

Purpose: Linux-specific requirement helpers for cgroup namespaces and overlayfs/overlay2 support.

Important APIs and helpers: `CgroupNamespacesEnabled`, `overlayFSSupported`, and `Overlay2Supported`.

Control flow: `CgroupNamespacesEnabled` checks for `/proc/self/ns/cgroup`. `overlayFSSupported` runs `modprobe overlay` and treats success as support. `Overlay2Supported` parses a kernel version and returns true for kernels newer than or equal to 4.0, or RHEL/CentOS 3.10 kernels with the supported patch level.

State and persistence: reads procfs and may load the overlay kernel module through `modprobe`, changing kernel module state.

Dependencies and integration: depends on `os.Stat`, `exec.Command`, and kernel version comparison helpers from Moby daemon graphdriver overlay2 package.

Risks: `modprobe overlay` may require privileges and can have side effects. Kernel-version logic encodes distribution-specific compatibility assumptions.

Test signals: helper-only; used to skip or gate tests requiring cgroup namespaces or overlay2.
