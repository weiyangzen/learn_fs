# subset-b-001145

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm8550.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm8550.c

## Purpose

`gcc-sm8550.c` is the Qualcomm Global Clock Controller driver for the SM8550 SoC. It describes the GCC MMIO register block to the common Qualcomm clock-controller framework, exporting clock, reset, and power-domain handles through the IDs in `dt-bindings/clock/qcom,sm8550-gcc.h`.

The file is mostly declarative clock data. It builds the platform clock tree from external device-tree parents (`bi_tcxo`, sleep, PCIe pipe, PCIe PHY aux, UFS symbol, and USB3 pipe clocks), internal Lucid OLE GPLLs, parent selector tables, RCGs, read-only dividers, PHY muxes, branch gates, GDSCs, and reset maps. Runtime register access and common-clock behavior are delegated to shared qcom helpers.

## Important APIs, Types, And Functions

- `struct clk_alpha_pll` and `struct clk_alpha_pll_postdiv` model `gcc_gpll0`, `gcc_gpll4`, `gcc_gpll7`, `gcc_gpll9`, and `gcc_gpll0_out_even`. All use Lucid OLE register layouts and fixed PLL/post-divider operations.
- Local `DT_*` and `P_*` enums define, respectively, external DT parent indices and internal parent identifiers used by the RCG `parent_map` arrays.
- `struct parent_map` plus `struct clk_parent_data` arrays translate hardware selector values to CCF parents. These cover XO/sleep/GPLL selections, PCIe PHY aux, UFS symbol parents, and the USB3 pipe parent.
- `struct clk_regmap_phy_mux` is used for PCIe pipe parents. `struct clk_regmap_mux` is used for PCIe1 PHY aux, UFS RX/TX symbol, and USB3 pipe muxes with `clk_regmap_mux_closest_ops`.
- `struct freq_tbl` arrays encode allowed rates for GP clocks, PCIe aux/rchng clocks, PDM, QUPv3 serial engines, SDCC2/SDCC4, UFS PHY AXI/ICE/AUX/UNIPRO, and USB30 master/mock UTMI paths.
- `struct clk_rcg2` instances implement root clock generators. QUP serial engines use `clk_rcg2_ops`, GP/PCIe/PDM/UFS use shared RCG ops, SDCC apps clocks use `clk_rcg2_shared_floor_ops`, and USB30 master uses `clk_rcg2_shared_no_init_park_ops`.
- `struct clk_regmap_div` exposes `gcc_usb30_prim_mock_utmi_postdiv_clk_src` as a read-only divider.
- `struct clk_branch` entries provide the leaf gates exported to consumers. Branches use `BRANCH_HALT`, `BRANCH_HALT_VOTED`, `BRANCH_HALT_SKIP`, or `BRANCH_HALT_DELAY` depending on hardware ownership and halt semantics; many include hardware clock gating (`hwcg_reg`/`hwcg_bit`).
- `struct gdsc` entries define PCIe0/1 controller and PHY domains, UFS PHY and memory PHY domains, and USB30/USB3 PHY domains.
- `struct qcom_reset_map gcc_sm8550_resets[]` maps binding reset IDs to block reset registers and two video AXI ARES bits with a 1000 us delay.
- `gcc_sm8550_probe()` maps the controller, registers DFS metadata, performs UFS ICE memory-core retention setup, marks a set of infrastructure clocks always-on, clears the GDSC sleep vote register, and then calls `qcom_cc_really_probe()`.

## Control Flow

Driver registration happens from `subsys_initcall(gcc_sm8550_init)`, which registers a platform driver matching `compatible = "qcom,sm8550-gcc"`. Probe performs a two-stage qcom CC setup rather than using `qcom_cc_probe()` directly:

1. `qcom_cc_map(pdev, &gcc_sm8550_desc)` maps the GCC register range using `gcc_sm8550_regmap_config`.
2. `qcom_cc_register_rcg_dfs()` registers dynamic frequency scaling metadata for the sixteen QUPv3 wrapper RCGs.
3. `regmap_update_bits()` sets bit 14 in the UFS PHY ICE core clock halt register to force memory core retention for that clock path.
4. `qcom_branch_set_clk_en()` enables always-on camera, display, GPU, and video AHB/XO/config clocks that are not otherwise exported as normal branch entries in this file.
5. `regmap_write(regmap, 0x52024, 0x0)` clears `GDSC_SLEEP_ENA_VOTE`, preventing sleep from automatically removing GDSC votes.
6. `qcom_cc_really_probe()` registers clocks, resets, and GDSCs with CCF, reset, and genpd.

After probe, consumers use normal CCF/reset/genpd APIs. Rate requests select rows from each `freq_tbl`, RCG ops program parent selectors and dividers, branch ops toggle enable bits, reset ops manipulate reset registers, and GDSC ops manage power-domain state.

## Clock And Subsystem Coverage

- Root sources: external XO/sleep/pipe/symbol clocks plus GPLL0, GPLL4, GPLL7, GPLL9, and GPLL0 even divider.
- General-purpose clocks: `gcc_gp1_clk`, `gcc_gp2_clk`, and `gcc_gp3_clk` with 50/100/200 MHz source choices.
- PCIe: two controllers with aux, cfg AHB, master/slave AXI, slave Q2A AXI, pipe, PHY rchng, and PCIe1 PHY aux paths, plus PCIe controller and PHY GDSCs/resets.
- QUPv3: ten I2C serial clocks and two QUP wrapper blocks with eight serial engines each. DFS metadata covers the wrapper serial RCGs.
- Storage: SDCC2 and SDCC4 apps/AHB clocks with floor rate selection; UFS PHY AXI, ICE core, PHY aux, UNIPRO core, RX/TX symbol clocks, hardware-control variants, UFS GDSCs, and UFS reset.
- USB: USB30 primary master/mock UTMI/sleep, USB3 PHY aux/com aux/pipe, USB30 and USB3 PHY GDSCs, and USB/QUSB/DP PHY resets.
- Multimedia and GPU infrastructure: camera/display/video AXI and QMIP AHB clocks, GPU GPLL0 branch exports, GPU memnoc/SNOC/DVM clocks, and always-on probe enables for some AHB/XO paths.
- PDM and boot ROM: PDM2 source/branch, PDM AHB/XO4, and boot ROM AHB.

## State And Persistence Behavior

The persistent state is hardware register state in the GCC block. The driver does not allocate private runtime state, does not start workqueues or timers, and has no suspend/resume callbacks. Framework state is owned by CCF, reset-controller, and genpd registration.

Clock rates, gate enables, reset assertions, DFS programming, and GDSC votes persist in MMIO registers until another agent changes them or the SoC resets. Probe intentionally mutates a few persistent bits: it forces UFS ICE memory core retention, enables selected infrastructure clocks, and clears the GDSC sleep-vote auto-removal register. Boot firmware may have left some clocks and PLLs enabled before Linux probes; this driver describes legal control paths rather than reinitializing every clock.

## Dependencies And Integration Points

- Linux platform driver and OF matching: `<linux/platform_device.h>`, `<linux/of.h>`, `MODULE_DEVICE_TABLE()`, `subsys_initcall()`, and `module_exit()`.
- Linux CCF: `<linux/clk-provider.h>`, qcom alpha PLL, RCG, branch, regmap mux/divider, and PHY mux helpers.
- Regmap: `gcc_sm8550_regmap_config` uses 32-bit registers, 4-byte stride, 32-bit values, `max_register = 0x1f41f0`, and `fast_io = true`.
- Reset framework: `gcc_sm8550_resets[]` is bound into `gcc_sm8550_desc`.
- Generic power domains/GDSC: `gdsc.h` and `gcc_sm8550_gdscs[]` expose PCIe, UFS, and USB domains.
- Device-tree ABI: external parent order must match the local `DT_*` enum, and consumers use the IDs from `qcom,sm8550-gcc.h`.
- Shared qcom CC helpers: `qcom_cc_map()`, `qcom_cc_register_rcg_dfs()`, `qcom_cc_really_probe()`, and `qcom_branch_set_clk_en()`.

## Risks And Edge Cases

- Binding order is critical. A mismatch between the GCC node `clocks` list and the `DT_*` enum can silently select the wrong pipe, symbol, XO, or sleep parent.
- Rate tables are hardware-facing. Mistakes in QUP fractional rates, SDCC floor rates, UFS high-speed rates, PCIe rchng rates, or USB master rates can break peripheral function or overclock hardware.
- Halt-check mode changes are risky. Pipe and symbol clocks use delayed/skip halt checks for externally timed sources, while shared infrastructure uses voted checks. Converting these to ordinary halt checks can cause false timeouts or races.
- Probe mutates non-obvious retention and always-on state. Removing the UFS ICE force bit, always-on AHB/XO enables, or `GDSC_SLEEP_ENA_VOTE` clear may cause suspend/resume or late peripheral failures.
- GDSC collapse register offsets and masks are shared control-plane data. Incorrect masks can collapse the wrong PCIe controller/PHY domain.
- The reset map is dense and offset-based. Off-by-one reset IDs or register offsets could reset camera, display, GPU, PCIe, UFS, USB, or video blocks unexpectedly.
- External PHY pipe and UFS symbol clocks depend on PHY providers. Missing or late providers can lead to probe deferral or unusable high-speed links.

## Test Signals

- Build with the SM8550 GCC Kconfig option enabled and ensure no missing binding IDs, bad initializer types, or qcom clock helper API mismatches.
- Boot an SM8550 device tree with `qcom,sm8550-gcc` and confirm GCC probes before dependent PCIe, UFS, USB, SDCC, QUP, GPU/display/camera/video consumers.
- Inspect `/sys/kernel/debug/clk/clk_summary` for GPLLs, GP clocks, QUPv3 wrapper clocks, SDCC2/4, UFS, PCIe, and USB entries.
- Exercise QUP I2C/SPI/UART serial engines, SDCC2/SDCC4 storage, UFS link bring-up and ICE operation, PCIe0/1 link training, and USB3 operation.
- Validate power domains by toggling PCIe, UFS, and USB consumers and checking genpd/GDSC debugfs state.
- Validate reset consumers for PCIe, UFS, USB PHYs, SDCC, QUP wrappers, video ARES, camera/display/GPU/video block resets.
- Suspend/resume tests should watch for regressions from the always-on clocks and the cleared GDSC sleep-vote behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm8550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm8650.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm8650.c

## Purpose

`gcc-sm8650.c` is the Qualcomm Global Clock Controller driver for the SM8650 SoC. It exports the SoC GCC clock, reset, and GDSC power-domain controls to Linux using the IDs from `dt-bindings/clock/qcom,sm8650-gcc.h`.

The driver is an SM8650-specific data description for the common qcom clock-controller framework. It defines external parent ordering, Lucid OLE GPLLs including always-on variants, RCG rate tables, QUP/QSPI dividers, PHY muxes, branch gates, GDSCs, reset maps, and a small probe sequence for DFS and retention programming.

## Important APIs, Types, And Functions

- `struct clk_alpha_pll` describes normal GPLLs `gcc_gpll0`, `gcc_gpll1`, `gcc_gpll3`, `gcc_gpll4`, `gcc_gpll6`, `gcc_gpll7`, `gcc_gpll9` and always-on GPLLs `gcc_gpll0_ao`, `gcc_gpll1_ao`, `gcc_gpll3_ao`, `gcc_gpll4_ao`, `gcc_gpll6_ao`.
- `struct clk_alpha_pll_postdiv` exposes `gcc_gpll0_out_even` and `gcc_gpll0_out_even_ao` from GPLL0. PLLs use Lucid OLE fixed ops and enable registers `0x52020` or AO register `0x57020`.
- The `DT_*` enum explicitly must match the DT binding clock-parent order and includes both `DT_BI_TCXO` and `DT_BI_TCXO_AO`.
- `parent_map` and `clk_parent_data` arrays map hardware parent selectors to XO/sleep/GPLL/PHY/symbol parents. SM8650 adds GPLL1/GPLL3/GPLL6 parent choices compared with SM8550-style maps.
- `clk_regmap_phy_mux` entries handle PCIe0/PCIe1 pipe clocks. `clk_regmap_mux` entries handle PCIe1 PHY aux, UFS RX/TX symbol muxes, and the USB3 pipe mux.
- `freq_tbl` arrays cover GP clocks, PCIe aux/rchng, PDM2, QUPv3 serial rates, QSPI reference rates, QUPv3 IBI control, SDCC2/SDCC4, UFS AXI/ICE/AUX/UNIPRO, and USB30 master/mock UTMI.
- `clk_rcg2` entries implement most programmable sources. SDCC apps clocks use floor ops; QUP wrapper RCGs are registered for DFS; USB30 master uses shared ops.
- `clk_regmap_div` exposes read-only dividers for `gcc_qupv3_wrap1_s2_clk_src`, `gcc_qupv3_wrap3_s0_clk_src`, and `gcc_usb30_prim_mock_utmi_postdiv_clk_src`.
- `clk_branch` entries export leaf gates across PCIe, QUPv3, QSPI, IBI, SDCC, UFS, USB, GPU, multimedia, PDM, and boot ROM domains.
- `gdsc` entries expose PCIe0/1 controller and PHY domains, UFS PHY/memory PHY domains, USB30 primary, and USB3 PHY domains.
- `gcc_sm8650_probe()` maps registers, registers DFS RCGs, enables always-on infrastructure clocks, sets UFS ICE and UFS AXI force-memory-core behavior, clears GDSC sleep vote removal, and finalizes qcom CC registration.

## Control Flow

The module registers a platform driver at `subsys_initcall(gcc_sm8650_init)`. The OF match table binds `compatible = "qcom,sm8650-gcc"` to `gcc_sm8650_probe()`.

Probe flow:

1. `qcom_cc_map(pdev, &gcc_sm8650_desc)` maps the MMIO region using `gcc_sm8650_regmap_config`.
2. `qcom_cc_register_rcg_dfs()` registers DFS data for QUPv3 wrapper 1 serial/QSPI sources, wrapper 2 serial sources, and wrapper 3 QSPI source.
3. `qcom_branch_set_clk_en()` keeps camera AHB/XO, display AHB/XO, GPU config AHB, and video AHB/XO clocks enabled.
4. `qcom_branch_set_force_mem_core()` enables FORCE_MEM_CORE_ON behavior for `gcc_ufs_phy_ice_core_clk` and `gcc_ufs_phy_axi_clk`.
5. `regmap_write(regmap, 0x52150, 0x0)` clears `GDSC_SLEEP_ENA_VOTE`.
6. `qcom_cc_really_probe()` registers clocks, resets, and GDSCs with the kernel frameworks.

After registration, consumers use CCF to prepare/enable clocks and request rates, reset-controller APIs to assert/deassert resets, and genpd APIs to vote GDSCs on/off. The qcom common helpers perform the actual regmap reads and writes against the offsets declared in this file.

## Clock And Subsystem Coverage

- Root sources: external XO/AO XO, sleep clock, PCIe pipe clocks, PCIe1 PHY aux, UFS RX/TX symbol clocks, USB3 pipe clock, normal GPLLs, AO GPLLs, and GPLL0 even outputs.
- General-purpose clocks: three GP clocks with shared 50/100/200 MHz tables.
- PCIe: two PCIe controllers with aux, cfg AHB, master/slave AXI, slave Q2A AXI, pipe, PHY rchng, PCIe1 PHY aux, resets, and GDSCs. Some ANOC/CNOC/DDRSS PCIe register offsets differ from SM8550.
- QUPv3 and QSPI: ten I2C serial clocks, QUP wrapper 1 and wrapper 2 serial engines, QUP wrapper 1 QSPI ref, wrapper 2 IBI AHB/control clocks, and wrapper 3 core/QSPI/S0 clocks. Wrapper 1 S2 and wrapper 3 S0 sources are read-only dividers from QSPI reference RCGs.
- Storage: SDCC2/SDCC4 apps/AHB; UFS PHY AXI, ICE, PHY aux, UNIPRO, symbol clocks, hardware-control clocks, GDSCs, and reset.
- USB: USB30 primary master/mock UTMI/sleep and USB3 PHY aux/com aux/pipe clocks with USB30/USB3 PHY GDSCs and USB/QUSB/DP PHY resets.
- Multimedia/GPU infrastructure: camera/display/video AXI and QMIP AHB clocks, GPU GPLL0 branches, GPU memory/SNOC/DVM clocks, and always-on probe enables.
- PDM and boot ROM: PDM2, PDM AHB/XO4, and boot ROM AHB clocks.

## State And Persistence Behavior

The driver stores no private mutable state. Persistent state is the GCC MMIO register state programmed through regmap by qcom clock, reset, and GDSC helpers. CCF, reset, and genpd hold framework objects after `qcom_cc_really_probe()`.

Clock enables, selected parents, dividers, DFS state, reset assertions, and GDSC votes persist until reset or another firmware/kernel agent changes the registers. Probe makes deliberate persistent changes: it leaves selected infrastructure clocks enabled, forces memory-core retention on UFS ICE and UFS AXI branches, and disables automatic removal of GDSC sleep votes. The AO GPLLs and AO XO parent represent always-on clock islands and are exposed separately from normal GPLL outputs.

## Dependencies And Integration Points

- Linux platform/OF/module APIs: `<linux/mod_devicetable.h>`, `<linux/module.h>`, `<linux/platform_device.h>`, `MODULE_DEVICE_TABLE()`, `subsys_initcall()`, and `module_exit()`.
- Linux CCF and qcom helpers: alpha PLL, RCG2, branch2, regmap divider, regmap mux, PHY mux, and DFS helpers.
- Regmap: `gcc_sm8650_regmap_config` uses 32-bit registers, stride 4, 32-bit values, `max_register = 0x1f41f0`, and `fast_io = true`.
- Reset framework: `gcc_sm8650_resets[]` is registered through `gcc_sm8650_desc`.
- Generic power domains/GDSC: `gcc_sm8650_gdscs[]` exposes PCIe, UFS, and USB domains.
- Device-tree ABI: external parent ordering must match the local `DT_*` enum, especially the separate AO XO parent.
- Binding coverage: exported clock/reset/GDSC IDs come from `qcom,sm8650-gcc.h`; all consumer drivers rely on those stable IDs.

## Risks And Edge Cases

- The local `DT_*` enum is ABI-sensitive. Misordering `bi_tcxo`, `bi_tcxo_ao`, pipe clocks, UFS symbols, or USB pipe parents can create wrong parent selection with little diagnostic signal.
- AO and non-AO GPLL definitions share conceptual PLL names but different enable registers and parent clocks. Mixing AO and normal IDs can affect low-power behavior.
- Read-only QSPI dividers mean some wrapper clocks cannot be freely reprogrammed by Linux. Consumers must tolerate the hardware-programmed divider state.
- Rate-table errors can affect serial baud generation, QSPI, SDCC, UFS, PCIe, USB, and GP outputs. SDCC uses floor ops to avoid overclocking; changing that behavior is risky.
- Probe-time force-memory-core programming is necessary for UFS ICE/AXI stability. Removing or moving it can cause UFS failures, especially through suspend/resume or low-power transitions.
- GDSC collapse registers use SM8650-specific `0x5214c` and sleep-vote register `0x52150`. Copying SM8550 values here would affect power votes incorrectly.
- Halt-check choices reflect hardware behavior. Voted, skipped, and delayed checks should not be normalized without hardware validation.
- Reset map changes can reset unrelated subsystems, especially because QUP wrapper 3, USB PHY, PCIe PHY, video ARES, and multimedia block resets are adjacent in the binding space.

## Test Signals

- Build with SM8650 GCC support enabled and check for binding ID, initializer, and qcom helper API errors.
- Boot an SM8650 DT containing `qcom,sm8650-gcc`; confirm dependent QUP, QSPI, SDCC, UFS, PCIe, USB, GPU/display/camera/video devices leave probe deferral.
- Inspect `clk_summary` for normal and AO GPLLs, QUP wrapper 1/2/3 clocks, QSPI reference clocks, IBI clocks, SDCC2/4, UFS, PCIe, and USB clocks.
- Exercise QUP I2C/SPI/UART, QSPI on wrapper 1 or wrapper 3 where wired, SDCC2/4, UFS including ICE, PCIe0/1 link training, and USB3 primary.
- Validate GDSC behavior through PCIe, UFS, and USB runtime PM plus suspend/resume, watching for domains losing votes in sleep.
- Test reset controls for QUP wrappers including wrapper 3, PCIe controllers/PHYs, UFS, USB/DP PHYs, SDCC, camera/display/GPU/video, and video AXI ARES.
- Confirm low-power behavior with AO GPLLs and the cleared GDSC sleep-vote register by running suspend/resume and checking clocks needed for wake or retention remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm8650.c -->
