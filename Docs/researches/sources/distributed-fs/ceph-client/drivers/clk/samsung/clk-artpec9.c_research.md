# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-artpec9.c

## Purpose

`clk-artpec9.c` provides the ARTPEC-9 SoC clock topology for the Linux common clock framework using Samsung's clock description macros and arm64 Exynos CMU registration helpers. It defines descriptors for `CMU_CMU`, `CMU_BUS`, `CMU_CORE`, `CMU_CPUCL`, `CMU_FSYS0`, `CMU_FSYS1`, `CMU_IMEM`, and `CMU_PERI`, then binds them to Axis ARTPEC-9 device-tree compatible strings.

ARTPEC-9 expands the ARTPEC-8 style with split FSYS0/FSYS1 domains, two CPUCL PLLs for CPU and SCU paths, newer fractional PLL types, and many boot-critical PCIe, USB, UART, I3C, MMU/Q-channel, and timer gates.

## Important APIs, types, and functions

- Clock arrays are built with `PLL()`, `MUX()`, `nMUX()`, `MUX_F()`, `DIV()`, `DIV_F()`, `FFACTOR()`, and `GATE()`.
- `artpec9_pll_audio_rates`, `artpec9_pll_cpucl_rates`, and `artpec9_pll_fsys1_rates` define explicit PLL rate tables. The CPUCL table is documented as requiring descending order.
- `struct samsung_cmu_info` objects collect per-domain PLL, mux, divider, fixed-factor, gate, register-list, and clock-ID metadata.
- `artpec9_cmu_imem_init()` registers IMEM early through `exynos_arm64_register_cmu(NULL, np, &cmu_imem_info)` and `CLK_OF_DECLARE()`.
- `artpec9_cmu_probe()` handles platform-driven domains by calling `exynos_arm64_register_cmu(dev, dev->of_node, info)`.
- `artpec9_cmu_init()` registers the `artpec9-cmu` platform driver at `core_initcall()`.

## Control flow and integration

IMEM is initialized through early OF clock declaration, while the other CMUs bind through the platform driver. Each platform probe obtains the `samsung_cmu_info` pointer from match data and delegates register setup and provider registration to the common arm64 helper.

`CMU_CMU` is the root distribution domain. It declares shared/audio PLLs, shared divider outputs, and `dout_clkcmu_*` clocks for bus, core, CPUCL switch, FSYS0/FSYS1, GPU, IMEM, MIF, PERI, RSP, TRFM, VIO, VIP, and VPP. Several parent arrays reference `mout_clk_pll_fsys1` or `fout_pll_fsys1`, making FSYS1 PLL a source for multiple branches.

`CMU_CPUCL` has two PLLs, `fout_pll0_cpucl` and `fout_pll1_cpucl`, with mux/divider paths for CPU and SCU clocks. CPU cluster, GIC, PCLK, ATCLK, CMUREF, debug, shortstop, and CoreSight clocks are exposed, with CPU/debug gates marked critical. `CMU_FSYS0` covers Ethernet, I3C, MMC, QSPI, ADC, PWM, and NAND clocks. `CMU_FSYS1` covers FSYS1 PLL, UART0, PCIe, USB, XHB, TZC400, and MMU TBU gates. `CMU_PERI` covers DSIM, I3C2/I3C3, I2C, SPI, UART1, and UART2.

## State and persistence behavior

Runtime state is held mainly in hardware registers described by the `*_clk_regs` arrays and in common clock framework registrations. The static arrays are `__initconst`; after registration, CCF owns the `clk_hw` state and register contents persist in hardware. The file does not define suspend/resume callbacks or use `exynos_arm64_register_cmu_pm()`, so local save/restore is absent.

## Dependencies

Dependencies include `dt-bindings/clock/axis,artpec9-clk.h`, Samsung `clk.h` macros, `clk-exynos-arm64.h`, CCF provider APIs, platform-device probing, and correct DT compatible/reg/parent-clock data. Parent-name consistency across `CMU_CMU`, `CMU_FSYS1`, and downstream domains is especially important.

## Risks and edge cases

- Binding ID maxima and `*_NR_CLK` constants must remain synchronized.
- String parent names and cross-domain registration order are critical, especially for FSYS1-derived parent paths.
- CPUCL PLL rates must stay descending.
- Heavy `CLK_IS_CRITICAL` use protects boot but can hide missing consumers.
- IMEM's early registration model may need rework if it gains dependencies requiring a `struct device`.
- Register offset or gate bit mistakes usually surface only on ARTPEC-9 hardware.

## Test signals

Validation should include build and binding checks, ARTPEC-9 boot without clock registration errors, complete `clk_summary` coverage for all eight domains, and working UART, timers/MCT, thermal, MMC/QSPI, Ethernet, PCIe, USB, I3C/I2C/SPI, and DSIM clocks after unused-clock cleanup. CPU/SCU rate tests should exercise the CPUCL PLL table, and PCIe/USB/Ethernet tests should cover FSYS0/FSYS1 split parentage.
