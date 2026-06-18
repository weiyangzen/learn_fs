# sources/distributed-fs/ceph-client/fs/sysfs/Makefile

## Purpose
This Makefile defines the object composition of the sysfs virtual filesystem.

## Important APIs, Types, and Functions
`obj-y := file.o dir.o symlink.o mount.o group.o` means sysfs is built into the kernel image when the containing Kconfig selects the directory. It composes sysfs from regular/binary file handling, directory management, symlinks, mount initialization, and attribute groups.

## Control Flow and State
There is no runtime logic. Build ordering is simple and all listed objects are always included when sysfs is compiled.

## Persistence, Dependencies, and Integration
The build depends on kernfs and kobject infrastructure selected by `CONFIG_SYSFS`. The object list mirrors the public sysfs API surface used by driver core and subsystems.

## Risks and Test Signals
Risk is accidental omission of an object when sysfs APIs move. Build tests with `CONFIG_SYSFS=y` should catch undefined references, while allmodconfig/tinyconfig-style jobs catch dependency drift.
