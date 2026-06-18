# sources/cloud-native/moby/daemon/graphdriver/overlayutils/userxattr.go

Purpose: detects whether rootless overlayfs mounts need the `userxattr` option.

Important APIs and control flow: `NeedsUserXAttr` returns false outside a user namespace. Inside a user namespace it fast-paths to true for kernel >=5.11, because upstream rootless overlayfs uses `user.overlay.*` xattrs. For older kernels, it creates a temporary overlay mount with `userxattr`; if mounting fails, it assumes an Ubuntu/Debian-style backport that does not need the option and returns false; if mounting succeeds, it unmounts and returns true.

State, dependencies, and risks: state is a temporary `userxattr-check` directory under the driver home. Dependencies include kernel version parsing, user namespace detection, containerd mount helpers, and overlay mount behavior. Risks include distro backports making version checks imperfect, mount permission failures being interpreted as no userxattr needed, and cleanup/unmount warnings. It directly influences overlay2 native-diff checks and mount options.
