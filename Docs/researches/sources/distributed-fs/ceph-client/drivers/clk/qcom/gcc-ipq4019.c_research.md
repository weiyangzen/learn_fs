# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-ipq4019.c

## Purpose

`gcc-ipq4019.c` is the Qualcomm Global Clock Controller driver for IPQ4019-class SoCs. It registers the GCC clock tree and reset lines used by APSS, PCNOC, BLSP, SDCC, PCIe, USB, ESS, crypto, audio, QPIC, IMEM, and 2.4/5 GHz WCSS blocks. The file is older than the alpha-PLL based IPQ5018/IPQ5210 drivers and carries custom FEPLL/divider logic for the APSS CPU PLL and fixed FEPLL outputs.

The exported ABI is the device-tree clock and reset provider described by `dt-bindings/clock/qcom,gcc-ipq4019.h`. Consumers request IDs from `gcc_ipq4019_clocks[]` and `gcc_ipq4019_resets[]`; no public C functions are exported.

## Important APIs, Types, And Functions

The driver depends on the common qcom clock framework: `qcom_cc_probe()`, `struct qcom_cc_desc`, `struct clk_regmap`, `struct clk_rcg2`, `struct clk_branch`, `struct qcom_reset_map`, `clk_rcg2_ops`, `clk_rcg2_floor_ops` where applicable, `clk_branch2_ops`, and `clk_regmap_div` helpers.

Two local data types model the FEPLL hardware:

- `struct clk_fepll_vco` describes feedback-divider and reference-divider bitfields in a PLL_DIV register.
- `struct clk_fepll` wraps a `clk_regmap_div` with optional fixed divider, divider table, frequency table, and VCO descriptor.

The custom operations are central:

- `clk_fepll_vco_calc_rate()` reads the PLL divider register through regmap and calculates `parent / refclkdiv * 2 * fdbkdiv`.
- `clk_cpu_div_determine_rate()` maps requested APSS CPU rates through `ftbl_apss_ddr_pll[]` and selects the parent.
- `clk_cpu_div_set_rate()` writes the APSS CPU divider field and waits with `udelay(1)` because the hardware has no completion bit.
- `clk_cpu_div_recalc_rate()` handles the APSS nonlinear divider encoding, including half-step values encoded above 10.
- `clk_regmap_clk_div_recalc_rate()` provides fixed or table-driven FEPLL-derived rates.
- `gcc_ipq4019_cpu_clk_notifier_fn()` moves `apps_clk_src` to a safe FEPLL500 parent before APSS rate changes.

## Clock And Reset Model

The root parent set is small: XO, FEPLL200, FEPLL500, DDRPLL-derived SDCC/APSS outputs, WCSS FEPLL divided outputs, and FEPLL125DLY. The file defines fixed FEPLL outputs such as `fepll125`, `fepll200`, `fepll500`, APSS DDR PLL dividers for CPU and SDCC, and table-backed WCSS 2G/5G dividers.

RCG sources cover PCNOC AHB, audio PWM, BLSP I2C/SPI/UART, GP1-GP3, SDCC1 apps, APSS apps and APSS AHB, FEPHY delay, USB mock UTMI, and WCSS 2G/5G. Branch clocks gate the corresponding peripherals and bus paths. Several branches use `BRANCH_HALT_VOTED`, meaning enable state is controlled through shared vote registers such as `0x6000`; others use direct branch registers and normal halt polling.

`pcnoc_clk_src` is marked `CLK_IS_CRITICAL`, reflecting that the peripheral NoC clock must stay alive for system access. Many consumer-visible clocks use `CLK_SET_RATE_PARENT`, allowing device drivers to propagate rate requests up to their source clock.

The reset map includes WiFi0/WiFi1 cold/warm/radio resets, USB2/USB3 PHY resets, PCIe reset groups, ESS/MAC resets, subsystem BCRs, NoC timeout BCRs, BLSP, crypto, SDCC, QPIC, TLMM, SPDM, MPM, and related hardware reset lines. Reset entries are simple register/bit mappings; the common reset controller implements assertion and deassertion.

## Control Flow

At boot, `core_initcall(gcc_ipq4019_init)` registers a platform driver named `qcom,gcc-ipq4019`. Device-tree matching uses compatible `qcom,gcc-ipq4019`.

`gcc_ipq4019_probe()` calls `qcom_cc_probe(pdev, &gcc_ipq4019_desc)`. The common qcom code maps the MMIO region using `gcc_ipq4019_regmap_config`, initializes the listed `clk_regmap` entries, and registers reset controls. After successful clock-controller registration, the probe registers `gcc_ipq4019_cpu_clk_notifier` against `apps_clk_src.clkr.hw.clk`.

Normal runtime operations are driven by Linux CCF consumers. Rate changes call through `clk_rcg2_ops` or the custom FEPLL CPU divider ops. Branch enables update hardware enable bits and wait according to each branch halt policy. APSS rate changes are special: before the rate change, the notifier forces the APSS source parent to safe parent index 2, which the file documents as FEPLL500 in `gcc_xo_ddr_500_200`.

## State And Persistence

All meaningful state is hardware register state accessed through regmap. There is no file-backed persistence, heap-owned persistent state, or runtime cache beyond static clock descriptor objects and common CCF registration structures. Divider values, parent selections, branch enables, and reset assertions persist only as long as the GCC hardware and power domain retain registers.

The custom FEPLL code reads live VCO fields instead of caching them. The APSS divider set path writes a divider field and uses a fixed microsecond delay because the hardware exposes no completion status. That makes bootloader-programmed PLL values and current hardware state important inputs to recalc behavior.

## Dependencies And Integration Points

The driver relies on Linux platform-device probing, device tree, CCF, regmap, qcom common clock/reset helpers, and dt-binding ID stability. It includes `linux/clk.h` for notifier registration and parent switching. Integration consumers include APSS CPU frequency code, BLSP serial/I2C/SPI controllers, SDHCI, USB, PCIe, crypto, ESS Ethernet switch, WiFi/WCSS blocks, and reset-controller clients.

## Risks

The main risk is register-description accuracy. Parent maps, source-selection values, M/N/D values, divider encodings, and reset bits must match the IPQ4019 GCC hardware manual and dt bindings. A one-entry error can silently produce bad peripheral rates or gate the wrong domain.

The FEPLL VCO calculation divides by `refclkdiv` read from hardware. If hardware or boot firmware leaves a zero divider, the code has no explicit guard. This is usually prevented by valid silicon initialization, but it is still a hardware-state dependency. APSS rate changes also depend on the safe parent index staying aligned with `gcc_xo_ddr_500_200`; a parent-list reorder without updating `gcc_ipq4019_cpu_safe_parent` would be dangerous.

The custom APSS divider path lacks status polling and depends on `udelay(1)`. If a future SoC revision needs longer settling or exposes a real status bit, this code would need adjustment. Critical/voted clocks should be treated carefully because incorrect halt policy can cause false timeout warnings or shut down shared infrastructure.

## Test Signals

Build-level signals are successful compilation with the IPQ4019 dt-binding header and no sparse/Coccinelle issues around static initializers. Boot-level signals are a clean probe for `qcom,gcc-ipq4019`, no CCF duplicate-name warnings, no branch halt timeout messages, and a populated `/sys/kernel/debug/clk/clk_summary` containing APSS, PCNOC, BLSP, USB, PCIe, WCSS, ESS, and SDCC clocks.

Functional signals include serial console stability through BLSP UART rates, SDCC1 frequency changes including 400 kHz and high-speed modes, USB2/USB3 enumeration, PCIe link bring-up, ESS/WCSS resets working for network devices, and cpufreq/APSS rate changes completing without lockups. Reset testing should assert/deassert representative USB, PCIe, WiFi, and ESS reset IDs and verify the target hardware recovers.
