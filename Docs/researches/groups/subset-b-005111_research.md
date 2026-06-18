# Research: subset-b-005111

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear1310.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear1310.c

## Purpose
This file is the SPEAr1310 SoC-specific pinmux table for the shared SPEAr pinctrl core. It describes pins 0 through 245, all SPEAr1310 muxable peripheral groups, the function-to-group map exported to the pinctrl subsystem, and GPIO fallback mux records used when selected pins are requested as GPIOs.

## Important APIs, Types, And Data
- `spear1310_pins[]` combines `SPEAR_PIN_0_TO_101` and `SPEAR_PIN_102_TO_245`.
- Register constants cover `PERIP_CFG`, `PCIE_SATA_CFG`, `PAD_FUNCTION_EN_0..2`, and `PAD_DIRECTION_SEL_0..2`.
- `struct spear_muxreg`, `struct spear_modemux`, `struct spear_pingroup`, and `struct spear_function` tables encode all hardware behavior.
- Major functions include `i2c0`, `ssp0`, `i2s0`, `i2s1`, `clcd`, `arm_gpio`, `smi`, `gmii`, `rgmii`, `smii_0_1_2`, `nand`, `keyboard`, `uart0`, `gpt0`, `gpt1`, `sdhci`, `cf`, `xd`, `uart1`, `uart2_3`, `uart4`, `uart5`, `i2c_1_2`, `i2c3_i2s1`, `i2c_4_5`, `i2c_6_7`, `can0`, `can1`, `pci`, `pci_express`, `sata`, `ssp1`, and `gpt64`.
- `DEFINE_2_MUXREG()` and `GPIO_PINGROUP()` build per-pin GPIO reclaim mappings for many muxed pads.
- `spear1310_machdata` is the final descriptor consumed by `spear_pinctrl_probe()`.

## Control Flow And Integration
The platform driver matches `st,spear1310-pinmux`. Probe is intentionally simple: `spear1310_pinctrl_probe()` passes the static `spear1310_machdata` to `spear_pinctrl_probe()`. The shared SPEAr core performs DT parsing, pinctrl registration, function selection, register updates through regmap, and GPIO handoff behavior.

Most groups program both a pad function-enable register and a direction-select register. Storage/media functions add extra selector writes: `sdhci`, `cf`, and `xd` share the `MCIF_MUXREG` sequence and then set `PERIP_CFG` to SD, CompactFlash, or XD mode. PCIe and SATA groups have no pin list and instead program fixed lane/clock/reset bits in `PCIE_SATA_CFG`. Ethernet variants select large shared pin ranges and either assert GMII bits or clear overlapping RGMII/SMII masks to route alternate wiring.

## State And Persistence
The file itself contains static tables and no mutable runtime state beyond platform-driver registration. Persistent hardware state is the set of MMIO register fields written by the common SPEAr core: pad function bits, direction-select bits, MCIF media selection, and PCIe/SATA lane configuration. GPIO persistence is represented by `spear1310_gpio_pingroup[]`, which tells the core which mux bits to clear/set when GPIO consumers request those pads.

## Dependencies
It depends on Linux platform/OF/init headers and local `pinctrl-spear.h` definitions. It depends behaviorally on the common SPEAr core honoring multi-register `spear_modemux` entries and on the pin names and macro ranges in `pinctrl-spear.h`.

## Risks And Review Notes
- Table consistency is the main risk. Pin arrays, group names, function group strings, and GPIO fallback entries must stay synchronized.
- Register masks often combine unrelated shared pins. A wrong value can disable boot-critical NAND, SD/MMC, GMII/RGMII, PCI, PCIe, or SATA routing.
- The `i2c3_unction` C identifier appears misspelled, although the function table still references it and the exported function name is `i2c3_i2s1`.
- Several muxes intentionally clear function bits to select alternate signals. These entries are easy to misread because `val = 0` can be the active peripheral selection, not GPIO.
- PCIe/SATA groups have no pins; consumers and debug tooling may show function selection as register-side configuration rather than a visible pin group.

## Test Signals
Build with the SPEAr pinctrl configuration and `W=1` to catch array/prototype drift. Boot a SPEAr1310 DT using `st,spear1310-pinmux` and verify pinctrl debugfs lists all groups/functions. Exercise representative states for NAND, SDHCI, CF/XD, UART/I2C alternate groups, GMII/RGMII/SMII, PCI, PCIe, SATA, and GPIO requests on muxed pads. Hardware register readback should confirm both `PAD_FUNCTION_EN_*` and `PAD_DIRECTION_SEL_*` fields change together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear1310.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear1340.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear1340.c

## Purpose
This file defines the SPEAr1340 pin controller description. SPEAr1340 has pins 0 through 251 and a two-level mux model: first pads are enabled as GPIO or peripheral, then shared peripheral pads select primary versus alternate IP. The file encodes those choices as static SPEAr pinctrl tables and registers a platform driver for `st,spear1340-pinmux`.

## Important APIs, Types, And Data
- `spear1340_pins[]` extends the common SPEAr pin ranges with PLGPIO246..251.
- First-level pad control uses `PAD_FUNCTION_EN_1..8`.
- Second-level shared-IP control uses `PAD_SHARED_IP_EN_1..2`.
- Sideband configuration registers include `PERIP_CFG`, `GMAC_CLK_CFG`, and `PCIE_SATA_CFG`.
- `pads_as_gpio` clears pad function enables to override bootloader state.
- Major functions include `fsmc`, `keyboard`, `spdif_in`, `spdif_out`, `gpt_0_1`, `pwm`, `vip`, `cam0..cam3`, `smi`, `ssp0`, `uart0`, `uart1`, `i2s`, `gmac`, `i2c0`, `i2c1`, `cec0`, `cec1`, `sdhci`, `cf`, `xd`, `clcd`, `arm_trace`, `miphy_dbg`, `pcie`, and `sata`.
- `gpio_request_endisable()` is a SoC callback that dynamically clears or sets the relevant `PAD_FUNCTION_EN_*` bit for GPIO request/release.

## Control Flow And Integration
Probe calls the shared `spear_pinctrl_probe()` with `spear1340_machdata`. During mux selection the common core walks each selected group's `spear_modemux` list and writes the specified register/mask/value triples. Many groups write both first-level pad enable registers and second-level shared-IP selectors. GMAC groups share the `GMAC_MUXREG` pad enable sequence, then select GMII, RGMII, RMII, or SGMII in `GMAC_CLK_CFG`. SDHCI, CF, and XD share MCIF pad enables and select the media mode in `PERIP_CFG`. PCIe and SATA select mutually exclusive lane mode and clocks/resets in `PCIE_SATA_CFG`.

## State And Persistence
Runtime state is held by the common SPEAr core. This file's persistent hardware impact is the programmed pad function state, shared-IP selections, GMAC mode bits, MCIF mode bits, SPDIF output enable, CLCD sleep/active pin state, and PCIe/SATA lane configuration. GPIO request persistence is mediated by `gpio_request_endisable()`, which computes the pad enable register from the pin number and toggles one bit.

## Dependencies
It depends on Linux platform/OF/init headers and local `pinctrl-spear.h`. It assumes the common SPEAr core supports the optional `gpio_request_endisable` hook and multi-register mux sequences.

## Risks And Review Notes
- The two-level mux model requires correct ordering and polarity. Some alternate functions are selected by writing zero to `PAD_SHARED_IP_EN_*`; others are selected by setting bits.
- `gpio_request_endisable()` uses `sizeof(int *)` as the register stride. This works only if it matches the intended 4-byte register spacing on all target builds; it is a notable review point.
- `pads_as_gpio` touches all pad-function enable registers and can override bootloader mux defaults. It must be used deliberately by DT states.
- `clcd_sleep_grp` intentionally disables CLCD output to avoid panel damage; display suspend/resume should validate this state.
- GMAC, MCIF, and PCIe/SATA sideband registers configure more than pin routing and can affect clocks, reset, and peripheral mode.

## Test Signals
Run build coverage for SPEAr1340 and boot with `st,spear1340-pinmux`. Use debugfs to confirm all groups/functions are registered. Test GPIO request/release on peripheral-capable pads, GMAC in all declared interface modes, SDHCI/CF/XD media selection, SPDIF out enable, CLCD active and sleep states, camera/VIP exclusivity, and PCIe versus SATA lane selection. Register readback should include both `PAD_FUNCTION_EN_*` and `PAD_SHARED_IP_EN_*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear1340.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear300.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear300.c

## Purpose
This file is the SPEAr300-specific overlay on top of the common SPEAr3xx pinmux tables. It adds SPEAr300 board/application modes, extra peripheral groups, and the `st,spear300-pinmux` platform driver.

## Important APIs, Types, And Data
- `PMX_CONFIG_REG` is the main mux register and `MODE_CONFIG_REG` selects one of the SPEAr300 mode encodings.
- `struct spear_pmx_mode` instances map mode names such as NAND, NOR, photo frame, IP phone, WiFi phone, ATA/PABX, and camera/LCD modes to 4-bit mode values.
- SPEAr300-specific functions include `fsmc`, `clcd`, `tdm`, `i2c1`, `cam`, `dac`, `i2s`, `sdhci`, and `gpio1`, in addition to `SPEAR3XX_COMMON_FUNCTIONS`.
- Each group has one or more `spear_modemux` entries with `.modes` masks so the common core can apply only the register writes valid for the active SoC mode.

## Control Flow And Integration
Probe fills the shared `spear3xx_machdata` with SPEAr300 group/function arrays, disables `gpio_pingroups`, enables mode support, attaches `spear300_pmx_modes`, initializes common group register addresses to `PMX_CONFIG_REG`, and delegates to `spear_pinctrl_probe()`.

Mux selection is mode-sensitive. For example, FSMC chip-select groups are available in NAND/NOR/photo-frame/ATA modes, CLCD groups differ between LCD and photo-frame modes, and camera, I2S, DAC, SDHCI, and GPIO1 groups are enabled only in selected mode combinations. Most SPEAr300 alternate functions are selected by clearing bits in `PMX_CONFIG_REG` that the common SPEAr3xx table otherwise uses for base functions.

## State And Persistence
Static tables are immutable. Hardware state persists in `PMX_CONFIG_REG` and `MODE_CONFIG_REG` after the common core writes the selected mode and pin group mux values. Unlike SPEAr310/320, this probe clears `gpio_pingroups`, so this file does not expose the common 3xx GPIO fallback table through `spear3xx_machdata`.

## Dependencies
It depends on `pinctrl-spear3xx.h` for common pins, groups, functions, mux masks, and shared `spear3xx_machdata`. It relies on `pmx_init_addr()` to rewrite common group mux register placeholders and on the common core to interpret `.modes`.

## Risks And Review Notes
- The group name `i2c_clk_grp_grp` does not match the function group string `i2c_clk_grp`; this looks like a functional lookup risk.
- Mode masks are dense and overlapping. A missing mode bit can make a valid board mode unable to select its peripheral pins.
- Many groups actively clear common 3xx mux bits; this can conflict with common functions if DT selects incompatible states.
- Because `gpio_pingroups` is set to `NULL`, GPIO fallback behavior differs from the other SPEAr3xx variants.

## Test Signals
Build SPEAr300 support and boot a DT with `st,spear300-pinmux`. Validate that the configured mode is written to `MODE_CONFIG_REG`, all expected groups appear in debugfs, and DT states for FSMC, CLCD, TDM, camera, I2S, DAC, SDHCI, and GPIO1 resolve. A targeted test should check the suspected `i2c1` group-name mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear310.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear310.c

## Purpose
This file is the SPEAr310-specific overlay for the common SPEAr3xx pinmux definitions. It adds extra UART, EMI, FSMC, RS485, and TDM functions, initializes common mux register placeholders to the SPEAr310 register offset, and registers `st,spear310-pinmux`.

## Important APIs, Types, And Data
- `PMX_CONFIG_REG` is `0x08`.
- SPEAr310-specific groups include `emi_cs_0_to_5`, `uart1` through `uart5`, `fsmc`, `rs485_0`, `rs485_1`, and `tdm`.
- `spear310_pingroups[]` prepends `SPEAR3XX_COMMON_PINGROUPS` and then adds SPEAr310-specific groups.
- `spear310_functions[]` similarly combines common functions and SPEAr310-specific functions.
- Probe uses `pmx_init_addr()` and `pmx_init_gpio_pingroup_addr()` to retarget common SPEAr3xx mux register placeholders to `PMX_CONFIG_REG`.

## Control Flow And Integration
The platform driver matches `st,spear310-pinmux`. Probe mutates the shared `spear3xx_machdata` by assigning SPEAr310 groups/functions, initializing mux register addresses, enabling common GPIO pingroup register addresses, setting `modes_supported = false`, and calling `spear_pinctrl_probe()`.

SPEAr310 has no separate mode table. Alternate functions are selected directly by clearing bits in `PMX_CONFIG_REG`: UART1 clears FIRDA, UART2 clears timer 0/1, UART3-5 share UART0 modem bits, FSMC clears SSP chip select bits, RS485/TDM clear MII bits, and EMI chip selects clear timer mux bits.

## State And Persistence
The file stores only static tables and modifies the process-global `spear3xx_machdata` during probe. Hardware state persists in `PMX_CONFIG_REG`. Common GPIO fallback behavior is enabled for the inherited SPEAr3xx groups after their register addresses are initialized.

## Dependencies
It depends on `pinctrl-spear3xx.h` and the common SPEAr pinctrl core. Because it edits shared `spear3xx_machdata`, it assumes each SPEAr3xx SoC driver is instantiated in a way that does not require multiple variants to coexist with independent machdata.

## Risks And Review Notes
- `rs485_0_grps[]` contains `"rs485_0"` while the declared group is `"rs485_0_grp"`; `rs485_1` has the same suffix mismatch. This can prevent those functions from resolving their groups.
- Multiple UART functions share the same `PMX_UART0_MODEM_MASK`; selecting one can exclude the others.
- This driver mutates shared common machdata at probe time. Cross-SoC coexistence is unlikely in real hardware, but it is a test isolation concern.
- No mode gating means invalid DT combinations rely entirely on pinctrl state selection and shared mask conflicts.

## Test Signals
Build and boot with `st,spear310-pinmux`. Confirm common and SPEAr310-specific functions appear in pinctrl debugfs. Apply DT states for UART1-5, EMI, FSMC, RS485, and TDM, and verify `PMX_CONFIG_REG` readback. Specifically test RS485 group lookup because the function group strings appear inconsistent with pingroup names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear310.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear320.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear320.c

## Purpose
This file defines the SPEAr320 pinmux variant. It extends the common SPEAr3xx tables with a large set of mode-aware and extended-mode pad selectors for CLCD, EMI/FSMC, SPP, SDHCI, I2S, UARTs, RS485, touchscreen, CAN, PWM, SSP, MII/RMII/SMII, and I2C functions.

## Important APIs, Types, And Data
- Main registers are `PMX_CONFIG_REG`, `MODE_CONFIG_REG`, and `MODE_EXT_CONFIG_REG`.
- `spear320_pmx_modes[]` describes `AUTO_NET_SMII`, `AUTO_NET_MII`, `AUTO_EXP`, `SMALL_PRINTERS`, and `EXTENDED` modes.
- Extended selector registers `IP_SEL_PAD_0_9_REG` through `IP_SEL_MIX_PAD_REG` encode per-pad 3-bit function choices and port selectors.
- `EXT_CTRL_REG` carries dynamic EMI/FSMC muxing, MII MDIO location, and MAC mode selections.
- The file uses arrays of pingroups for multi-location functions: UART3/4/5/6, UART1 modem, PWM0/1, PWM2, PWM3, SSP1/2, SDHCI card-detect alternatives, MII0/1 SMII/RMII variants, I2C1, and I2C2.
- Probe combines `SPEAR3XX_COMMON_PINGROUPS` and `SPEAR3XX_COMMON_FUNCTIONS` with SPEAr320-specific tables in shared `spear3xx_machdata`.

## Control Flow And Integration
The driver matches `st,spear320-pinmux`. Probe assigns SPEAr320 groups/functions into `spear3xx_machdata`, enables mode support, installs the mode table, retargets common mux register placeholders to `PMX_CONFIG_REG`, initializes common GPIO fallback registers, and calls `spear_pinctrl_probe()`.

Mux application is layered. In legacy modes, many groups clear common SPEAr3xx bits in `PMX_CONFIG_REG`. In `EXTENDED_MODE`, groups additionally write the `IP_SEL_PAD_*` registers and sometimes `IP_SEL_MIX_PAD_REG` port selectors. Network groups write `EXT_CTRL_REG` to select MII, RMII, SMII, MDIO location, and MAC modes. EMI and FSMC groups set `EMI_FSMC_DYNAMIC_MUX_MASK`.

## State And Persistence
Static tables are immutable, but probe mutates shared `spear3xx_machdata`. Hardware state persists across the main mux register, mode registers, extended selector registers, and `EXT_CTRL_REG`. Common 3xx GPIO fallback state is available through initialized `gpio_pingroups`.

## Dependencies
It depends on `pinctrl-spear3xx.h`, common 3xx group/function exports, and the shared SPEAr core's mode filtering. It assumes the core applies every modemux whose `.modes` intersects the active mode and can handle repeated groups with different pin alternatives.

## Risks And Review Notes
- The cross product of modes, common mux bits, extended selector fields, and port selector fields is high risk for subtle routing mistakes.
- Several groups require both a common mux clear and an extended selector write. Applying only one layer can leave pads in an incoherent state.
- `PMX_PL_*` masks and values are dense 3-bit fields. A shift or mask error can affect neighboring pads.
- Shared `spear3xx_machdata` mutation has the same isolation risk as SPEAr300/310.
- Network mode programming in `EXT_CTRL_REG` controls MAC interface mode, not just pad routing, so wrong DT states can break Ethernet.

## Test Signals
Build with SPEAr320 enabled and boot a DT containing `st,spear320-pinmux`. Validate each SoC mode and especially `EXTENDED_MODE`. Use debugfs to inspect all alternate-location groups. Hardware tests should cover SDHCI card-detect on pins 12 and 51, CLCD versus EMI/SPP overlap, UART3/4/5/6 alternate locations, PWM alternatives, SSP1/2 alternatives, I2C1/2 alternatives, RMII/SMII/MII modes, and GPIO fallback on common 3xx pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear320.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear3xx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear3xx.c

## Purpose
This file provides the shared SPEAr3xx pin definitions, common pin groups, common functions, and GPIO fallback mappings reused by SPEAr300, SPEAr310, and SPEAr320 variant drivers.

## Important APIs, Types, And Data
- `spear3xx_pins[]` publishes pins 0..101 using `SPEAR_PIN_0_TO_101`.
- Common groups include FIRDA, I2C0, SSP chip selects, SSP0, MII0, GPIO0 pins 0..5, UART0 modem, UART0, and timer groups.
- For each common group, a `struct spear_pingroup` describes pins and a `struct spear_function` maps the exported function name to group strings.
- Initial group mux registers use `.reg = -1`; variant drivers later call `pmx_init_addr()` to set the actual `PMX_CONFIG_REG`.
- `DEFINE_MUXREG()` and `GPIO_PINGROUP()` create GPIO fallback mux records for common groups.
- `spear3xx_machdata` contains common pins and common GPIO pingroups; variant drivers fill the groups/functions and mode data.

## Control Flow And Integration
This file has no platform driver. It is linked as shared data for SPEAr3xx variant drivers. At variant probe time, SPEAr300/310/320 set `spear3xx_machdata.groups`, `functions`, mode fields, and register offsets, then call `spear_pinctrl_probe()`. The common SPEAr core later consumes the group/function arrays for pinctrl operations and the GPIO pingroup array for GPIO request mux handling.

## State And Persistence
Static common tables are process-global and reused. The externally visible `spear3xx_machdata` is mutable because each variant probe completes it with SoC-specific arrays and register addresses. Hardware persistence is indirect: common groups program the variant's mux register once their `.reg` placeholders have been initialized.

## Dependencies
It depends on Linux pinctrl descriptors and local `pinctrl-spear3xx.h`/`pinctrl-spear.h` macros. It depends on variant drivers to finish machdata setup before registration.

## Risks And Review Notes
- Common data is mutable and shared; tests that instantiate multiple SPEAr3xx variants in one kernel lifetime should be careful.
- `.reg = -1` placeholders are invalid until `pmx_init_addr()` runs. Missing initialization would produce bad register writes.
- Function group matching is string-based; variant files must preserve exact common group names.
- Common GPIO fallback entries assume clearing a function bit returns the pad to GPIO. That polarity must remain valid for every variant that reuses them.

## Test Signals
Compile all SPEAr3xx variants. For each variant, confirm common groups and functions are registered and that register addresses in common mux entries are updated to the SoC-specific `PMX_CONFIG_REG`. Exercise common functions FIRDA, I2C0, SSP0, MII0, UART0, timers, and GPIO request paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear3xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear3xx.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear3xx.h

## Purpose
This header is the shared declaration layer for SPEAr3xx pinmux variants. It defines common mux bit masks, declares the common groups/functions exported by `pinctrl-spear3xx.c`, provides aggregate macros for variant group/function arrays, and exposes the shared `spear3xx_machdata`.

## Important APIs, Types, And Data
- `PMX_*_MASK` constants define bit positions in the SPEAr3xx mux control register for PWM, FIRDA, I2C, SSP, MII, GPIO0 pins, UART0, and timers.
- `SPEAR3XX_COMMON_PINGROUPS` expands to pointers to all common `struct spear_pingroup` objects.
- `SPEAR3XX_COMMON_FUNCTIONS` expands to pointers to all common `struct spear_function` objects.
- Extern declarations allow variant files to compose common and SoC-specific tables without duplicating common definitions.
- `spear3xx_machdata` is declared as the shared machine descriptor completed by each variant probe.

## Control Flow And Integration
The header has no runtime flow. Its macros are included by SPEAr300, SPEAr310, and SPEAr320 drivers when constructing their group and function arrays. It also imports `pinctrl-spear.h`, which supplies the SPEAr core data structures and helper macros.

## State And Persistence
It owns no storage. It declares shared objects whose storage lives in `pinctrl-spear3xx.c`. Hardware state is affected only when variant drivers and the common SPEAr core consume the declared masks and tables.

## Dependencies
It depends on `pinctrl-spear.h` and the exact names of common group/function symbols in `pinctrl-spear3xx.c`.

## Risks And Review Notes
- Mask definitions are a cross-file ABI. Changing a bit position affects every SPEAr3xx variant.
- Aggregate macros hide ordering and membership. New common groups must update both extern declarations and aggregate macros.
- The shared `spear3xx_machdata` declaration encourages probe-time mutation by variants; that pattern should stay synchronized with the common core expectations.

## Test Signals
Build all SPEAr3xx variant drivers after any mask or macro change. Confirm common group/function counts and names in debugfs for SPEAr300/310/320 and verify common mux bit behavior with register readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear3xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/Kconfig

## Purpose
This Kconfig file defines the build switches for Spreadtrum pinctrl support. It provides a common hidden/base `PINCTRL_SPRD` symbol and a user-visible SC9860 SoC driver option.

## Important Symbols
- `PINCTRL_SPRD` is a tristate base symbol. It selects `PINMUX`, `PINCONF`, `GENERIC_PINCONF`, and `GENERIC_PINMUX_FUNCTIONS`.
- `PINCTRL_SPRD_SC9860` is the visible `Spreadtrum SC9860 pinctrl driver` option. It depends on `OF` and `ARCH_SPRD || COMPILE_TEST`, and selects `PINCTRL_SPRD`.

## Control Flow And Integration
Kconfig has build-time control flow only. Enabling SC9860 pulls in the common Spreadtrum pinctrl core and the SC9860 data driver through the sibling Makefile. The selected generic pinctrl helpers define which pinmux/pinconf APIs are available to the compiled driver.

## State And Persistence
The persistent state is the generated kernel `.config`. No runtime state is created by this file directly.

## Dependencies
It depends on the kernel pinctrl framework, OF support for SC9860, architecture symbol `ARCH_SPRD`, and `COMPILE_TEST` for non-native build coverage.

## Risks And Review Notes
- `PINCTRL_SPRD` is not user-prompted; SoC symbols must select it or the common object will not build.
- Missing generic helper selections would break core driver compilation or runtime feature availability.
- New Spreadtrum SoCs need coordinated Kconfig and Makefile entries.

## Test Signals
Run `make olddefconfig` with `ARCH_SPRD` and with `COMPILE_TEST` to ensure `PINCTRL_SPRD_SC9860` is visible and selects `PINCTRL_SPRD`. Build `drivers/pinctrl/sprd/` and inspect `.config` for `PINMUX`, `PINCONF`, and generic helper selections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/Makefile

## Purpose
This Makefile maps Spreadtrum pinctrl Kconfig symbols to object files.

## Important Build Rules
- `obj-$(CONFIG_PINCTRL_SPRD) += pinctrl-sprd.o` builds the common Spreadtrum pinctrl core.
- `obj-$(CONFIG_PINCTRL_SPRD_SC9860) += pinctrl-sprd-sc9860.o` builds the SC9860 SoC-specific table/driver.

## Control Flow And Integration
The file participates in Kbuild only. Because `PINCTRL_SPRD_SC9860` selects `PINCTRL_SPRD`, a normal SC9860 build links both common and SoC-specific objects.

## State And Persistence
There is no runtime state. Build output depends entirely on `.config`.

## Dependencies
It depends on symbol names from the local `Kconfig` and source files named `pinctrl-sprd.c` and `pinctrl-sprd-sc9860.c` in the same directory.

## Risks And Review Notes
- Kconfig/Makefile symbol mismatch would silently omit required objects.
- Adding another SoC requires an additional object rule and a matching Kconfig symbol.
- If a SoC object is enabled without the common symbol selecting correctly, link failures or missing common APIs would result.

## Test Signals
Build with `CONFIG_PINCTRL_SPRD_SC9860=y` and `=m` to confirm both objects are included with the expected linkage. `make V=1 drivers/pinctrl/sprd/` should show `pinctrl-sprd.o` and `pinctrl-sprd-sc9860.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/Makefile -->
