# sources/cloud-native/cri-o/pkg/config/config_unsupported.go

This build-tagged file supports platforms that are not Linux, FreeBSD, or Windows. It provides placeholder constants and minimal stubs so the package can compile on unsupported targets, while intentionally making runtime defaults invalid.

Important symbols are invalid-valued defaults for runtime name/type/root, monitor cgroup, and `ImageVolumesBind`, plus `DefaultPauseImage`. It also defines `selinuxEnabled` as false, `checkKernelRROMountSupport` as `errdefs.ErrNotImplemented`, and `(*RuntimeConfig).ValidatePinnsPath` as a no-op. There is no state persistence; the behavior is compile-time platform selection.

Dependencies are only `utils/errdefs`. Integration is with generic config code that expects these functions and constants to exist on every platform. The risk is deliberate: tests and real runtime behavior are not expected to pass because defaults are placeholders. This file should be treated as portability scaffolding, not as a supported runtime implementation.
