# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6q.c

## Purpose
`clk-imx6q.c` registers the i.MX6Q, i.MX6DL, and i.MX6QP CCM/ANATOP clock topology. It exposes `IMX6QDL_CLK_*` IDs as a hardware-clock onecell provider and models PLL bypasses, PFDs, audio/video post dividers, display/LDB paths, GPU/IPU/MMDC/AXI buses, ENET/PCIe/SATA references, and large peripheral gate banks. It also handles several hardware quirks that must be resolved before ordinary CCF consumers manipulate the clocks.

## Important APIs, Types, And Functions
State is held in `static struct clk_hw **hws` and `static struct clk_hw_onecell_data *clk_hw_data`. `clk_on_imx6q()`, `clk_on_imx6qp()`, and `clk_on_imx6dl()` branch registration for SoC variants. `ldb_di_sel_by_clock_id()` and `of_assigned_ldb_sels()` parse `assigned-clock-parents` so LDB DI muxes can be safely initialized before read-only registration. `pll6_bypassed()` detects static ENET PLL bypass configuration. `mmdc_ch1_disable()`, `mmdc_ch1_reenable()`, and `init_ldb_clks()` implement the special multi-step LDB mux transition. `disable_anatop_clocks()` gates unused PFDs and PLL5 after safe parents are known. `imx6q_obtain_fixed_clk_hw()` prefers OF-provided fixed clocks but falls back to local fixed-clock creation.

The main `imx6q_clocks_init()` allocates the flexible onecell array, maps ANATOP and CCM, registers PLL/PFD/fixed-factor/mux/divider/busy-divider/gate/shared-gate clocks, publishes the provider, and applies default parent/rate policy.

## Control Flow
Initialization starts from `CLK_OF_DECLARE(imx6q, "fsl,imx6q-ccm", imx6q_clocks_init)`. The driver obtains fixed inputs, maps `fsl,imx6q-anatop`, adjusts post-divider tables for i.MX6Q revision 1.0, builds PLL bypass sources and PLL gates, models ENET PLL outputs differently depending on bypass state, and creates LVDS exclusive in/out gates. After PFD and fixed-factor clocks are created, CCM muxes and dividers are registered. The code masks MMDC handshakes, initializes LDB DI muxes before registration on non-QP parts, gates large CCGR banks, checks all hardware clocks, and calls `of_clk_add_hw_provider()`. Post-registration setup assigns display, ENFC, USB PHY, CLKO, SPDIF, PCIe, GPU, and ENET parents/rates.

## State And Persistence
Runtime state includes the global `hws` array, shared-gate refcounts for ESAI/ASRC/SSI/MIPI/SPDIF/PRG, and hardware CCM/ANATOP/IOMUXC-GPR register contents. No persistent storage is used. Hardware state persists until reset and includes gate bits, mux choices, divider settings, PLL bypass bits, and GPR ENET reference mux selection.

## Dependencies And Integration Points
The file integrates with CCF `clk_hw` provider APIs, `dt-bindings/clock/imx6qdl-clock.h`, OF assigned-clock properties, SoC revision checks, `imx_mmdc_mask_handshake()`, `imx_clk_gpr_mux()` through `fsl,imx6q-iomuxc-gpr`, optional USB PHY and PCIe configurations, and `imx_register_uart_clocks()`. Consumers include IPU/LDB display, GPU, ENET, PCIe, SATA, SDHC, audio, UART, and memory-controller users.

## Risks
The LDB and MMDC code is high-risk because incorrect parent switching can glitch display clocks or disable a memory-derived clock. The PLL6 bypass model is intentionally static; changing assumptions later can misrepresent ENET/SATA/PCIe rates. Many branches reuse IDs differently across Q/DL/QP, so missing variant coverage can leave NULL `hws` entries. Register table mutations for i.MX6Q rev 1.0 affect global divider tables and must run before divider registration. `WARN_ON(!base)` does not stop execution after failed MMIO mapping.

## Test Signals
Boot should show no missing `imx_check_clk_hws()` entries and no LDB glitch/errors unless firmware already changed reset mux state. Check `clk_summary` for expected ENET/SATA/PCIe/LDB/IPU/GPU parents. Display panels using LDB/IPU, PCIe with LVDS1 reference, ENET reference selection via GPR, USB PHY refcounting, SDHC, SPDIF/audio clocks, and GPU rate ceilings are the primary integration tests.
