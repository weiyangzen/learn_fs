# sources/distributed-fs/openafs/src/platform/SOLARIS/Makefile.in

## Purpose
Builds and stages the Solaris `fs_conv_sol26` utility, which converts AFS partition inode metadata between pre-SunOS 5.6 and SunOS 5.6-compatible formats.

## Important APIs, Types, And Functions
Important variables are `INCLS` and `LIBS`, covering AFS interfaces, command parsing, inode, sys, dir, LWP, and ACL libraries. Targets include `all`, `fs_conv_sol26`, `install`, `dest`, and `clean`. The executable depends on `fs_conv_sol26.o`, OpenAFS command/sys/dir libraries, roken, and component version generation.

## Control Flow
`all` builds `fs_conv_sol26`. The link rule invokes `$(AFS_LDRULE)` with `fs_conv_sol26.o`, `libcmd`, roken, other OpenAFS libraries, and `${XLIBS}`. `install` places the binary under `${afssrvsbindir}`; `dest` stages it under `root.server/usr/afs/bin`.

## State And Persistence
Build artifacts include `fs_conv_sol26.o`, `AFS_component_version_number.c`, and the executable. Install/dest targets persist a server administration binary.

## Dependencies And Integration Points
Depends on Solaris UFS/inode headers consumed by the C source and OpenAFS server tooling paths. It integrates a one-off filesystem migration utility into server install images.

## Risks And Test Signals
Risks include obsolete Solaris UFS layout assumptions, library-order sensitivity, and installing a destructive disk utility. Test signals are successful Solaris build, correct destination path, and controlled dry-run/force behavior in the tool.
