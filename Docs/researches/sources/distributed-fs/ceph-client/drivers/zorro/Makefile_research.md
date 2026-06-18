<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/Makefile -->
# sources/distributed-fs/ceph-client/drivers/zorro/Makefile

## Purpose
This Makefile maps Zorro bus configuration to core bus objects, procfs support, optional device names, and the host generator for `devlist.h`.

## Important APIs, types, and functions
It builds `zorro.o`, `zorro-driver.o`, and `zorro-sysfs.o` for `CONFIG_ZORRO`; `proc.o` for `CONFIG_PROC_FS`; `names.o` for `CONFIG_ZORRO_NAMES`; and host program `gen-devlist`.

## Control flow
Kbuild first builds `gen-devlist`, then generates `devlist.h` from `zorro.ids` before compiling `names.o`.

## State and persistence
No runtime state. `devlist.h` is generated build output and cleaned by `make clean`.

## Dependencies and integration points
The file integrates with kbuild host programs, procfs config, Zorro core objects, and generated name tables.

## Risks and test signals
Risks include missing explicit generated-file dependencies and generator/parser failures on malformed `zorro.ids`. Test signals include clean builds, parallel builds, `CONFIG_PROC_FS=n`, and `CONFIG_ZORRO_NAMES=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/Makefile -->
