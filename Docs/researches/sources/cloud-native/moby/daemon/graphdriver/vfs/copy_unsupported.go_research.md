# sources/cloud-native/moby/daemon/graphdriver/vfs/copy_unsupported.go

Purpose: non-Linux VFS directory-copy implementation binding.

Important APIs and control flow: under build tag `!linux`, `dirCopy` uses `chrootarchive.NewArchiver(user.IdentityMapping{}).CopyWithTar(srcDir, dstDir)`, copying parent layer contents through tar rather than Linux-specific filesystem walking.

State, dependencies, and risks: no direct state. Dependencies are chrootarchive and an empty identity mapping. The tar copy path is more portable but may not preserve every platform-specific metadata detail the Linux copy helper handles. It is used whenever VFS creates a child layer on non-Linux platforms. Test signal is cross-platform VFS behavior/builds.
