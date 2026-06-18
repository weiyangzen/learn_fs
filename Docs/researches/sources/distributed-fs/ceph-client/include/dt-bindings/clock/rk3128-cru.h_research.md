# Research: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3128-cru.h

## Purpose
Rockchip CRU clock/reset binding. The file is a C preprocessor device-tree binding header under `include/dt-bindings/clock`; it assigns stable integer IDs that DTS files, board descriptions, and provider drivers share when referring to clock, reset, or power-domain resources. This Rockchip CRU binding exports one namespace for PLLs, special clocks, bus gates, display/media clocks, and software resets. Device trees pass these integers to the Rockchip CRU provider, so clock IDs and `SRST_*` reset IDs are ABI-like constants.

## Important APIs, Types, and Exports
- Exported macro count: 241 across 273 source lines.
- Dominant prefix: `SRST`; prefix distribution: ACLK: 14, ARMCLK: 1, DCLK: 2, HCLK: 26, PCLK: 29, PLL: 6, SCLK: 49, SRST: 114.
- Export categories inferred from names: clock: 127, reset: 114.
- First exported ID: `PLL_APLL=1`; last exported ID: `SRST_VIO_MIPI_DSI=137`.
- Representative exported IDs: `PLL_APLL=1`, `PLL_DPLL=2`, `PLL_CPLL=3`, `PLL_GPLL=4`, `ARMCLK=5`, `...=...`, `SRST_TIMER5=135`, `SRST_VIO_H2P=136`, `SRST_VIO_MIPI_DSI=137`.
- This header defines no C structs, enums, functions, or inline helpers. Its API surface is the macro namespace and the numeric values bound to that namespace.

## Control Flow
There is no executable control flow. Compilation flow is limited to the include guard, optional `#include` dependencies, and macro expansion by the C preprocessor or by the device-tree compiler when DTS files include the header. Runtime behavior happens in the matching clock/reset/power-domain provider driver, which interprets these integer IDs.

## State and Persistence Behavior
The file owns no mutable state, storage, locks, memory allocations, or persistence. The numeric assignments are persistent ABI-like data because compiled DTBs and out-of-tree DTS files may embed these values. Reordering or renumbering existing macros can silently bind a consumer to the wrong clock, reset, or power-domain line.

## Dependencies and Integration Points
- Header dependencies: No local binding includes; only the preprocessor include guard is used.
- Integration points are Linux DTS files using `<dt-bindings/clock/...>` constants, clock provider drivers under the corresponding vendor controller family, reset-controller users when reset IDs are present, and power-domain/GDSC consumers where power-domain IDs appear.
- The source-tree location mirrors upstream kernel binding layout, so include paths are expected to resolve through `include/` during kernel or device-tree builds.

## Risks and Edge Cases
- Numeric drift between this header and the provider driver's descriptor arrays can cause incorrect clock/reset lookup while still compiling cleanly.
- Duplicate values are valid only when the provider intentionally aliases resources; accidental duplicates or gaps should be reviewed against the hardware manual and driver tables.
- Adding a macro without updating YAML bindings, DTS users, or provider tables can leave dead constants; changing an existing value is a compatibility break.
- For shared-include variants, missing or renamed dependencies break DTS preprocessing even if this file's own constants are unchanged.

## Test Signals
- Build signal: `make dtbs` or targeted `dtc` preprocessing succeeds for DTS files that include this header.
- Binding signal: `make dt_binding_check` validates compatible nodes, `#clock-cells`, `#reset-cells`, and provider-specific schema expectations.
- Driver signal: the matching clock/reset provider probes and resolves every referenced ID without out-of-range warnings.
- Static review signal: compare the macro count and max IDs here against the provider arrays and any `clock-names`, reset, or power-domain references in DTS.
