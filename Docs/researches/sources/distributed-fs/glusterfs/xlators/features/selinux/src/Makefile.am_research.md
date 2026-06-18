# sources/distributed-fs/glusterfs/xlators/features/selinux/src/Makefile.am

## Purpose
This Automake file builds the SELinux feature translator module.

## Important APIs and build outputs
When `WITH_SERVER` is enabled, it builds `selinux.la` as an xlator module installed under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features`. The module source is `selinux.c`; private headers are `selinux.h`, `selinux-messages.h`, and `selinux-mem-types.h`. It links against `libglusterfs.la` and uses default xlator module flags.

## Dependencies and integration
`AM_CPPFLAGS` adds libglusterfs and RPC XDR include paths from both source and build trees. `AM_CFLAGS` enables `-Wall` plus project C flags. The conditional `WITH_SERVER` means packaging or client-only builds may omit the module.

## Risks and test signals
Because this file names only `selinux.c`, any new implementation file must be added here or it will not compile into the module. Build tests should cover both `WITH_SERVER` true and false, confirm the module install path, and verify the listed noinst headers are included in distribution/build dependencies as intended.
