# sources/cloud-native/cri-o/pkg/config/config_windows.go

This Windows-specific file defines CRI-O default paths for CNI, runtime exits, attach sockets, config files, and sockets using Windows path syntax, and stubs recursive read-only mount support as not implemented.

The important exported/default constants include `ContainerAttachSocketDir`, `CrioConfigPath`, `CrioConfigDropInPath`, and `CrioSocketPath`. The control flow is minimal: `checkKernelRROMountSupport` returns `errdefs.ErrNotImplemented`. Persistence behavior is path-based, mapping CRI-O config and runtime files under `C:\crio\...`.

Dependencies are limited to `utils/errdefs`. Integration is with `DefaultConfig` and validation on Windows builds. A notable risk is that this file declares `CrioConfigPath` twice in the same const block, once for `C:\crio\etc\crio.conf` and once where the comment describes a version file. That would be a compile-time redeclaration problem if this Windows file is built, and it likely intended a distinct version-path constant. Tests in this subset do not exercise Windows builds, so this risk is not covered here.
