# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-msdc.c

## Purpose
`clk-mt8192-msdc.c` registers MT8192 MSDC top clocks for eMMC/SD storage controller support.

## Important APIs, Types, And Functions
The file defines `msdc_top_cg_regs`, `msdc_top_clks`, `msdc_top_desc`, and the OF compatible `mediatek,mt8192-msdc_top`. It uses the simple MediaTek clock helper pair.

## Control Flow, State, And Persistence
Probe registers storage-related gates and publishes the provider. Persistent state is only the registered CCF clocks and hardware gate state.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are MMC/SD/eMMC host controller nodes and top storage clock parents. Risks include storage boot failures if critical bus/storage gates are wrong. Test signals include rootfs-on-eMMC boot, SD card probe, high-speed mode negotiation, and suspend/resume.
