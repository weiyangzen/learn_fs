# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-mmsys.h

## Purpose
This shared private header defines common MMSYS route constants, the `MMSYS_ROUTE` helper, `struct mtk_mmsys_routes`, `struct mtk_mmsys_driver_data`, and the default routing table used by older SoCs.

## Important APIs, Types, and Functions
`MMSYS_ROUTE()` is the most important macro: it fills route records while compile-time checking that masks are nonzero and selection values fit masks. `struct mtk_mmsys_driver_data` carries clock driver names, route arrays, reset offsets/tables, VPPSYS marker, and mixer vsync length. `mmsys_default_routing_table[]` describes legacy BLS/OVL/COLOR/RDMA/GAMMA/OD/UFOE routes.

## Control Flow and State
There is no executable control flow. The data here drives runtime route iteration, reset registration, and clock/DRM child device creation in `mtk-mmsys.c`.

## Dependencies and Integration Points
The header depends on DDP component IDs and bit macros. It is included by all per-SoC MMSYS route headers and the core driver, making it the local contract for route data shape.

## Risks and Test Signals
The compile-time route checks reduce mask/value mistakes, but default route reuse for incomplete SoC route information is explicitly provisional. Test signals include build-time validation failures, legacy display path tests on MT2701/MT2712-like SoCs, and route-specific register traces.
