# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-mdm9615.c

## Purpose
This file is the Qualcomm GCC driver for the MDM9615 modem SoC compatible string `qcom,gcc-mdm9615`. It describes an older GCC block using classic PLLs, voted PLL wrappers, legacy `clk_rcg` roots, branch gates, and reset maps. It exposes clocks for GSBI UART/QUP blocks, GP clocks, PMEM, PRNG, SDC, USB HS/HSIC, crypto engine, BAM/DMA, PMIC/RPM, EBI2, and related AHB/H clocks.

## Important APIs, Types, And Functions
- Device-tree parent indices include `DT_CXO` and `DT_PLL4`. Internal parent IDs are `P_CXO`, `P_PLL8`, and `P_PLL14`.
- PLL definitions include `pll0`, external/voted `pll4_vote`, `pll8`, and `pll14`, with vote wrappers using `clk_pll_vote_ops`.
- Parent maps `gcc_cxo_map`, `gcc_cxo_pll8_map`, and `gcc_cxo_pll14_map` drive RCG source selection.
- Legacy `struct clk_rcg` roots describe GSBI UART sources, GSBI QUP sources, GP0-2 sources, PRNG source, SDC1/2 sources, USB HS1 and HSIC sources. These use explicit NS/MD registers and `mn`, `p`, and `s` bitfield layouts rather than the newer `clk_rcg2` shape.
- `struct clk_branch` entries gate each source or bus clock and include halt registers/bits, hardware clock gating fields, and flags such as `CLK_SET_RATE_PARENT`, `CLK_SET_PARENT_GATE`, `CLK_SET_RATE_GATE`, and `CLK_IGNORE_UNUSED`.
- `gcc_mdm9615_clks[]` maps binding constants from `dt-bindings/clock/qcom,gcc-mdm9615.h` to the static clock objects.
- `gcc_mdm9615_resets[]` maps reset constants from `dt-bindings/reset/qcom,gcc-mdm9615.h` to register offsets and optional bits.
- `gcc_mdm9615_probe()` maps the MMIO block through `qcom_cc_map()` and registers the descriptor with `qcom_cc_really_probe()`.

## Control Flow
The module registers its platform driver at `core_initcall` time. A device-tree node matching `qcom,gcc-mdm9615` invokes `gcc_mdm9615_probe()`. Probe maps the controller register window using `gcc_mdm9615_regmap_config`, returns the mapping error if present, and otherwise calls `qcom_cc_really_probe()` to register clocks and resets. Runtime control is then fully delegated to the common clk and reset frameworks.

There is no local clock policy beyond the static descriptors. The one notable static policy is `CLK_IGNORE_UNUSED` on `usb_hs1_system_clk`, keeping that USB system clock from being disabled by the common unused-clock cleanup.

## State And Persistence
The file maintains no dynamic driver-private state. Hardware state lives in MMIO registers for PLL enables/votes, RCG source and M/N programming, branch gates, halt status, hardware clock gating, and reset bits. The static tables are compiled into the driver and do not persist user or runtime choices. Register state is lost across hardware reset or power loss.

## Dependencies And Integration Points
- Linux platform driver, device tree, regmap, reset controller, and common clk frameworks.
- Qualcomm helpers from `common.h`, `clk-regmap.h`, `clk-pll.h`, `clk-rcg.h`, `clk-branch.h`, and `reset.h`.
- Clock binding constants in `dt-bindings/clock/qcom,gcc-mdm9615.h` and reset constants in `dt-bindings/reset/qcom,gcc-mdm9615.h`.
- Device tree must provide `DT_CXO` as `cxo_board` and `DT_PLL4` as `pll4`; the driver also registers/votes PLL0/PLL8/PLL14 internally.
- Consumers include GSBI UART/QUP devices, SDC1/2, USB HS1/HSIC, PRNG, CE1, DMA BAM, PMIC arbiter/SSBI, RPM message RAM, EBI2, ADM, and bus/peripheral H clocks.
- The `MODULE_ALIAS("platform:gcc-mdm9615")` supports platform module alias matching in addition to OF matching.

## Risks And Edge Cases
- This is a legacy RCG layout with hand-coded NS/MD bitfields. Mistakes in `mn`, `p`, or `s` shifts and widths can produce wrong rates even when the clock registers successfully.
- Parent mapping values are sparse (`P_PLL8` selector 3, `P_PLL14` selector 4). Normalizing these values would break hardware source selection.
- `pll4_vote` is an external parent indexed from DT rather than a locally defined PLL. Missing or misordered DT parents can break clocks that depend on it.
- Branch halt registers share status words with different bits. A wrong halt bit can produce false-positive enable success or timeout.
- `usb_hs1_system_clk` is marked `CLK_IGNORE_UNUSED`; removing that can let common clk disable a clock required by USB hardware.
- Some branches use hardware clock gating bits and combined enable masks, for example PMEM, BAM, EBI2, and GSBI H clocks. Incorrect masks can enable only part of a functional path.
- Reset offsets include both whole-register and bit-specific resets. Incorrect bit use may reset wider hardware than intended.

## Test Signals
- Build with the MDM9615 clock and reset bindings.
- Boot with a `qcom,gcc-mdm9615` node and verify `qcom_cc_really_probe()` succeeds.
- Inspect debugfs clock summaries for PLL0/PLL4/PLL8/PLL14 votes, GSBI UART/QUP source rates, SDC rates, USB HS/HSIC rates, and branch enable states.
- Exercise GSBI UART and QUP instances 1-5, SDC1/2, USB HS1, USB HSIC, PRNG, CE1, DMA BAM, PMIC arbiter, RPM message RAM, and EBI2 consumers.
- Verify reset-controller behavior for DMA BAM, CE1, SDC, ADM, USB, GSBI, and PDM resets.
- Run unused-clock cleanup and suspend/resume tests to confirm `CLK_IGNORE_UNUSED`, voted PLLs, and hardware-gated branches do not regress device availability.
