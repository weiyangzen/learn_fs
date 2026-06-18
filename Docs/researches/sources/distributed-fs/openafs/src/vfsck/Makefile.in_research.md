# sources/distributed-fs/openafs/src/vfsck/Makefile.in

## Purpose
This makefile builds and installs the OpenAFS `vfsck` utility, a server-side filesystem checker derived from Berkeley fsck sources and adapted for OpenAFS-supported platforms. It collects the vfsck source modules, applies platform CFLAGS, links the binary, and installs it into server libexec or destination root.server locations.

## Important APIs, Types, And Functions
Important variables are `MODULE_CFLAGS=${VFSCK_CFLAGS}`, `SRCS`, and `OBJS`. The main targets are `all`, `vfsck`, `main.o`, `install`, `dest`, and `clean`. `SRCS` includes pass files (`pass1.c` through `pass5.c` plus `pass1b.c`), setup/utilities, inode/dir helpers, UFS tables/subroutines, and `vprintf.c`. `main.o` depends on generated `AFS_component_version_number.c`.

## Control Flow
The default target builds `vfsck`. The link rule uses `$(AFS_LDRULE)` over all object files plus `$(XLIBS)`. `install` creates `$(DESTDIR)$(afssrvlibexecdir)` and installs `vfsck` there. `dest` installs copies under `${DEST}/root.server/etc/vfsck` and `${DEST}/root.server/usr/afs/bin/vfsck`, and conditionally copies HP-UX boot/check scripts plus mount/umount helpers with executable permissions. `clean` removes objects, the binary, core files, and generated component version source. The file includes `../config/Makefile.version` at the end to generate version metadata.

## State And Persistence
Build state consists of object files, `vfsck`, and `AFS_component_version_number.c`. Install/dest targets persist binaries and HP-UX helper scripts under server installation trees. Clean removes local build artifacts only.

## Dependencies And Integration Points
It includes OpenAFS `Makefile.config` and `Makefile.lwp`, takes platform-specific `VFSCK_CFLAGS`, and links with platform libraries. It integrates with OpenAFS server packaging layout and HP-UX root.server boot/check support.

## Risks And Test Signals
Risks include the age and platform specificity of UFS/fsck code, conditional HP-UX script handling, reliance on `SYS_NAME` patterns, and link portability if `XLIBS` or LWP/config flags drift. Test signals are successful clean builds, generated component version dependency behavior, install and dest layout checks, HP-UX conditional file copies when applicable, and running `vfsck` in controlled filesystem images rather than production partitions.
