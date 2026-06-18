# sources/distributed-fs/ceph-client/lib/fdt_sw.c

## Purpose
Kernel wrapper for shared libfdt sequential-write creation routines. It includes the kernel libfdt environment and compiles `../scripts/dtc/libfdt/fdt_sw.c`.

## Important APIs, Types, and Functions
The included implementation provides `fdt_create_with_flags()`, `fdt_create()`, `fdt_resize()`, `fdt_add_reservemap_entry()`, `fdt_finish_reservemap()`, `fdt_begin_node()`, `fdt_end_node()`, `fdt_property_placeholder()`, `fdt_property()`, and `fdt_finish()`. Internal helpers probe current construction state and manage strings.

## Control Flow
Callers create a sequential-write FDT buffer, optionally add reserve-map entries, finish the reserve map, begin/end nodes, add properties, and finish the blob. The implementation enforces construction state ordering and writes structure/string blocks incrementally.

## State and Persistence
No wrapper-owned state exists. Construction state is encoded in the caller's FDT buffer/header while the tree is being built.

## Dependencies and Integration Points
Depends on libfdt environment definitions and shared libfdt internals. It integrates with architecture/boot code that synthesizes FDT blobs without starting from an existing complete tree.

## Risks
APIs are stateful by buffer contents: calling functions out of order returns bad-state errors or can leave an incomplete blob. Buffer size and alignment are critical. Shared-source updates can change construction behavior across kernel users.

## Test Signals
Create valid trees from scratch, attempt out-of-order operations, test reservation-map sequencing, no-space property insertion, string reuse, resize behavior, and final validation with `fdt_check_header()` plus read-only traversal.
