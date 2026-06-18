# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8186-mmsys.h

## Purpose
This header provides MT8186 MMSYS route definitions, OVL blend/background control bits, DPI output format constants, and software reset offset.

## Important APIs, Types, and Functions
The central artifact is `mmsys_mt8186_routing_table[]`. It maps OVL0 and OVL_2L0 to RDMA0/RDMA1, RDMA0 to COLOR0, DITHER0 to DSI0, and RDMA1 to DPI0. It also defines `MT8186_MMSYS_DPI_OUTPUT_FORMAT`, used by `mtk_mmsys_ddp_dpi_fmt_config()`.

## Control Flow and State
The header has no local execution. Its values drive masked register writes in MMSYS connect/disconnect and DPI format configuration. Hardware state includes output muxes, overlay blend path selections, and `SW0_RST_B` reset bits.

## Dependencies and Integration Points
`mtk-mmsys.c` binds this table to `mediatek,mt8186-mmsys` and exposes DPI format configuration to display drivers. The reset controller uses `MT8186_MMSYS_SW0_RST_B` with 32 resets.

## Risks and Test Signals
The overlap between MOUT, SEL_IN, and OVL_CON fields makes mask accuracy important. Test signals include RDMA0 DSI/COLOR output, RDMA1 DPI output, DPI RGB format changes, and reset controller exercise.
