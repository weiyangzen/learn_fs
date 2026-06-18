# sources/cloud-native/moby/daemon/graphdriver/vfs/copy_linux.go

Purpose: Linux VFS driver directory-copy implementation binding.

Important APIs and control flow: `dirCopy` delegates to `copy.DirCopy(srcDir, dstDir, copy.Content, false)`, using the graphdriver copy helper in content-copy mode and not copying overlay opaque xattrs.

State, dependencies, and risks: no direct state. The VFS driver depends on this when creating a child layer from a parent, so layer creation performs a full recursive copy while preserving Linux metadata handled by `copy.DirCopy`. Risks inherit from the copy helper: expensive full copies, filesystem metadata/xattr differences, and special-file handling limitations in user namespaces. Tests are indirect through VFS create/snapshot tests and copy helper tests.
