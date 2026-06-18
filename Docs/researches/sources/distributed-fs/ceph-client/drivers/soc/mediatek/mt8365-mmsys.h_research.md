# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8365-mmsys.h

## Purpose
This header describes MT8365 MMSYS route registers for a display pipeline involving OVL0, RDMA0/RDMA1, COLOR0, CCORR, DITHER0, DSI0, DPI0, and LVDS clock selection.

## Important APIs, Types, and Functions
The important data is `mt8365_mmsys_routing_table[]`. It includes MOUT, SOUT, SEL_IN, RDMA0_RSZ0, and LVDS system configuration routes. `MT8365_DISP_MS_IN_OUT_MASK` is used broadly for four-bit selector fields.

## Control Flow and State
The header has no local execution. The MMSYS driver writes the described route values when display components are connected or disconnected. LVDS/DPI selection is captured as route state as well.

## Dependencies and Integration Points
It depends on the shared MMSYS route type and DDP component constants and is bound to `mediatek,mt8365-mmsys` in `mtk-mmsys.c`.

## Risks and Test Signals
There is a duplicate definition of `MT8365_DPI0_SEL_IN_RDMA1`, which is harmless but a maintenance signal. Test signals include DSI0 and DPI0 output, LVDS pixel clock route, RDMA0 resize path, and display component chain validation.
