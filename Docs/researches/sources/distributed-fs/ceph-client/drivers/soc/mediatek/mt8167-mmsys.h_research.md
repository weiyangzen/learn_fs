# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8167-mmsys.h

## Purpose
This header supplies MT8167-specific MMSYS display routing register offsets and route table entries. It is consumed by `mtk-mmsys.c` to program display data paths between DDP components.

## Important APIs, Types, and Functions
It defines register offsets for OVL, DITHER, COLOR, DSI, and RDMA selection registers, plus route values such as `MT8167_DITHER_MOUT_EN_RDMA0`. The exported data is `mt8167_mmsys_routing_table[]`, an array of `struct mtk_mmsys_routes` generated with `MMSYS_ROUTE`.

## Control Flow and State
There is no executable control flow. At runtime, `mtk_mmsys_ddp_connect()` and `mtk_mmsys_ddp_disconnect()` iterate this table and write matching register masks/values. The header therefore describes transient hardware mux state, not software-persistent state.

## Dependencies and Integration Points
The table depends on `struct mtk_mmsys_routes`, `MMSYS_ROUTE`, and DDP component identifiers from shared MMSYS/display headers. `mtk-mmsys.c` binds it to the `mediatek,mt8167-mmsys` compatible.

## Risks and Test Signals
Bad route masks or values would silently wire the display pipeline incorrectly. Strong test signals are panel bring-up, DSI output validation, display pipeline mode changes, and register tracing during DDP connect/disconnect.
