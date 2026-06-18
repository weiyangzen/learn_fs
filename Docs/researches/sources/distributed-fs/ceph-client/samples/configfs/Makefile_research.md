<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/configfs/Makefile -->
# sources/distributed-fs/ceph-client/samples/configfs/Makefile

## Purpose
The configfs sample `Makefile` wires the configfs sample kernel module into Kbuild.

## Important APIs, Types, And Functions
It contains one object selection rule: `obj-$(CONFIG_SAMPLE_CONFIGFS) += configfs_sample.o`.

## Control Flow
When `CONFIG_SAMPLE_CONFIGFS` is enabled as built-in or module, Kbuild compiles and links `configfs_sample.o` accordingly.

## State And Persistence
There is no runtime state. Build configuration determines whether the sample module exists.

## Dependencies And Integration Points
It integrates with the kernel samples build system and the `CONFIG_SAMPLE_CONFIGFS` Kconfig symbol.

## Risks And Edge Cases
If the Kconfig symbol is unset, the sample is not built. The Makefile assumes `configfs_sample.c` exists in the same directory.

## Test Signals
Builds with `CONFIG_SAMPLE_CONFIGFS=m` should produce a `configfs_sample` module; built-in configs should include the object in the kernel image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/configfs/Makefile -->
