# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-mdm9607.c

## Purpose
This file is the Qualcomm GCC driver for the MDM9607 modem SoC compatible string `qcom,gcc-mdm9607`. It registers the SoC's PLLs, root clock generators, branch gates, and a small reset map through the Qualcomm common clock-controller layer. The hardware described here covers XO/sleep parents, GPLL/BIMC PLLs, BLSP serial controllers, crypto, GP clocks, PDM, SDCC, APSS/TCU, USB HS/HSIC, MSS, SMMU, QDSS, and core NOC/APSS bus clocks.

## Important APIs, Types, And Functions
- `enum { P_XO, P_BIMC, P_GPLL0, P_GPLL1, P_GPLL2, P_SLEEP_CLK }` defines internal parent IDs used by parent maps and frequency tables.
- `gpll0_early` and `gpll2_early` are `clk_alpha_pll` objects with post-divided `gpll0` and `gpll2` outputs. `gpll1` and `bimc_pll` are classic `clk_pll` objects with `clk_regmap` vote wrappers.
- Parent maps cover XO/GPLL0, XO/GPLL0/GPLL1/sleep, XO/GPLL0/GPLL2, XO/GPLL0/GPLL1/GPLL2, and XO/GPLL0/BIMC.
- `clk_rcg2` roots define rates for APSS AHB, PCNOC/system NOC, six BLSP I2C/SPI/UART sources, crypto, GP1-3, PDM2, SDCC1/2, APSS TCU, USB HS system, USB HSIC, HSIC IO calibration, and HSIC system clocks.
- `clk_branch` objects expose the actual gateable clocks, usually pointing at one RCG or NOC parent and using `clk_branch2_ops`.
- `gcc_mdm9607_clocks[]` maps every binding ID from `dt-bindings/clock/qcom,gcc-mdm9607.h` to its `struct clk_regmap`.
- `gcc_mdm9607_resets[]` maps USB HS/HSIC, MSS restart, USB2 PHY-only, and QUSB2 PHY resets.
- `gcc_mdm9607_probe()` explicitly maps the controller, votes GPLL0 on with `regmap_update_bits(regmap, 0x45000, BIT(0), BIT(0))`, then calls `qcom_cc_really_probe()`.

## Control Flow
`gcc_mdm9607_init()` is registered with `core_initcall`, so this controller is registered early. When a matching platform device appears, `gcc_mdm9607_probe()` calls `qcom_cc_map()` to obtain the regmap for the GCC MMIO block. If mapping fails, the probe returns the error. Otherwise, it sets the GPLL0 vote bit because acpuclock requires GPLL0 enabled, then hands the regmap and descriptor to `qcom_cc_really_probe()` to register clocks and resets.

After probe, all rate changes, parent selection, enables, disables, and reset operations are performed through common clk/reset callbacks. The local file has no per-request logic once registration succeeds.

## State And Persistence
The driver's software data is static and read-only after registration. Persistent hardware state is limited to GCC registers: PLL votes, PLL programming, RCG source/divider/M/N configuration, branch enables, halt status, and reset bits. The explicit GPLL0 vote modifies the hardware vote register during probe and may keep GPLL0 active for CPU clock consumers. No state is stored in files, firmware variables, or dynamically allocated driver-private structures.

## Dependencies And Integration Points
- Linux common clk framework, platform driver core, regmap, reset controller, and device tree matching.
- Qualcomm common clock infrastructure: `common.h`, `clk-regmap.h`, `clk-alpha-pll.h`, `clk-pll.h`, `clk-rcg.h`, `clk-branch.h`, `reset.h`, and `gdsc.h` headers. This driver includes `gdsc.h` but does not register GDSCs.
- Binding IDs from `dt-bindings/clock/qcom,gcc-mdm9607.h` must align with `gcc_mdm9607_clocks[]` and `gcc_mdm9607_resets[]`.
- Device tree must provide firmware-named parents `xo` and `sleep_clk`.
- Consumers include BLSP I2C/SPI/UART controllers, crypto engine, SDCC controllers, USB HS/HSIC blocks, APSS/TCU, MSS, SMMU, QDSS DAP, PDM, PRNG, and bus fabric.
- The special GPLL0 vote is an integration contract with the CPU clock path (`acpuclock`) and should be considered when changing probe order or PLL handling.

## Risks And Edge Cases
- Incorrect binding indices or array placement can miswire clocks and resets for many consumers.
- The GPLL2 enable mask comment notes that it uses `BIT(3)` rather than the expected bit 2. Changing this to look "regular" would likely break the hardware vote.
- The probe-time GPLL0 vote is mandatory for acpuclock. If removed or delayed, CPU clock initialization can fail or run from an unintended source.
- Several branches omit explicit halt checks or use `BRANCH_HALT_VOTED`; mismatches between hardware behavior and the chosen check can cause false timeouts or hidden failures.
- Fractional dividers in SDCC, USB, PDM, and UART tables use non-integer divisors encoded through the `F()` macro. Rate-table changes need hardware-validation, especially for storage and USB tolerance.
- `bimc_ddr_clk_src` uses `CLK_GET_RATE_NOCACHE`; stale rate assumptions from consumers or tests can mask real parent changes.
- This driver is early-registered with `core_initcall`; dependencies on parent clocks and DT names must be available early enough.

## Test Signals
- Build the driver with MDM9607 DT bindings and Qualcomm clock helpers.
- Boot a board or test DT containing `qcom,gcc-mdm9607` and verify early probe success plus absence of `qcom_cc_map()` or clock-registration errors.
- Confirm GPLL0 vote bit behavior and CPU/acpuclock initialization.
- Use debugfs clk summaries to verify XO/sleep parents, GPLL0/GPLL1/GPLL2/BIMC parents, BLSP serial rates, SDCC rates, USB HS/HSIC rates, and APSS/TCU rates.
- Exercise BLSP UART/I2C/SPI instances 1-6, SDCC1/2, USB HS and HSIC paths, crypto, PRNG, and modem/APSS bus consumers.
- Assert and deassert listed resets via consumers or reset-controller tests, especially USB and MSS restart.
- Run suspend/resume or runtime PM smoke tests to catch always-on/voted clock and NOC dependency regressions.
