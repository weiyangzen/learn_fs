# sources/distributed-fs/ceph-client/lib/fdt_wip.c

## Purpose
Kernel wrapper for shared libfdt in-place/work-in-progress mutation helpers. It includes the kernel environment and compiles `../scripts/dtc/libfdt/fdt_wip.c`.

## Important APIs, Types, and Functions
The included implementation provides `fdt_setprop_inplace_namelen_partial()`, `fdt_setprop_inplace()`, `fdt_nop_property()`, `fdt_node_end_offset_()`, and `fdt_nop_node()`. Internal `fdt_nop_region_()` marks structure-block regions as NOP tags.

## Control Flow
In-place property updates locate an existing property and copy bytes into its current value without resizing. NOP operations find the property or node extent and replace the corresponding structure-block region with NOP tags so later pack operations can reclaim space.

## State and Persistence
No wrapper-owned state exists. The caller's mutable FDT buffer is changed in place.

## Dependencies and Integration Points
Depends on core and read-only libfdt helpers for locating nodes/properties and on kernel environment definitions. It integrates with code needing limited mutation of an already laid-out FDT without reallocating or changing block sizes.

## Risks
In-place setters cannot grow properties; callers must supply matching offsets and lengths. NOPing the wrong region can remove required tree data until repacked or rebuilt. Shared-source updates affect kernel behavior directly.

## Test Signals
Test partial/full in-place property replacement, overlength rejection, NOPing properties and nodes, subsequent read-only lookup behavior, and packing after NOP operations.
