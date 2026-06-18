<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167.c

Purpose: This is the main MT8167 topckgen/infracfg clock driver. It defines fixed clocks, PLL factors, a large set of top-level mux composites, infrastructure muxes, adjustable dividers, and top clock gates.

Important APIs, types, and functions: `fixed_clks`, `top_divs`, `top_muxes`, `ifr_muxes`, `top_adj_divs`, and `top_clks` are grouped into `topck_desc` and `infra_desc`. Gate banks `top0` through `top5` cover clocks for audio, storage, USB, display, NAND, GPU, and peripheral functions. The platform driver matches `mediatek,mt8167-topckgen` and `mediatek,mt8167-infracfg`.

Control flow: Simple probe chooses the descriptor from OF match data. For topckgen it registers fixed clocks, factors, composites, dividers, gates, and uses `mt8167_clk_lock`; for infracfg it registers infracfg composites. Consumers use binding IDs from `mt8167-clk.h`.

State and persistence behavior: Clock selection and divider/gate state reside in SoC clock registers. Provider state is volatile. The spinlock protects shared register updates for muxes/dividers/gates.

Dependencies and integration points: It depends on PLL parent names from apmixedsys, common MediaTek clock/gate/divider helpers, OF platform binding, and syscon/MFD headers. It feeds the whole MT8167 platform: AXI/infra, DDRPHY, MFG, MSDC, USB, audio, DPI, VDEC, Ethernet, NAND, SPI, I2C, UART, PWM, and debug clocks.

Risks and edge cases: This file is highly table-driven and vulnerable to parent-order, bit-field, and gate-polarity mistakes. Shared register locking is important. `top_muxes` is marked `__initdata`, so registration must copy or consume it before init memory is discarded.

Test signals: Boot all topckgen/infracfg consumers, compare rates against the datasheet, exercise storage/audio/display/VDEC/USB/Ethernet paths, verify gate polarity in clk summary, and run suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167.c -->
