# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2.h

## Purpose
This small public header declares the ATL2 hardware capability records and operations table. It is the include point used by PCI/device-selection code to bind supported A2 family devices to the ATL2 implementation.

## Important APIs, types, and functions
It includes `aq_common.h` and declares four external symbols: `hw_atl2_caps_aqc113`, `hw_atl2_caps_aqc115c`, `hw_atl2_caps_aqc116c`, and `hw_atl2_ops`. The capability symbols identify per-board limits and link masks, while `hw_atl2_ops` is the function-pointer table used by the Atlantic core hardware abstraction.

## Control flow
This file has no executable control flow. Its declarations let another translation unit select the correct `aq_hw_caps_s` and `aq_hw_ops` during device match/probe. The actual initialization, reset, rings, interrupts, filters, and firmware interactions live in `hw_atl2.c` and the ATL2 utility files.

## State and persistence
The header owns no state. It exposes immutable capability/ops objects defined elsewhere.

## Dependencies and integration points
The dependency on `aq_common.h` supplies declarations for `struct aq_hw_caps_s` and `struct aq_hw_ops`. Integration is outward-facing: PCI ID tables and core Atlantic setup code can include this header without including internal register maps.

## Risks
The main risk is declaration drift. If `hw_atl2.c` changes symbol names or capability coverage without updating this header, device binding will fail at build or link time. Because the header hides all internals, callers cannot validate feature assumptions from here alone.

## Test signals
Build coverage is the primary signal. A successful driver build with ATL2 enabled verifies that all externs resolve, and probe logs on AQC113/AQC115C/AQC116C confirm that the declared caps and ops are reachable.
