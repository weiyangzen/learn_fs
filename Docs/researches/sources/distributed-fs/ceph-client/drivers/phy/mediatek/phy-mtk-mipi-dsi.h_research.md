<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi.h -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi.h

Purpose: Declares the shared data structures and symbols for MediaTek MIPI DSI TX common and SoC-specific files.

Important APIs and types: `struct mtk_mipitx_data` provides SoC preserve value, clock ops, and signal callbacks. `struct mtk_mipi_tx` stores device, registers, cached data rate, drive strength, five RT calibration codes, SoC data, and PLL clock hardware. Declares common clock helpers and SoC data objects.

Control flow: No executable logic. The header defines callback boundaries used by common probe and MT2701/MT8173/MT8183 implementations.

State and persistence: The struct fields hold runtime state used across clk and PHY callbacks. `rt_code[]` persists software-side calibration data extracted from nvmem and then written to hardware by SoC code.

Dependencies and integration points: Includes clk, nvmem, platform, PHY, module, delay, and slab headers. Shared by aggregate `phy-mtk-mipi-dsi-drv`.

Risks: Adding fields or changing callback semantics affects all SoC implementations. Clock op style differs between MT8173-style prepare and MT8183-style enable callbacks but shares the same common state.

Test signals: Aggregate module compile/link, all SoC match data references, and panel enable paths invoking both common and SoC callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-dsi.h -->
