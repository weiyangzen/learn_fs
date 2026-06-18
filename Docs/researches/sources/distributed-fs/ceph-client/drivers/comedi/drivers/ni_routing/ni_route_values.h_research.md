# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_route_values.h

## Purpose
This header defines the common storage format and marking scheme for NI route register values. It is the contract between generated family data, the conversion tools, and the runtime route lookup implementation.

## Important APIs, Types, And Data
`struct family_route_values` contains `const char *family` and `register_values[NI_NUM_NAMES][NI_NUM_NAMES]`, indexed by destination then source after applying `B(x) ((x) - NI_NAMES_BASE)`. `V(x)` marks a register value valid, implemented, and tested. `I(x)` means implemented but needing testing in external conversion mode, but collapses to `V(x)` for kernel builds. `U(x)` means not implemented and becomes zero in kernel builds. `UNMARK(x)` strips marker bits. `Gi_SRC(val, subsel)` packs M-series counter source subselect data. The header declares `extern const struct family_route_values *const ni_all_route_values[]`.

## Control Flow
The header has no runtime flow, but its macros directly shape route lookup. Kernel consumers only see `u8 register_type`, so unimplemented `U()` entries compile to zero and are ignored. Conversion tooling defines `NI_ROUTE_VALUE_EXTERNAL_CONVERSION`, widening `register_type` to `u16` and preserving `V/I/U` markers for CSV regeneration.

## State And Persistence
The header defines immutable table shape, not mutable state. Its marker definitions affect which source entries persist into compiled kernel route availability versus external maintenance artifacts.

## Dependencies And Integration Points
It includes `<linux/comedi.h>` for NI signal constants and `NI_NUM_NAMES`, and `<linux/types.h>` for fixed-width types. `ni_routes.c` relies on `B()` and the flattened `register_values` layout. `convert_c_to_py.c` relies on external conversion mode marker macros to recover maintenance status.

## Risks
The include guard name contains `ROUTINT`, a typo that is stable but easy to copy incorrectly. Marker semantics are subtle: in kernel mode `I()` becomes valid and `U()` disappears, while external tooling preserves both. Any route value above seven bits must be handled carefully because `V()` and `UNMARK()` mask with `0x7f`; packed `Gi_SRC()` values rely on that seven-bit payload budget.

## Test Signals
Route tests should verify `UNMARK()` values are what hardware programming expects. Tool tests should compile `convert_c_to_py.c` with `NI_ROUTE_VALUE_EXTERNAL_CONVERSION` and confirm `MARKED_V/I/U` survive. Static checks should ensure all indexed signal constants are within `NI_NUM_NAMES`.
