<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-topckgen.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-topckgen.c

Purpose: This file registers MT7988 topckgen and mcusys clocks: fixed oscillator aliases, fixed PLL-derived factors, top-level muxes for networking/storage/audio/peripheral domains, one audio divider composite, and CPU/MCU bus mux composites.

Important APIs, types, and functions: It uses `struct mtk_fixed_clk`, `struct mtk_fixed_factor`, `struct mtk_mux`, `struct mtk_composite`, `struct mtk_clk_desc`, `mtk_clk_simple_probe`, and `mtk_clk_simple_remove`. `topck_desc` exposes `top_fixed_clks`, `top_divs`, `top_muxes`, `top_aud_divs`, and `mt7988_clk_lock`; `mcusys_desc` exposes `mcu_muxes`. OF compatibles are `mediatek,mt7988-topckgen` and `mediatek,mt7988-mcusys`.

Control flow: Platform probe is entirely table-driven. The common MediaTek simple probe obtains the MMIO base from the matching OF node, allocates onecell clock data, registers fixed clocks/factors, muxes, and composites from the selected descriptor, and publishes them as an OF clock provider. Consumers then select mux parents or audio divider rates through the common clock framework.

State and persistence behavior: State is volatile kernel clock-provider state plus register bits in the topckgen/mcusys MMIO blocks. The spinlock serializes mux and composite register updates. There is no disk persistence; removal unregisters the provider and clocks.

Dependencies and integration points: The driver depends on `clk-mtk.h`, `clk-gate.h`, `clk-mux.h`, the MT7988 clock binding IDs, DT clock names such as `top_xtal`, `net1pll`, `net2pll`, `mmpll`, `apll2`, and MediaTek common clock registration helpers. It feeds Ethernet, USXGMII, PCIe, storage, UART, SPI, I2C, audio, TOPS/NPU, and CPU-bus consumers.

Risks and edge cases: Parent arrays must match hardware mux encodings exactly; wrong order silently selects bad rates. Shared mux registers require the lock. The mcusys and topckgen descriptors share one driver but expose different clock sets, so compatible-string routing is critical. Network clocks use many divided PLL paths, making regressions visible as Ethernet/PCIe/USXGMII failures.

Test signals: Boot with both compatibles present, inspect `/sys/kernel/debug/clk/clk_summary`, exercise Ethernet/USXGMII, PCIe, eMMC/SPI/NAND, UART, I2C, and audio paths, change mux parents through consumers, and unload/reload the module where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-topckgen.c -->
