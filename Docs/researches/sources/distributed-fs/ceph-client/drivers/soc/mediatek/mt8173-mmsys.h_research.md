# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8173-mmsys.h

## Purpose
This header describes MT8173 MMSYS routing for two display paths, including OVL, OD, UFOE, COLOR, AAL, GAMMA, RDMA, DSI, and DPI connections.

## Important APIs, Types, and Functions
The key artifact is `mt8173_mmsys_routing_table[]`. It uses `MMSYS_ROUTE` entries to describe both MOUT/SOUT and SEL_IN registers. Several entries intentionally use a zero selection value for routes where selecting a path means clearing a field.

## Control Flow and State
Runtime control is table-driven in `mtk-mmsys.c`. When a display driver connects a component pair, matching entries cause masked register updates. Disconnecting clears matching masks.

## Dependencies and Integration Points
The table is bound to MT8173 and reused by MT6795 in `mtk-mmsys.c`. It integrates with DRM DDP topology setup and with shared bit helpers such as `BIT()` and `GENMASK()`.

## Risks and Test Signals
The main risk is that shared reuse with MT6795 may hide SoC differences. Test signals include dual pipeline display output, DPI/DSI routing, UFOE path selection, and checking that zero-valued selections are not mistaken for missing data.
