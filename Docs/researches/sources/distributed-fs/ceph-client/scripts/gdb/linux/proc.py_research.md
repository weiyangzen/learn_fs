# sources/distributed-fs/ceph-client/scripts/gdb/linux/proc.py

## Purpose
`proc.py` implements GDB equivalents of selected `/proc` views: command line, version, I/O resources, mounts, and FDT dumping.

## Important APIs, Types, and Functions
Commands include `lx-cmdline`, `lx-version`, `lx-iomem`, `lx-ioports`, `lx-mounts`, and `lx-fdtdump`. Helpers include `get_resources()` for resource trees, `show_lx_resources()`, `info_opts()`, and `LxFdtDump.fdthdr_to_cpu()`.

## Control Flow
Resource commands recursively walk child/sibling `struct resource` trees. `lx-mounts` finds a task by PID, reads its mount namespace, walks the namespace RB tree, reconstructs mount paths through VFS helpers, and formats flags. `lx-fdtdump` reads `initial_boot_params`, validates the FDT magic, dumps the blob to a local file, and reports header fields.

## State and Persistence Behavior
Most commands are read-only. `lx-fdtdump` writes a host-side DTB file; default name is `fdtdump.dtb`. No kernel state is modified.

## Dependencies and Integration Points
It depends on constants, task iteration, list/RB tree helpers, VFS name helpers, and target endianness utilities.

## Risks and Test Signals
Mount path reconstruction cannot call filesystem callbacks and may omit escaping or special proc formatting. FDT dump file creation is host-side and can overwrite the default file. Test against `/proc/cmdline`, `/proc/version`, `/proc/iomem`, `/proc/ioports`, `/proc/mounts`, and a valid `dtc` parse of the dumped DTB.
