# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-fsd.c

## Purpose
`clk-fsd.c` is the Samsung common clock framework provider for the Tesla/Samsung FSD SoC. It maps FSD clock-management-unit register blocks into CCF clocks, reset-adjacent gate controls, and power-domain-aware platform CMU providers. The file covers CMU_CMU, PERIC, FSYS0, FSYS1, IMEM, MFC, and CAM_CSI.

CMU_CMU is the root provider. It defines four shared PLLs, their derived divider clocks, and gated exports used by downstream domains. PERIC covers Ethernet, GPIO, ADC, PWM, DMA, I2C, MCAN, SPI, TDM, and UART clocks. FSYS0 handles UFS, PCIe, and EQOS-related clocks. FSYS1 handles two PCIe links and PCIe PHY reference paths. IMEM covers timers, watchdogs, TMUs, DMA, interrupt/memory infrastructure, and system registers. MFC and CAM_CSI are media/camera-local PLL and gate providers.

## Important APIs, Types, And Functions
The driver is descriptor-driven. It uses `struct samsung_pll_rate_table`, `struct samsung_pll_clock`, `struct samsung_fixed_rate_clock`, `struct samsung_mux_clock`, `struct samsung_div_clock`, `struct samsung_gate_clock`, and `struct samsung_cmu_info`. The helper macros `PLL()`, `FRATE()`, `PNAME()`, `MUX()`, `DIV()`, and `GATE()` encode all clock topology. Clock IDs come from `dt-bindings/clock/fsd-clk.h`.

The direct functions are `fsd_clk_cmu_init()`, `fsd_clk_imem_init()`, `fsd_cmu_probe()`, and `fsd_cmu_init()`. `fsd_clk_cmu_init()` registers the root CMU_CMU early for `tesla,fsd-clock-cmu` using `samsung_cmu_register_one()`. `fsd_clk_imem_init()` similarly registers IMEM early for `tesla,fsd-clock-imem`. `fsd_cmu_probe()` reads the matched `samsung_cmu_info` from OF match data and calls `exynos_arm64_register_cmu()`. `fsd_cmu_init()` registers the `fsd-cmu` platform driver at `core_initcall()`.

The key descriptor blocks are `cmu_cmu_info`, `peric_cmu_info`, `fsys0_cmu_info`, `fsys1_cmu_info`, `imem_cmu_info`, `mfc_cmu_info`, and `cam_csi_cmu_info`. Each includes its domain's `clk_regs` save/restore list and a `CLKS_NR_*` bound based on the last binding ID used by that domain.

## Control Flow
Boot starts with early OF clock declarations. CMU_CMU is registered from `CLK_OF_DECLARE(fsd_clk_cmu, "tesla,fsd-clock-cmu", fsd_clk_cmu_init)` so shared PLL outputs and top-level derived clocks exist before downstream devices request them. IMEM is also registered early through `CLK_OF_DECLARE(fsd_clk_imem, "tesla,fsd-clock-imem", fsd_clk_imem_init)`, reflecting its timer, watchdog, TMU, DMA, and interrupt-infrastructure role.

The remaining CMUs are registered by the `fsd-cmu` platform driver. Its match table maps `tesla,fsd-clock-peric`, `tesla,fsd-clock-fsys0`, `tesla,fsd-clock-fsys1`, `tesla,fsd-clock-mfc`, and `tesla,fsd-clock-cam_csi` to the corresponding descriptor. Probe has no per-domain logic beyond fetching match data and handing the descriptor to the Exynos ARM64 CMU helper.

Runtime operations are handled by Samsung CCF helpers. PLL rate tables define allowable PLL programming for the shared root PLLs, MFC PLL, and CAM_CSI PLL. Mux, divider, and gate descriptors translate consumer requests into MMIO field updates and gate bit changes. Many gates are marked `CLK_IGNORE_UNUSED`, so the late unused-clock cleanup should not disable them even if there is not yet an explicit consumer.

## State And Persistence
The driver has no persistent storage and no complex runtime data structure of its own. Boot-time descriptor arrays are marked `__initconst`; durable runtime state for the boot is the programmed CMU register state and registered CCF clock objects.

CMU_CMU defines four `pll_142xx` shared PLLs with fixed tables: shared0 at 2.0 GHz, shared1 and shared2 at 2.4 GHz, and shared3 at 1.8 GHz from `fin_pll`. Derived dividers and gates create named roots such as `dout_cmu_pll_shared0_div4`, `dout_cmu_fsys0_shared1div4`, `dout_cmu_fsys1_shared0div4`, `dout_cmu_imem_aclk`, and `dout_cmu_peric_shared*`. Downstream domains select between `fin_pll` and those CMU_CMU outputs.

PERIC includes a fixed 125 MHz `eqos_phyrxclk`. FSYS0 includes fixed 125 MHz EQOS PHY RX, 26 MHz MPHY reference, and 100 MHz PCIe PHY XTAL clocks. FSYS1 defines fixed 100 MHz PHY reference clocks. MFC and CAM_CSI each define local PLLs with single-entry rate tables. IMEM marks DMA0 and DMA1 ACLK gates with `CLK_IS_CRITICAL`, and MFC marks `mfc_busd_gate` critical, which makes those gates part of the boot stability contract.

## Dependencies And Integration Points
The file depends on Linux CCF, platform, OF, and Samsung Exynos ARM64 CMU helpers. Device-tree compatibility strings use the Tesla vendor prefix, and consumers identify clocks via `fsd-clk.h`.

PERIC integrates with the EQOS Ethernet MAC and PTP/RGMII/RII/RMII paths, GPIO, ADC, PWM, DMA, I2C0-I2C7, four MCAN controllers, SPI0-SPI2, TDM0/TDM1, UART0/UART1, SMMU, APB bridges, and sysreg. FSYS0 integrates with UFS top0/top1, PCIe sub-controller instance 0, EQOS top0, MPHY references, PCIe PHY references, SMMU, and bus fabric clocks. FSYS1 integrates with PCIe link0/link1, PCIe PHY0, auxiliary/ref clocks, DBI/master/slave ACLKs, TBU, sysreg, and bus fabric clocks. IMEM integrates with MCT, watchdogs, TMU sensors, GIC, mailbox, DMA, internal memory, OTP, reset sync, TBU, TCU, and sysreg. CAM_CSI integrates with three CSI groups with four lanes/instances each plus camera bus, NoC, bridge, sysreg, and TBU clocks.

## Risks
Descriptor accuracy is the main risk. The file encodes many register offsets and gate bits, and small copy/paste mistakes can affect unrelated hardware because all gates use bit 21 at different offsets. Parent clock names must line up with clocks registered by CMU_CMU or fixed-rate descriptors; a typo can leave consumers with orphan parents or fallback rates.

`CLK_IGNORE_UNUSED` is widely applied, so clock leaks can be masked during bring-up. Conversely, removing it can break hardware blocks whose drivers do not explicitly claim every bus, bridge, SMMU, or sysreg clock. `CLK_IS_CRITICAL` on IMEM DMA gates and the MFC bus gate should be changed only with hardware evidence.

The early/root split matters. CMU_CMU and IMEM use `samsung_cmu_register_one()` early, while PERIC/FSYS/MFC/CAM_CSI are platform-driver managed. Changing registration order can break timer/watchdog/TMU/GIC availability or leave downstream domain parents unavailable. Rate tables are single-entry for most PLLs, which limits dynamic rate flexibility and means any requested alternate rate will depend on generic framework behavior rather than a rich local table.

Several names preserve hardware or generated spelling, such as `fsys1_phy0_osccllk` and `GAT_CMU_PERIC_SHARED0DIVE*`. They look like typos but are internally referenced, so cleanup must not rename them without checking binding/user impact and parent references.

## Test Signals
Build validation should compile this driver with `fsd-clk.h` and catch duplicate symbol, missing ID, or parent-name reference problems. Boot logs should show successful early registration for `tesla,fsd-clock-cmu` and `tesla,fsd-clock-imem`, plus successful probes for PERIC, FSYS0, FSYS1, MFC, and CAM_CSI.

Runtime validation should inspect `/sys/kernel/debug/clk/clk_summary` for shared PLLs, CMU_CMU derived roots, PERIC UART/SPI/I2C/MCAN/EQOS clocks, FSYS0 UFS/PCIe/EQOS clocks, FSYS1 PCIe link clocks, IMEM TMU/WDT/MCT/GIC/DMA clocks, MFC clocks, and CAM_CSI clocks. Hardware tests should cover UART, SPI, I2C, MCAN, Ethernet including PTP and RGMII/RMII/RII modes, UFS top0/top1 link-up, PCIe instance 0 and FSYS1 link0/link1 training, watchdog/timer/TMU operation, MFC media access, camera CSI capture paths, and suspend/resume with CMU register restore if supported.
