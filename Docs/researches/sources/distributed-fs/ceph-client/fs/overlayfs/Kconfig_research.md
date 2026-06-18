## sources/distributed-fs/ceph-client/fs/overlayfs/Kconfig

Purpose: this Kconfig file declares overlayfs build support and default feature toggles. It lets kernel builders enable overlayfs itself and choose default behavior for redirect directories, redirect following, inode indexing, NFS export support, xino inode mapping, metadata-only copy-up, and extra debug checks.

Important APIs and options: `OVERLAY_FS` is a tristate that selects `FS_STACK` and `EXPORTFS`. `OVERLAY_FS_REDIRECT_DIR`, `OVERLAY_FS_REDIRECT_ALWAYS_FOLLOW`, `OVERLAY_FS_INDEX`, `OVERLAY_FS_NFS_EXPORT`, `OVERLAY_FS_XINO_AUTO`, `OVERLAY_FS_METACOPY`, and `OVERLAY_FS_DEBUG` control defaults that are later interpreted by overlayfs module parameters and mount options. Dependencies encode important constraints: NFS export requires index and excludes metacopy, xino auto requires 64-bit, and metacopy selects redirect-dir.

Control flow: Kconfig has no runtime flow, but it controls which defaults are compiled into the overlayfs module and which help text warns about backward compatibility. Runtime mount options can still override most default-on features.

State and persistence behavior: the selected options become kernel configuration state. Several options affect persistent on-upper metadata formats such as redirect xattrs, index directory entries, origin xattrs, and metacopy xattrs; help text explicitly warns that these formats are not backward compatible with older kernels.

Dependencies and integration points: integrates with the kernel build system, documentation in `Documentation/filesystems/overlayfs.rst`, and source files in the overlayfs module that check config defaults. `OVERLAY_FS_NFS_EXPORT` depends on the index feature because file handle decoding relies on indexed lower-to-upper relationships.

Risks and test signals: enabling incompatible defaults can create upper layers that older kernels interpret incorrectly. NFS export and metacopy are mutually constrained because lower-handle stability and metadata-only upper files conflict. Build tests should cover all option combinations allowed by dependencies, especially builtin/module/disabled overlayfs, 32-bit builds without xino auto, NFS export dependency enforcement, and debug builds.
