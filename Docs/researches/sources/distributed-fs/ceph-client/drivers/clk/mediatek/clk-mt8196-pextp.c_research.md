# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-pextp.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-pextp.c

### Purpose
`clk-mt8196-pextp.c` registers MT8196 PCIe transmit PHY clock and reset providers for PEXTP0 and PEXTP1. It covers PCIe MAC/PHY TL, REF, MCU bus, AXI, AHB/APB, PL, and VLP low-power clocks.

### Important APIs, Types, And Functions
The file defines `GATE_PEXT`, two gate arrays, two reset index maps, `pext_rst_desc`, `pext1_rst_desc`, and descriptors with `.rst_desc`. It uses `MTK_RST_SET_CLR` reset semantics and reset IDs from `mediatek,mt8196-resets.h`.

### Control Flow, State, And Persistence
OF matching selects either PEXTP0 or PEXTP1. `mtk_clk_simple_probe()` registers both clocks and reset controller data from the descriptor. Gate state is stored in PEXTP CG registers, while reset state is controlled through set/clear reset banks.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include PCIe PHY/MAC consumers, parent clocks `tl`, `tl_p1`, `tl_p2`, `ufs_pexpt0_mem_sub`, `ufs_pextp0_axi`, `pextp1_usb_axi`, and reset framework integration. Risks include reset index map off-by-one errors, mismatched PEXTP0/PEXTP1 compatible usage, and incorrect memory-subsystem parents. Test signals include PCIe port probe/reset, reset-controller lookup, link training, clk summary, and unbind/rebind of both providers.
