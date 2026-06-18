# sources/cloud-native/containers-storage/pkg/system/mknod_windows.go

Purpose: Windows stub for Unix `mknod` functionality.

Important APIs/types/functions: `Mknod` returns `ErrNotSupportedPlatform`; `Mkdev` panics because Windows has no compatible device-node encoding in this package.

Control flow: no syscall is attempted. `Mkdev` is deliberately fail-fast if a caller reaches it on Windows.

State/persistence: none.

Dependencies/integration: protects cross-platform callers from compiling Unix-only node creation on Windows.

Risks: `Mkdev` panics rather than returning an error, so callers must guard platform-specific device handling. `Mknod` signature differs from FreeBSD/default variants in the type of `dev`, which is safe by build tag but relevant to cross-platform code.

Test signals: Windows tests should assert unsupported errors for device creation and avoid executing `Mkdev` except in panic-specific tests.
