# sources/distributed-fs/ceph-client/security/apparmor/path.c

Purpose: resolves VFS paths into AppArmor mediation names while handling chroot-relative lookup, disconnected paths, deleted dentries, internal mounts, directory suffixes, and audit diagnostics.

Important functions: `prepend()` safely prepends text into the backwards path buffer. `disconnect()` handles paths not connected to the expected root and optional disconnected prefixes. `d_namespace_path()` performs the main lookup using `dentry_path()`, `__d_path()`, `d_absolute_path()`, or `dentry_path_raw()`. `aa_path_name()` wraps lookup and maps errors to human-readable info.

Control flow: callers provide a buffer sized by `aa_g_path_max` and path flags. Internal mounts use dentry paths and special-case proc sysctl paths. Chroot-relative lookup uses current fs root; otherwise absolute path lookup is used. Disconnected paths may be denied or prefixed depending on policy flags. Directories get a trailing slash except root.

State and persistence: no persistent state; consumes global `aa_g_path_max`, current fs root, mount namespace membership, and profile path flags.

Dependencies and integration: used by file, mount, link/rename, and audit mediation. Risks include off-by-one buffer handling, name-too-long behavior, deleted dentry mediation flags, chroot escape/connect semantics, and internal proc/sys rewriting. Test deleted files, disconnected bind mounts, chroot-relative paths, directories, root, long paths, internal proc/sys paths, and `PATH_CONNECT_PATH`/`PATH_CHROOT_NSCONNECT` combinations.
