# sources/distributed-fs/ceph-client/fs/zonefs/Makefile

## Purpose
`fs/zonefs/Makefile` describes how the zonefs filesystem object is built.

## Important APIs, types, and functions
It adds `-I$(src)` to `ccflags-y`, builds `zonefs.o` when `CONFIG_ZONEFS_FS` is enabled, and links `super.o`, `file.o`, and `sysfs.o` into the composite object.

## Control flow
The local include path lets generated trace include directives find `trace.h`. The composite object ties mount/superblock logic, file operations, and sysfs support into one filesystem module or built-in object.

## State and persistence
No runtime state exists in the makefile.

## Dependencies and integration points
It connects the Kconfig option to the kbuild system and supports the tracepoint include layout used by `super.c`.

## Risks and test signals
Risks include omitting a new source file from `zonefs-y` or breaking trace header include resolution. Test signals are clean module and built-in builds with tracing enabled.
