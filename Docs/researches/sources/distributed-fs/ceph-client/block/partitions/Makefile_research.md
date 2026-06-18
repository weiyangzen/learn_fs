<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/Makefile -->
# sources/distributed-fs/ceph-client/block/partitions/Makefile

## Purpose
`partitions/Makefile` maps partition parser Kconfig symbols to object files in the kernel build.

## Important APIs, Types, and Functions
There are no functions. The key entries build `core.o` whenever `CONFIG_BLOCK` is enabled and conditionally include parser objects such as `acorn.o`, `amiga.o`, `atari.o`, `aix.o`, `cmdline.o`, `mac.o`, `ldm.o`, `msdos.o`, `of.o`, `osf.o`, `sgi.o`, `sun.o`, `ultrix.o`, `ibm.o`, `efi.o`, `karma.o`, and `sysv68.o`.

## Control Flow
Kbuild expands `obj-$(CONFIG_...)` entries into built-in objects for enabled symbols. The resulting compiled objects must define the parser functions referenced under matching `#ifdef`s in `core.c`.

## State and Persistence Behavior
The file has no runtime state. It controls static kernel contents and therefore the set of partition formats recognized by the built kernel.

## Dependencies and Integration Points
It depends on symbol names from `Kconfig` and source filenames in the same directory. It also depends on `core.o` always being present for partition management when block support is compiled.

## Risks and Edge Cases
Kconfig/Makefile/core mismatches produce link errors or dead code. Removing an object without updating parser declarations can break builds for specific configs. Parser order is not defined here, so adding an object also requires updating `core.c` if it participates in probing.

## Test Signals
Build all partition-related config combinations, especially individual parser enablement, `CONFIG_BLOCK=n`, and allmodconfig/allyesconfig link checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/Makefile -->
