# sources/distributed-fs/glusterfs/xlators/mount/fuse/utils/Makefile.am

## Purpose
Selects the installed FUSE mount helper script for the target platform.

## APIs, Types, and Functions
The automake variables are `utildir = @mountutildir@`, `util_SCRIPTS`, and `CLEANFILES`. Under `GF_LINUX_HOST_OS`, `util_SCRIPTS` installs `mount.glusterfs`; otherwise it installs `mount_glusterfs`.

## Control Flow, State, and Persistence
There is no runtime control flow. During configure/build, automake expands the conditional and installs exactly one helper into the configured mount utility directory. `CLEANFILES` is empty here.

## Dependencies and Integration
Depends on configure-time substitution of `@mountutildir@` and the `GF_LINUX_HOST_OS` automake conditional. It integrates with system mount helper discovery, where Linux expects `mount.glusterfs` and non-Linux platforms use the underscore variant.

## Risks and Test Signals
Risks include installing the wrong helper if host OS detection is wrong, or missing generated helper substitutions if packaging rules do not process the `.in` templates. Test signals are `make install` output on Linux and BSD/Darwin targets, package file lists containing the expected helper name, and mount invocations resolving the installed script.
