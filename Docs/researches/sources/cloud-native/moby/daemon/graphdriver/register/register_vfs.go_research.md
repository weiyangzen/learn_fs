# sources/cloud-native/moby/daemon/graphdriver/register/register_vfs.go

Purpose: blank-import registration hook for the VFS graphdriver.

Important APIs and control flow: imports `github.com/moby/moby/v2/daemon/graphdriver/vfs` for side effects, causing its `init` to register `"vfs"` on all supported builds.

State, dependencies, and risks: no direct state. VFS is the portable fallback driver in Linux priority and is useful in test or unsupported filesystem environments. Registration is unconditional in this file; runtime behavior still depends on VFS init and quota options. Build coverage is the signal.
