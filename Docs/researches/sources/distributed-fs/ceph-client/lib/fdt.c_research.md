# sources/distributed-fs/ceph-client/lib/fdt.c

## Purpose
This file is a kernel build wrapper for the common libfdt core implementation. It includes `linux/libfdt_env.h` and then compiles `../scripts/dtc/libfdt/fdt.c` into the kernel tree with the kernel environment definitions.

## Important APIs, Types, and Functions
The wrapper itself declares no functions. The included implementation provides core flattened device tree routines such as `fdt_ro_probe_()`, `fdt_header_size()`, `fdt_check_header()`, `fdt_next_tag()`, `fdt_check_node_offset_()`, `fdt_check_prop_offset_()`, `fdt_next_node()`, `fdt_first_subnode()`, `fdt_next_subnode()`, and `fdt_move()`.

## Control Flow
Compilation substitutes the kernel libfdt environment before including the shared source. At runtime the included routines validate FDT headers, walk structure-block tags, iterate nodes/subnodes, validate offsets, and move an FDT blob into another buffer when size permits.

## State and Persistence
There is no wrapper-owned state. The included libfdt functions operate on caller-provided FDT memory buffers and may copy data in `fdt_move()`.

## Dependencies and Integration Points
Depends on the in-tree `scripts/dtc/libfdt` source and `linux/libfdt_env.h`. It integrates boot, architecture, and device-tree code that uses libfdt APIs from kernel C code while sharing implementation with dtc tooling.

## Risks
Because this is an include wrapper, changes in the shared dtc libfdt file directly affect kernel behavior. Environment mismatches between userspace libfdt assumptions and kernel `libfdt_env.h` can cause build or ABI issues. Header and structure validation are security-sensitive because FDT blobs may be firmware supplied.

## Test Signals
FDT boot tests, malformed-header tests, node iteration tests, and `fdt_move()` buffer-size tests are relevant. Build coverage should ensure the wrapper continues compiling after shared libfdt updates.
