# subset-b-005084 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdx55.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdx55.c

## Purpose
Provides the Qualcomm SDX55 TLMM pin controller description for the shared `pinctrl-msm` driver. The file is almost entirely static SoC data: 108 GPIO pins, four SD/eMMC pseudo-pins, mux function names, function-to-group membership arrays, per-pin register layout, and the platform-driver binding for `qcom,sdx55-pinctrl`.

## Important APIs, Types, And Functions
`sdx55_pins[]` declares pins 0-107 plus `SDC1_RCLK`, `SDC1_CLK`, `SDC1_CMD`, and `SDC1_DATA`. `DECLARE_MSM_GPIO_PINS()` creates one-pin arrays consumed by `PINCTRL_PINGROUP`. `enum sdx55_functions` and `sdx55_functions[]` expose mux selectors through `FUNCTION(...)`. `PINGROUP()` fills `struct msm_pingroup` entries for normal GPIOs with a 0x1000 register stride and standard Qualcomm bit positions. `SDC_PINGROUP()` models SD controller pads with pull/drive fields but no mux, GPIO, or interrupt control. `sdx55_pinctrl` is the `struct msm_pinctrl_soc_data` passed to `msm_pinctrl_probe()`.

## Control Flow
At `arch_initcall`, `sdx55_pinctrl_init()` registers the platform driver. Device tree match creates a platform device, `sdx55_pinctrl_probe()` calls `msm_pinctrl_probe(pdev, &sdx55_pinctrl)`, and the shared driver registers pinctrl, pinmux, pinconf, GPIO, and IRQ handling from these tables. Runtime requests select a function by name, then the shared driver uses the group entry to program mux, pull, drive, output enable, value, and interrupt bits in the TLMM register block.

## State And Persistence
This file has no mutable local state. Persistent state is the hardware TLMM register content programmed by the common driver. The only durable contract here is the static mapping between Linux pin/group/function names and SDX55 register offsets. `ngpios = 108`, so pins 108-111 are non-GPIO SDC groups and are intentionally outside gpiolib.

## Dependencies And Integration Points
Depends on `pinctrl-msm.h`, Linux platform driver matching, and device-tree states referencing group/function names such as BLSP UART/I2C/SPI, UIM, QDSS, QLINK, SPMI, PCIe, EMAC PPS, TSENS, and SD controller pads. Interrupt fields target KPSS with value 3. Unlike later SDX parts, there is no wakeirq map in this file.

## Risks
The array has sparse designated entries: GPIO groups 0-107 and SDC entries 109-112, leaving index 108 empty even though `SDC1_RCLK` pin number is 108. That is intentional only if the shared core tolerates empty groups between valid entries. Wrong SDC offsets or pull/drive bit positions can silently break eMMC/SD signal integrity. Absence of a wake map means suspend wake support depends on other firmware paths or is unavailable. Because all pin mux alternatives are positional integer arrays, a mismatched function enum/order would program the wrong mux value.

## Test Signals
Useful signals are boot probe on `qcom,sdx55-pinctrl`, `/sys/kernel/debug/pinctrl` showing 112 pins and expected group/function names, GPIO loopback for pins below 108, interrupt trigger tests on TLMM-backed GPIOs, BLSP/UIM/QDSS/PCIe/EMAC pin-state application from device tree, and SD/eMMC operation with pull/drive changes. Source size reviewed: 1007 lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdx55.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdx65.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdx65.c

## Purpose
Describes the Qualcomm SDX65 TLMM controller for the common MSM pinctrl implementation. It covers 108 regular GPIOs, a UFS reset pseudo-pin, four SDC/QDSD pins, SoC mux functions, and GPIO-to-PDC wake interrupt routing for the `qcom,sdx65-tlmm` compatible.

## Important APIs, Types, And Functions
`PINGROUP()` defines normal GPIO group register offsets from `REG_BASE + 0x1000 * id` with mux bit 2, pull bit 0, drive bit 6, output-enable bit 9, value bits 0/1, and IRQ fields at bits 0-5. `SDC_QDSD_PINGROUP()` describes SD controller pads without mux/GPIO/IRQ support. `UFS_RESET()` defines the dedicated reset output with pull, drive, and output value support but no mux or interrupt fields. `sdx65_pdc_map[]` maps selected GPIO numbers to PDC IRQ lines, and `sdx65_pinctrl` packages pins, functions, groups, `ngpios = 109`, and wakeirq metadata.

## Control Flow
The platform driver is registered from `arch_initcall`. Matching `qcom,sdx65-tlmm` invokes `sdx65_pinctrl_probe()`, which delegates to `msm_pinctrl_probe()`. The common driver then consumes `sdx65_groups[]` to resolve device-tree pinctrl states, service GPIO requests, and register IRQ domains. Wake-capable GPIOs are connected through `sdx65_pdc_map[]` when the common code arms wake interrupts.

## State And Persistence
All state in this file is static descriptor data. Hardware state persists in TLMM, UFS reset, and SD controller pad registers after common-driver writes. `ngpios = 109` includes GPIO0-107 plus the UFS reset group as a GPIO-like controllable line, while SDC pins 109-112 are pinctrl-only special groups.

## Dependencies And Integration Points
Integrates with `pinctrl-msm`, gpiolib, irqchip/PDC wake routing, UFS reset control via pinctrl/GPIO semantics, SD/eMMC pad configuration, and device-tree consumers for BLSP, UIM, QLINK0/1/2, QDSS, SPMI, PCIe, audio, TSENS, DDR/BIMC test, and USB PHY analog control functions. The DT compatible differs from SDX55 by using `-tlmm`.

## Risks
The UFS reset group uses offset 0x0 while normal GPIO0 also starts at base 0x0; correctness depends on the hardware map and common driver treating the pseudo-group as intended. Wake routing is hand-coded, so wrong GPIO/PDC pairs can produce missed suspend wakeups or spurious wake events. Empty mux alternatives represented by `_` still consume mux selector positions; any enum or table reorder changes ABI-visible function numbers. SDC/QDSD groups have no interrupt or output-enable fields, so accidental GPIO use should be rejected by the core.

## Test Signals
Probe with `qcom,sdx65-tlmm`; verify 113 pins, 109 GPIO-capable groups, UFS reset toggling, SD/eMMC card operation, PDC wake from mapped GPIOs in suspend, and mux application for BLSP/UIM/QLINK/QDSS states. Debugfs should expose function groups consistent with `sdx65_functions[]`. Source size reviewed: 955 lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdx65.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdx75.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdx75.c

## Purpose
Defines the SDX75 TLMM pin controller data for the shared Qualcomm MSM pinctrl driver. It models 133 GPIOs, SDC1 and SDC2 pseudo-pads, expanded mux options, eGPIO metadata bits, and a large GPIO-to-PDC wake map for the `qcom,sdx75-tlmm` binding.

## Important APIs, Types, And Functions
`PINGROUP()` creates `struct msm_pingroup` entries with `REG_BASE = 0x100000`, 0x1000 stride, eleven mux selectors per group, and eGPIO fields `.egpio_enable = 12` and `.egpio_present = 11`. `SDC_QDSD_PINGROUP()` supplies non-GPIO SD pad groups at offsets 0x19a000 and 0x19b000. `sdx75_pins[]`, `enum sdx75_functions`, `sdx75_functions[]`, and many group-name arrays enumerate QUP, Ethernet/RGMII, PCIe, QLINK, UIM, QDSS, audio, and test functions. `sdx75_pdc_map[]` provides wakeirq routing. The probe uses `of_device_get_match_data()` instead of passing a file-local singleton directly.

## Control Flow
`sdx75_pinctrl_init()` registers the platform driver early. The OF match table carries `.data = &sdx75_pinctrl`; `sdx75_pinctrl_probe()` retrieves it, returns `-EINVAL` if absent, and calls `msm_pinctrl_probe()`. After registration, common pinctrl/gpio/irq callbacks use the per-group offsets and mux lists to program TLMM and route wake IRQs.

## State And Persistence
The file has static configuration only. Runtime state belongs to the common driver and hardware registers. `ngpios = 133`; pins 133-139 are SDC-only and not gpiolib GPIOs. eGPIO presence/enable bits add another hardware state dimension that the shared driver may inspect or configure for external GPIO-capable pads.

## Dependencies And Integration Points
Depends on `pinctrl-msm` support for eGPIO bit fields, PDC wake maps, OF match data, and standard TLMM register semantics. Integrates with QUP serial engines, two Ethernet MAC/PHY interfaces through RGMII/SGMII/MDIO/PTP/PPS groups, PCIe clock request lines, SD card detect/write-protect style signals, UIM, QLINK, QDSS, and audio/debug/test functions.

## Risks
This file has a high risk of table transcription errors because Ethernet, QUP, QDSS, and wake mappings are dense and selector positions are hardware ABI. The nonzero `REG_BASE` means a missing base adjustment would target wrong registers for every GPIO. SDC offsets sit in the same numerical region as `REG_BASE`-relative GPIOs, so register-map validation matters. The probe now depends on match `.data`; adding a compatible without data would fail probe. The license string is `GPL` while the SPDX is GPL-2.0-only, which is common but worth noticing in automated license checks.

## Test Signals
Boot probe, debugfs pin/function inspection, GPIO direction/value/IRQ tests below 133, PDC wake validation across representative mapped pins, Ethernet RGMII/MDIO/PTP operation, PCIe clock request pin states, QUP serial/I2C/SPI operation, SD1/SD2 pad drive and pull validation, and eGPIO present/enable behavior where hardware exposes it. Source size reviewed: 1140 lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdx75.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm4250-lpass-lpi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm4250-lpass-lpi.c

## Purpose
Supplies SM4250 LPASS low-power-island pin, group, and function data for the reusable `pinctrl-lpass-lpi` driver. It covers audio-domain GPIOs rather than main TLMM pins, exposing SoundWire, MI2S/I2S, DMIC, SLIMbus, external master clocks, QUP IO, and sync output muxes for `qcom,sm4250-lpass-lpi-pinctrl`.

## Important APIs, Types, And Functions
`enum lpass_lpi_functions` defines LPI mux IDs ending in `LPI_MUX_gpio` and `LPI_MUX__`. `sm4250_lpi_pins[]` declares pins `gpio0` through `gpio26`. Function group arrays bind each function name to one or more GPIO group names. `sm4250_groups[]` uses `LPI_PINGROUP(pin, slew_offset, f1, f2, f3, f4)`; several low-numbered audio pins have explicit slew offsets, while many digital microphone and QUP/sync pins use `LPI_NO_SLEW`. `sm4250_functions[]` exposes `LPI_FUNCTION(...)` entries. `sm4250_lpi_data` is the `struct lpi_pinctrl_variant_data` consumed by `lpi_pinctrl_probe()`.

## Control Flow
`module_platform_driver()` registers a simple variant driver. On OF match, the generic LPASS LPI probe fetches `.data`, maps the LPASS TLMM and optional slew resources, registers generic per-pin groups, pinctrl operations, and a sleeping GPIO chip. This file contributes only the variant arrays that tell the generic driver which mux values and slew offsets are legal for each pin.

## State And Persistence
No local mutable state exists. Hardware state persists in LPASS LPI registers configured by `pinctrl-lpass-lpi.c`. Pins 0-23 and 25-26 have group entries; pin 24 is declared as a pin and appears only as part of the `sync_out_groups[]` function list, so consumers must rely on the generic driver handling pins without explicit mux group entries carefully.

## Dependencies And Integration Points
Depends on `pinctrl-lpass-lpi.h` macros, the LPASS LPI generic probe/remove functions, gpiolib, and platform DT resources/clocks expected by the generic driver. Integrates with ASoC/audio DT pin states for SoundWire TX/RX/WSA, MI2S/quad MI2S, DMIC, SLIMbus, external clocks, and QUP IO pins used by low-power audio firmware or peripherals.

## Risks
Function membership must match hardware mux values exactly; audio pins often share pads across SoundWire, MI2S, DMIC, and external clocks, so a wrong selector can silently break capture/playback. The declared-but-not-explicitly-grouped gpio24 is a notable audit point. Slew offsets are sparse and variant-specific; using `LPI_NO_SLEW` incorrectly can make high-speed audio signaling marginal. Because this is module-driven, missing compatible or resource names produce a full LPASS audio pinctrl probe failure.

## Test Signals
Probe with `qcom,sm4250-lpass-lpi-pinctrl`, debugfs function/group visibility, GPIO request/set/get for LPASS pins, audio playback/capture over SoundWire and MI2S, DMIC capture on listed pins, external MCLK output, QUP IO pin states, sync output on GPIO19-26, and pinconf readback for slew-capable pins. Source size reviewed: 236 lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm4250-lpass-lpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm4450.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm4450.c

## Purpose
Defines the SM4450 application-processor TLMM pin controller for the common MSM pinctrl driver. It describes 136 GPIOs, UFS reset, SDC1/SDC2 special pads, mux tables for camera/display/QUP/UIM/USB/PCIe/debug functions, eGPIO bits, and PDC wake routing for `qcom,sm4450-tlmm`.

## Important APIs, Types, And Functions
`PINGROUP()` uses a 0x1000 register stride, standard mux/pull/drive/output/IRQ bit positions, and eGPIO bits 11/12. `SDC_QDSD_PINGROUP()` and `UFS_RESET()` describe special nonstandard pads. `QUP_I3C()` is defined but unused in this file, suggesting a leftover helper or future extension. `sm4450_pins[]`, `DECLARE_MSM_GPIO_PINS()`, `enum sm4450_functions`, function group arrays, `sm4450_functions[]`, and `sm4450_groups[]` provide the actual pinctrl surface. `sm4450_pdc_map[]` supplies GPIO wake routing. `sm4450_tlmm` packages this data with `ngpios = 137`.

## Control Flow
Early platform-driver registration happens through `arch_initcall`. The OF compatible `qcom,sm4450-tlmm` calls `sm4450_tlmm_probe()`, which passes `sm4450_tlmm` to `msm_pinctrl_probe()`. The common driver registers pins, functions, GPIOs, and IRQ support, then programs group registers according to device-tree pinctrl states and GPIO/IRQ clients.

## State And Persistence
The file is static data. Runtime pin state persists in TLMM, UFS reset, and SD pad registers. GPIOs 0-135 plus the UFS reset pseudo-line are gpiolib-visible through `ngpios = 137`; SDC pins 137-143 are special pinctrl-only groups. eGPIO present/enable bits allow the shared driver to account for externally capable GPIO pads.

## Dependencies And Integration Points
Integrates with `pinctrl-msm`, PDC wake IRQ support, UFS, SD/eMMC, QUP/I3C-capable serial engines, camera CCI/MCLK, display vsync, UIM, USB PHY/HS analog controls, PCIe clock request, WLAN coexistence/test signals, QDSS CTI/GPIO, and power/debug/test functions. Device-tree pin state names must match the function and group strings here exactly.

## Risks
The unused `QUP_I3C()` macro is harmless at runtime but can mislead maintainers into thinking I3C mode registers are wired when only mux names are present. Wake map density creates suspend-resume risk if any GPIO/PDC pair is wrong. UFS reset at 0x97000 and SDC offsets at 0x8c000/0x8f000 must match the SoC address map, not the normal GPIO stride. Function alternatives include many `_` placeholders, so selector position is more important than visible function count.

## Test Signals
Probe and debugfs inspection on SM4450 hardware, GPIO/IRQ tests across low and high GPIO numbers, PDC wake from representative mapped pins, UFS reset assertion/deassertion, SD1/SD2 operation, QUP serial/I2C/I3C-mode board tests, camera CCI/MCLK states, display vsync outputs, USB PHY control, and PCIe clock request pin behavior. Source size reviewed: 1010 lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm4450.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6115-lpass-lpi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6115-lpass-lpi.c

## Purpose
Provides SM6115 LPASS LPI pinctrl variant data for the shared LPASS low-power audio GPIO driver. It describes 19 audio-domain pins and mux functions for SoundWire, quad MI2S, DMIC, I2S1-3, and WSA MCLK under `qcom,sm6115-lpass-lpi-pinctrl`.

## Important APIs, Types, And Functions
`enum lpass_lpi_functions` enumerates the variant mux IDs. `sm6115_lpi_pins[]` declares `gpio0` through `gpio18`. Function group arrays define where each audio function can appear. `sm6115_groups[]` maps each pin to a `LPI_PINGROUP` with either explicit slew offsets for SoundWire and WSA MCLK pins or `LPI_NO_SLEW` for many digital audio pins. `sm6115_functions[]` exports function descriptors, and `sm6115_lpi_data` passes pins, groups, and functions to the generic LPI probe.

## Control Flow
The module platform driver binds to its OF compatible and uses generic `lpi_pinctrl_probe` and `lpi_pinctrl_remove`. Probe-time control flow is in `pinctrl-lpass-lpi.c`; this file only supplies the static function/group matrix. Runtime mux or pinconf changes requested by audio drivers are validated against these arrays before the generic driver writes LPASS LPI registers.

## State And Persistence
No mutable local state exists. Hardware state persists in LPASS LPI TLMM and slew registers. All declared pins 0-18 have group entries, and the final pin, gpio18, exposes `wsa_mclk` with explicit slew offset 14.

## Dependencies And Integration Points
Depends on `pinctrl-lpass-lpi.h`, generic LPASS LPI probe/remove, platform resources, optional clocks, gpiolib, and audio subsystem DT pin states. Integrates with SoundWire TX/RX, quad MI2S, DMIC01/23, I2S1/I2S2/I2S3, and WSA clock routing for SM6115 audio hardware.

## Risks
The file has no active logic, so failures are mostly table-contract bugs: wrong mux order, wrong group membership, or wrong slew offset. Several pins multiplex SoundWire and MI2S data, so board-specific states must avoid conflicting active functions. The generic driver has a 32-pin bitmap limit; this 19-pin variant is within it. Missing a function in `sm6115_functions[]` would make an otherwise listed group unusable from device tree.

## Test Signals
Successful probe, debugfs group/function listing, GPIO operations on LPASS pins, SoundWire TX/RX audio playback/capture, DMIC capture, I2S1-3 pin states, quad MI2S routing, WSA MCLK output, and pinconf readback on pins with explicit slew offsets. Source size reviewed: 155 lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6115-lpass-lpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6115.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6115.c

## Purpose
Defines the main SM6115 TLMM controller for the shared MSM pinctrl driver. It uses a tiled register map (`south`, `east`, `west`), 113 regular GPIOs, a UFS reset pseudo-line, SDC1/SDC2 special pads, mux functions for QUP/camera/UIM/audio/debug/test signals, and an MPM wake map.

## Important APIs, Types, And Functions
`sm6115_tiles[]` and the `SOUTH/EAST/WEST` enum name the TLMM regions consumed by the common driver. `PINGROUP()` adds `.tile = _tile` alongside the normal 0x1000 stride and standard mux/pull/drive/GPIO/IRQ bit fields. `SDC_QDSD_PINGROUP()` and `UFS_RESET()` also carry tile metadata, with UFS forced to `WEST`. `sm6115_groups[]` assigns every GPIO and special group to a tile and mux selector list. `sm6115_mpm_map[]` maps GPIOs to MPM wake interrupt numbers. `sm6115_tlmm` sets `ngpios = 114`, tile metadata, and wake map pointers.

## Control Flow
`sm6115_tlmm_init()` registers the platform driver at `arch_initcall`. The `qcom,sm6115-tlmm` match calls `sm6115_tlmm_probe()`, which delegates to `msm_pinctrl_probe()`. The common driver uses tile names to map/select register banks, then uses group descriptors to program mux/pinconf/GPIO/IRQ state. Wake setup uses the MPM map rather than a PDC map.

## State And Persistence
This file has static descriptor state only. Runtime state lives in the common driver and TLMM/MPM hardware. `ngpios = 114` includes GPIO0-112 and UFS reset at group 113; SDC groups 114-120 are special pad controls and not normal GPIOs.

## Dependencies And Integration Points
Integrates with `pinctrl-msm` tiled-bank support, MPM wake IRQ handling, UFS, SD/eMMC, QUP0-5, camera CCI/MCLK/timers, UIM1/2, display vsync, audio/adsp pins, USB PHY, QDSS, WLAN ADC, navigation/GPS, and several test/debug functions. Device-tree must provide TLMM resources compatible with the tile names used here.

## Risks
Tile assignment is a major risk: a correct offset in the wrong tile writes the wrong MMIO bank. MPM wake mappings are hand-maintained and must match firmware/interrupt-controller numbering. UFS reset and SDC groups are GPIO-like array entries but have restricted bit fields; consumers must not assume full IRQ or mux support. Function names such as `atest`, `dac_calib`, and `phase_flag` are broad test hooks, so accidental board usage can conflict with manufacturing/debug modes.

## Test Signals
Probe on `qcom,sm6115-tlmm`, debugfs showing tile-backed groups, GPIO direction/value/IRQ tests across all three tiles, MPM wake tests during suspend, UFS reset and storage bring-up, SD1/SD2 pad operation, QUP/camera/UIM/display pin states, and validation that pinctrl states touching special groups reject unsupported GPIO/IRQ operations. Source size reviewed: 923 lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6115.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6125.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6125.c

## Purpose
Provides the SM6125 TLMM SoC description for the MSM pinctrl core. It is a tiled controller with 133 regular GPIOs, UFS reset, SDC1/SDC2 pad groups, a large mux matrix spanning QUP, camera, audio, display, USB, navigation, UIM, QDSS, and test functions, plus MPM wake routing.

## Important APIs, Types, And Functions
`sm6125_tiles[]` names `south`, `east`, and `west` MMIO tiles. `PINGROUP()` creates tiled GPIO descriptors using a 0x1000 per-pin stride and standard TLMM bit assignments. `SDC_QDSD_PINGROUP()` and `UFS_RESET()` encode special pad/reset groups with limited capabilities and tile metadata. `sm6125_pins[]`, `enum sm6125_functions`, function group arrays, `sm6125_functions[]`, and `sm6125_groups[]` define the pinctrl ABI. `sm6125_mpm_map[]` maps GPIOs to MPM wake lines. `sm6125_tlmm` sets `ngpios = 134`.

## Control Flow
The driver is registered early through `arch_initcall`. A `qcom,sm6125-tlmm` platform device calls `sm6125_tlmm_probe()`, which passes the static data to `msm_pinctrl_probe()`. The common driver maps tiles, registers pinctrl/gpio/irq support, resolves device-tree group/function strings, and applies mux and pinconf settings. Suspend wake setup uses the MPM map.

## State And Persistence
There is no local runtime state. Hardware configuration persists in TLMM, UFS, and SDC registers after the common driver writes them. GPIO0-132 plus UFS reset at group 133 are counted in `ngpios`; SDC groups 134-140 are special pinctrl-only pads.

## Dependencies And Integration Points
Depends on `pinctrl-msm` tiled controller support and MPM wake routing. Integrates with QUP00-04 and QUP10-14 serial engines, camera CCI/MCLK/timers, WSA/MI2S/SoundWire/audio reference pins, DisplayPort/eDP hotplug and LCD, USB PHY/test pins, navigation/GPS, UIM, QLINK, QDSS, DDR/test hooks, and storage controllers.

## Risks
This is one of the denser tables in the set; selector order and tile assignment are the central correctness risks. Some functions are named `unused1`/`unused2`, which may indicate reserved hardware modes that should not be exposed to board files unless bindings deliberately allow them. MPM mappings include noncontiguous GPIOs and low wake numbers; wrong entries can be hard to diagnose because normal GPIO interrupts may still work while wake from suspend fails. SDC2 uses a high offset `0x58b000`, so resource sizing must cover it.

## Test Signals
Boot probe, debugfs inspection for all functions, GPIO/IRQ tests across south/east/west tiles, suspend wake using representative MPM-mapped GPIOs, UFS reset and SD1/SD2 operation, QUP buses, camera and display pin states, audio interfaces, USB/eDP/DP hotplug pins, and checks that reserved/unused muxes are not selected by production DT. Source size reviewed: 1282 lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6125.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6350.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6350.c

## Purpose
Defines the SM6350 TLMM controller data for the common MSM pinctrl driver. It covers 156 regular GPIOs, UFS reset, SDC1/SDC2 pads, a broad mux set for QUP, camera, display, LPASS/audio, UIM, QLINK, RFFE, USB/PCIe, QDSS, and test functions, plus PDC wake routing with a dual-edge wake erratum flag.

## Important APIs, Types, And Functions
`PINGROUP()` models normal GPIOs with 0x1000 stride and standard TLMM mux/pull/drive/output/interrupt fields. `SDC_PINGROUP()` and `UFS_RESET()` define special pad/reset groups with limited field support. `sm6350_pins[]`, `enum sm6350_functions`, function group arrays, `sm6350_functions[]`, and `sm6350_groups[]` form the pinctrl ABI. `sm6350_pdc_map[]` maps GPIOs to PDC IRQs. `sm6350_tlmm` sets `ngpios = 157`, wakeirq metadata, and `.wakeirq_dual_edge_errata = true`.

## Control Flow
`sm6350_tlmm_init()` registers the platform driver at `arch_initcall`. The `qcom,sm6350-tlmm` match calls `sm6350_tlmm_probe()`, which delegates to `msm_pinctrl_probe()`. Common code registers pinctrl, pinmux, pinconf, GPIO, and IRQ domains, applies DT-requested pin states, and uses the PDC wake map plus erratum flag when configuring wake-capable interrupts.

## State And Persistence
The file is static data only. Runtime state is in common driver allocations and TLMM/PDC hardware. `ngpios = 157` includes GPIO0-155 plus UFS reset at group 156; SDC groups 157-163 are special pinctrl-only groups. The dual-edge wake erratum changes wakeirq behavior in the common driver but is declared here as a SoC property.

## Dependencies And Integration Points
Depends on `pinctrl-msm` support for wake maps and dual-edge wake errata. Integrates with QUP/I3C, CCI/camera clocks, MDP/eDP/DP, LPASS external/audio/MI2S/SLIMbus/SoundWire-related pads, UIM, RFFE front-end buses, USB PHY, PCIe clock request, QLINK, QDSS, SD/eMMC, UFS, and WLAN/navigation/test interfaces.

## Risks
The table has many high-numbered pins with no mux alternatives, so off-by-one errors around GPIO155/UFS/SDC boundaries are likely audit points. The PDC wake map is large and nonsequential; wrong entries can pass normal IRQ tests while failing wake. `.wakeirq_dual_edge_errata = true` is significant: removing it could break both-edge wake semantics. Several QDSS GPIO aliases and audio functions overlap pins, making board-level mux conflicts possible.

## Test Signals
Probe and debugfs inspection on SM6350, GPIO value/direction and interrupt tests over low/mid/high pins, both-edge wake tests on mapped GPIOs, UFS reset and SD1/SD2 operation, QUP/I3C buses, camera CCI/MCLK, display hotplug/vsync, LPASS/audio pin states, UIM/RFFE/QLINK, USB/PCIe control pins, and verification of wake behavior under the dual-edge erratum path. Source size reviewed: 1389 lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6350.c -->
