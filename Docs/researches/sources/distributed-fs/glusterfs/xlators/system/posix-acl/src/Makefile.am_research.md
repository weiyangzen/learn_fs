# sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/Makefile.am

Purpose: automake build recipe for the GlusterFS POSIX ACL translator shared module.

Important APIs, types, and functions: declares `xlator_LTLIBRARIES = posix-acl.la`, installs it under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/system`, builds from `posix-acl.c` and `posix-acl-xattr.c`, links against `libglusterfs.la`, and lists the internal headers. `AM_CPPFLAGS`, `AM_CFLAGS`, and `AM_LDFLAGS` supply Gluster include and linker paths. The `access-control-compat` target creates a compatibility symlink from `xlator/features/access-control.so` to `../system/posix-acl.so`.

Control flow: normal build compiles the two C files into a module. `install-exec-local` runs `access-control-compat`; `uninstall-local` removes the compatibility symlink.

State and persistence: no runtime state, but install/uninstall mutate the target filesystem by creating/removing the legacy feature-path symlink.

Dependencies and integration points: depends on GlusterFS autotools variables, libtool module flags, libglusterfs, generated RPC XDR include paths, and the historical `features/access-control.so` module name expected by older configurations.

Risks and test signals: the compatibility symlink is path-sensitive and uses `rm -rf` on the target symlink path, so install tests should verify it resolves correctly under staged `DESTDIR`. Build tests should confirm module name, exported xlator API, and uninstall cleanup.
