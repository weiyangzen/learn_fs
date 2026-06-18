# sources/distributed-fs/ceph-client/lib/fdt_addresses.c

## Purpose
Kernel wrapper for shared libfdt address/size-cell helpers. It includes `linux/libfdt_env.h` and compiles `../scripts/dtc/libfdt/fdt_addresses.c`.

## Important APIs, Types, and Functions
The wrapper itself has no local declarations. The included code provides `fdt_address_cells()`, `fdt_size_cells()`, and `fdt_appendprop_addrrange()`, with an internal `fdt_cells()` helper for reading `#address-cells` and `#size-cells`.

## Control Flow
Calls read cell-count properties from nodes, apply libfdt validation and default/error rules, and append encoded address/size ranges to a property using the writable libfdt property machinery.

## State and Persistence
No persistent state is owned by the wrapper. The included functions read or mutate caller-provided FDT blobs when appending address ranges.

## Dependencies and Integration Points
Depends on libfdt core/read-write helpers and kernel endian/cell definitions from `linux/libfdt_env.h`. It is used by architecture and firmware code that interprets or constructs `reg`-style properties.

## Risks
Wrong cell-count interpretation can corrupt address range encoding. `fdt_appendprop_addrrange()` depends on sufficient FDT buffer space and valid parent/node offsets. Shared-source updates propagate through this wrapper.

## Test Signals
Test default and explicit cell counts, invalid cell properties, 32-bit and 64-bit address/size ranges, no-space errors, and integration with consumers parsing generated `reg` properties.
