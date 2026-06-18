# subset-b-005085 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6375.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6375.c

## Purpose
Provides the Qualcomm SM6375 TLMM pin controller description for the shared `pinctrl-msm` core. The file is a SoC data table: it enumerates 164 pin descriptors, 157 GPIO-capable pins, 164 mux functions, GPIO/special pin groups, SD card and UFS reset register descriptions, wake IRQ mappings, and platform-driver binding for `qcom,sm6375-tlmm`.

## Important APIs, Types, and Functions
The main exported contract is `static const struct msm_pinctrl_soc_data sm6375_tlmm`, passed to `msm_pinctrl_probe()` by `sm6375_tlmm_probe()`. The local `PINGROUP()` macro builds `struct msm_pingroup` entries with mux, pull, drive, output-enable, input/output, interrupt, and EGPIO bit positions at `REG_SIZE * id` offsets. `SDC_PINGROUP()` describes non-GPIO SD controller pads with pull/drive fields but no mux or interrupt operations. `UFS_RESET()` describes the UFS reset output pad. `sm6375_mpm_map[]` maps GPIO numbers to MPM wake interrupt IDs. Module registration uses `platform_driver_register()` from `arch_initcall()` and unregisters in `module_exit()`.

## Control Flow
At early init, `sm6375_tlmm_init()` registers `sm6375_tlmm_driver`. A device-tree node with compatible `qcom,sm6375-tlmm` binds to `sm6375_tlmm_probe()`, which delegates all runtime behavior to `msm_pinctrl_probe(pdev, &sm6375_tlmm)`. After that, the shared Qualcomm pinctrl core uses these tables to register pinctrl groups/functions, GPIO chip behavior for `ngpios = 157`, and wake IRQ support. This source has no custom request, set_mux, GPIO, IRQ, suspend, or resume logic.

## State and Persistence Behavior
All SoC-specific state is static and read-only after module load: pin descriptors, pin-function names, per-pin group register offsets, wake IRQ map, and OF match metadata. Runtime mutable state lives in the common `pinctrl-msm` driver and hardware registers. Pad configuration persists only in TLMM hardware register state and may be restored by consumers, firmware, or the common core across boot and power-management flows; this file itself does not store configuration.

## Dependencies and Integration Points
Depends on Linux module, OF, platform-device infrastructure, and `drivers/pinctrl/qcom/pinctrl-msm.h`. It integrates with device tree through `qcom,sm6375-tlmm`, with the generic pinctrl and gpiolib APIs through `msm_pinctrl_probe()`, and with interrupt wake routing through the MPM map. Consumer nodes use the function and group names listed here, including QUP, CCI, camera clocks, display sync, QDSS, UIM, audio, USB PHY, SD card, and UFS reset functions.

## Risks
The file is table-driven and index-sensitive. Pin descriptor order, `DECLARE_MSM_GPIO_PINS()` coverage, `sm6375_groups[]` indices, `.ngpios`, and special pad numbers must stay aligned. The `PINGROUP()` macro sets EGPIO bits even though no `egpio_func` is provided in the SoC data, so changes around EGPIO handling should be checked against the shared core. SDC and UFS groups intentionally disable mux and IRQ fields with `-1`; using normal GPIO paths on those pads would be wrong. Wake IRQ map entries are hardware-specific and incorrect mappings can break suspend wake without affecting normal GPIO interrupts.

## Test Signals
Compile with the Qualcomm pinctrl core, boot with a `qcom,sm6375-tlmm` node, verify pinctrl groups/functions appear in debugfs, request representative GPIOs 0 through 156, configure pull/drive/output/input through gpiolib, exercise QUP/CCI/UIM/audio/display alternate functions from device tree, test UFS reset and SDC1/SDC2 pads, validate wake from suspend for mapped GPIOs, and confirm no consumers can request dummy or special groups as ordinary GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm6375.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm7150.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm7150.c

## Purpose
Defines the Qualcomm SM7150 TLMM pin controller data for the shared MSM pinctrl driver. It describes three TLMM register tiles (`north`, `south`, `west`), 127 pin descriptors, 120 GPIO-capable pins, 109 mux functions, per-pin groups, SD/UFS special pads, PDC wake mappings, and the `qcom,sm7150-tlmm` platform binding.

## Important APIs, Types, and Functions
The central object is `sm7150_tlmm`, a `struct msm_pinctrl_soc_data` containing pin, function, group, tile, wake IRQ, and errata metadata. `PINGROUP(id, tile, ...)` fills `struct msm_pingroup` entries with tile selection and the standard Qualcomm TLMM register bits: mux at bit 2, pull at bit 0, drive at bit 6, output enable at bit 9, interrupt target at bit 5, raw status at bit 4, and two-bit detection at bit 2. `SDC_QDSD_PINGROUP()` models SDC1/SDC2 pads in a tile-aware way, and `UFS_RESET()` models the UFS reset output on the west tile. `sm7150_pdc_map[]` connects selected GPIOs to PDC wake interrupt IDs. The driver also attaches `.pm = &msm_pinctrl_dev_pm_ops`.

## Control Flow
`sm7150_tlmm_init()` registers a platform driver at `arch_initcall` time. Device-tree matching on `qcom,sm7150-tlmm` calls `sm7150_tlmm_probe()`, which hands the static SoC data to `msm_pinctrl_probe()`. From that point, pin muxing, pin configuration, GPIO operations, IRQ handling, and PM callbacks are all handled by the shared `pinctrl-msm` core using the tables from this file.

## State and Persistence Behavior
The SM7150-specific tables are immutable kernel data. Runtime pin states are not cached here; they are represented by hardware register contents and common-core objects allocated during probe. The tile array affects how the common core maps group register offsets to the correct MMIO resource. `.wakeirq_dual_edge_errata = true` tells the shared core to use its workaround path for dual-edge wake IRQ handling on this SoC.

## Dependencies and Integration Points
Uses Linux module, OF, platform-device, and pinctrl headers plus `pinctrl-msm.h`. It integrates with device tree through `qcom,sm7150-tlmm`, with PM through `msm_pinctrl_dev_pm_ops`, with the PDC interrupt controller through `sm7150_pdc_map[]`, and with consumers through named pin functions such as QUP, CCI, camera MCLK, MDP/EDP sync, TSIF, QDSS, UIM, MI2S, PCIe, USB PHY, WLAN ADC, SD card, and UFS reset.

## Risks
Tile assignment is a major risk: the same per-pin offset can refer to different MMIO windows depending on `NORTH`, `SOUTH`, or `WEST`. `ngpios = 120` deliberately excludes UFS and SDC special pads at descriptors 119-126 from ordinary GPIO use. Wake IRQ behavior depends on both the PDC map and the dual-edge errata flag, so regressions may appear only in suspend/resume or edge-triggered wake tests. Consumer-visible function names must match device-tree bindings exactly.

## Test Signals
Boot on SM7150 hardware or DT emulation and check `qcom,sm7150-tlmm` probe, debugfs pin/function/group registration, GPIO request/configuration for pins below 120, SDC1/SDC2 and UFS reset operation, tile-specific mux writes on north/south/west groups, PDC wake from suspend on mapped GPIOs, dual-edge wake IRQ behavior, and suspend/resume with `msm_pinctrl_dev_pm_ops` active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm7150.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8150.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8150.c

## Purpose
Supplies the Qualcomm SM8150 pinctrl/TLMM SoC description for the MSM pinctrl core. It defines four tiles (`north`, `south`, `east`, `west`), 179 pin descriptors, 176 GPIO-capable pins, 128 mux functions, 179 normal/special groups, SDC2 and UFS reset special pads, PDC wake mappings, and the platform driver for compatible `qcom,sm8150-pinctrl`.

## Important APIs, Types, and Functions
`sm8150_pinctrl` is the main `struct msm_pinctrl_soc_data`. `PINGROUP()` constructs tile-aware GPIO groups with standard Qualcomm TLMM field positions and ten mux entries per group including GPIO mode. `SDC_QDSD_PINGROUP()` describes SDC2 pads on the north tile with only pull/drive fields. `UFS_RESET()` describes the UFS reset output on the south tile. `sm8150_pdc_map[]` maps selected GPIOs to PDC wake IRQ IDs and includes some GPIOs with multiple wake IDs. `sm8150_pinctrl_probe()` calls `msm_pinctrl_probe()` and registration occurs via `arch_initcall()`.

## Control Flow
The module registers the platform driver early in boot. When the OF core matches `qcom,sm8150-pinctrl`, probe passes `sm8150_pinctrl` into the common MSM implementation. The common code then interprets the tile names, group offsets, bit fields, and wake map to serve pinctrl, pinconf, GPIO, and IRQ requests. No custom SM8150 runtime code executes beyond probe/register/unregister.

## State and Persistence Behavior
SM8150-specific data is static. Register state is held in TLMM hardware and manipulated by the shared core when clients select states or configure GPIOs. `.wakeirq_dual_edge_errata = true` persists as SoC metadata used by the common interrupt wake path. `.ngpios = 176` means pins 175-178 are descriptors/groups for UFS reset and SDC2, not general GPIO lines.

## Dependencies and Integration Points
Depends on `pinctrl-msm.h`, Linux OF/platform driver support, pinctrl, gpiolib, and irqchip wake infrastructure via the common core. Integration points include device-tree pinctrl states for QUP, QSPI, TSIF, RGMII/EMAC, PCIe, UIM, MI2S/audio, LPASS slimbus, camera/display, QDSS, SD write/SDC4 functions, USB PHY, SDC2, UFS reset, and PDC wake sources.

## Risks
The four-tile layout makes incorrect tile assignment especially damaging because register offsets are otherwise uniform. The PDC map has duplicate GPIO entries for some pins, so consumers and wake logic need coverage for all intended wake routes. The special SDC/UFS groups use `-1` for unsupported mux/IRQ fields, and they are excluded from `ngpios`; treating them as GPIOs would cause invalid register operations. Because this file is almost entirely static arrays, off-by-one errors in pin descriptors, group indices, or function enum ordering can compile cleanly but misprogram hardware.

## Test Signals
Useful signals include successful probe for `qcom,sm8150-pinctrl`, debugfs enumeration of all tiles/groups/functions, representative mux selection in each tile, GPIO input/output/pull/drive on pins below 176, SDC2 and UFS reset behavior, PDC wake from suspend including duplicated wake-map GPIOs, dual-edge wake IRQ handling, and peripheral bring-up for QUP, QSPI, PCIe, UIM, audio, camera, display, and Ethernet-related pin states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8150.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8250-lpass-lpi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8250-lpass-lpi.c

## Purpose
Defines the SM8250 LPASS LPI GPIO pin controller variant data. Unlike the TLMM files, this targets the low-power audio subsystem pins and feeds `pinctrl-lpass-lpi` with 14 pins, SoundWire, DMIC, I2S, MI2S, WSA SoundWire, and GPIO mux options for compatible `qcom,sm8250-lpass-lpi-pinctrl`.

## Important APIs, Types, and Functions
The file defines `enum lpass_lpi_functions` values consumed by `LPI_PINGROUP()` and `LPI_FUNCTION()` macros from `pinctrl-lpass-lpi.h`. `sm8250_lpi_pins[]` lists GPIO0-GPIO13. Per-function group arrays list which GPIO names can provide each audio function. `sm8250_groups[]` maps each pin to up to four mux alternatives and a slew register selector or `LPI_NO_SLEW`. `sm8250_functions[]` exposes 21 non-GPIO functions. `sm8250_lpi_data` is the `struct lpi_pinctrl_variant_data` passed indirectly through OF match data to `lpi_pinctrl_probe()`.

## Control Flow
The `module_platform_driver()` macro registers `lpi_pinctrl_driver`. A device-tree node matching `qcom,sm8250-lpass-lpi-pinctrl` supplies `&sm8250_lpi_data` as match data. The shared LPASS LPI core performs probe, registers the pinctrl/GPIO provider, and handles mux/config operations using the static pins, groups, functions, and slew metadata. Remove delegates to `lpi_pinctrl_remove()`.

## State and Persistence Behavior
The file contains only static variant data. Runtime state, MMIO mappings, GPIO chip registration, and pinctrl state are owned by the LPASS LPI core. Slew support is per-pin: pins with numeric slew offsets can expose slew programming, while pins marked `LPI_NO_SLEW` intentionally do not. Hardware register contents, not this file, hold active mux and electrical state.

## Dependencies and Integration Points
Depends on Linux GPIO, module, platform-device APIs, and `pinctrl-lpass-lpi.h`. It integrates with audio device-tree pinctrl states for SoundWire TX/RX, WSA SoundWire, DMIC1-3, I2S1/I2S2, and QUA MI2S pins. The GPIO fallback is part of the enum but normal function registration lists only the audio functions; the common LPI driver handles GPIO mode.

## Risks
Function enum names must line up with `LPI_PINGROUP()` macro expansion. Group string names must match `PINCTRL_PIN()` names exactly (`gpio0` through `gpio13`). Some pins share functions across buses, such as GPIO5 serving both SoundWire TX/RX data alternatives, so board pinctrl states must avoid impossible simultaneous use. Incorrect slew offset values can silently program the wrong LPASS register.

## Test Signals
Compile with the LPASS LPI core, probe a `qcom,sm8250-lpass-lpi-pinctrl` node, inspect pinctrl debugfs for 14 pins and 21 functions, apply representative SoundWire, DMIC, I2S, MI2S, WSA, and GPIO states, verify pins with `LPI_NO_SLEW` do not attempt unsupported slew writes, and remove/unbind the platform device without leaking pinctrl/GPIO state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8250-lpass-lpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8250.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8250.c

## Purpose
Describes the Qualcomm SM8250 TLMM/pinctrl hardware for the shared MSM pinctrl driver. It defines three tiles (`west`, `south`, `north`), 184 pin descriptors, 181 GPIO-capable lines, 115 mux functions, SDC2 and UFS reset special groups, PDC wake mappings, EGPIO metadata, and platform binding for `qcom,sm8250-pinctrl`.

## Important APIs, Types, and Functions
`sm8250_pinctrl` is the authoritative `struct msm_pinctrl_soc_data`. `PINGROUP()` builds tile-aware GPIO groups and includes both `.egpio_enable = 12` and `.egpio_present = 11`. `SDC_PINGROUP()` and `UFS_RESET()` create special non-GPIO groups. `sm8250_pdc_map[]` maps GPIOs to PDC wake IRQ IDs. `.egpio_func = 9` tells the shared core which mux slot corresponds to EGPIO-capable groups. `sm8250_pinctrl_probe()` delegates to `msm_pinctrl_probe()`, and module registration is done from `arch_initcall()`.

## Control Flow
Early boot registers `sm8250_pinctrl_driver`. Device-tree matching on `qcom,sm8250-pinctrl` calls probe, and probe hands the static SoC data to the common MSM pinctrl core. All later mux selection, pin configuration, GPIO operation, and IRQ handling is data-driven through the tables. The source has no custom SM8250 code paths after probe.

## State and Persistence Behavior
All SM8250-specific data is static after load. Runtime state lives in common-core allocations and TLMM registers. `.ngpios = 181` means descriptors beyond the GPIO range are not ordinary GPIO lines. EGPIO state is represented by the common core and hardware fields using the mux slot and EGPIO bit metadata supplied here.

## Dependencies and Integration Points
Uses Linux OF/platform/module support and `pinctrl-msm.h`. It integrates with device tree through `qcom,sm8250-pinctrl`, with PDC wake routing through `sm8250_pdc_map[]`, and with pinctrl consumers for QUP, QSPI, TSIF, PCIe, camera, CCI, display, audio/MI2S, LPASS slimbus, UIM, QDSS, USB PHY, SD card, UFS reset, and EGPIO-capable pads.

## Risks
The table is highly index-sensitive. A concrete consistency issue is visible in this source: pin descriptors label 180 as `SDC2_CLK`, 181 as `SDC2_CMD`, 182 as `SDC2_DATA`, and 183 as `UFS_RESET`, while the special pin arrays assign `ufs_reset_pins[] = { 180 }`, `sdc2_clk_pins[] = { 181 }`, `sdc2_cmd_pins[] = { 182 }`, and `sdc2_data_pins[] = { 183 }`. Any consumer of the descriptor names or group names should be checked for this mismatch. More generally, tile assignment, `.ngpios`, `.egpio_func`, and wake map entries can all fail at runtime without compile-time errors.

## Test Signals
Probe `qcom,sm8250-pinctrl`, inspect debugfs for pin names versus group membership around pins 180-183, verify GPIO operation for pins 0-180 as intended by `.ngpios`, test EGPIO muxing on groups whose ninth alternate function is `egpio`, exercise SDC2 and UFS reset pinctrl consumers, validate PDC wake from suspend on mapped GPIOs, and bring up representative QUP, PCIe, camera, display, USB, audio, and QDSS states across all three tiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8350.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8350.c

## Purpose
Provides the Qualcomm SM8350 TLMM pinctrl SoC table for the shared MSM pinctrl driver. It enumerates 207 pin descriptors, 204 GPIO-capable lines, 134 mux functions, 207 normal/special groups, SDC2 and UFS reset pads, wake IRQ mappings, and the `qcom,sm8350-tlmm` platform driver binding.

## Important APIs, Types, and Functions
The central data object is `sm8350_tlmm`, a `struct msm_pinctrl_soc_data`. `PINGROUP()` describes standard GPIO groups with mux, pull, drive, output, input, and interrupt bit positions at 0x1000-byte per-pin spacing. `SDC_PINGROUP()` describes SDC2 pads with only pull/drive fields. `UFS_RESET()` describes the UFS reset output register. `sm8350_pdc_map[]` maps selected GPIOs to PDC wake interrupt IDs. Probe is a thin wrapper around `msm_pinctrl_probe(pdev, &sm8350_tlmm)`.

## Control Flow
`sm8350_tlmm_init()` registers the platform driver with `arch_initcall()`. A matching device-tree node with compatible `qcom,sm8350-tlmm` invokes `sm8350_tlmm_probe()`. The shared MSM core then registers the pinctrl provider, GPIO chip for `ngpios = 204`, and wake IRQ support from the static tables. Module exit unregisters the platform driver.

## State and Persistence Behavior
This file has no mutable runtime state beyond platform-driver registration. Pin configuration, mux state, and interrupt state persist in hardware registers and common-core data structures. Pins 203-206 are special descriptors for UFS reset and SDC2 and are outside the ordinary GPIO range. The table has no tile array, so offsets are interpreted in a single register namespace by the common core.

## Dependencies and Integration Points
Depends on Linux module, OF, platform-device support and `pinctrl-msm.h`. Integrates with pinctrl/gpiolib/IRQ users through the common Qualcomm core. Device-tree consumers use function and group names for QUP, PCIe clock request, camera, CCI, display, QDSS, audio/MI2S/LPASS slimbus, UIM, MSS/QLINK/coexistence, navigation GPIOs, USB PHY, SDC2, and UFS reset.

## Risks
SM8350 has the largest table in this work item, so off-by-one descriptor/group/function errors are the primary risk. `.ngpios = 204` must remain aligned with pin descriptors and special groups. Wake IRQ map entries are numerous and hardware-specific; bad entries mainly surface in low-power wake tests. The absence of tile metadata means adding tile-style offsets later would require coordinated changes with resource mapping in the common core.

## Test Signals
Build and boot with `qcom,sm8350-tlmm`, verify debugfs shows 207 pins and all functions, request GPIOs below 204, reject or avoid ordinary GPIO use for UFS/SDC special pads, exercise representative QUP, PCIe, camera, CCI, audio, UIM, QDSS, USB, MSS, SDC2, and UFS reset pinctrl states, and validate suspend wake for mapped PDC GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8350.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8450-lpass-lpi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8450-lpass-lpi.c

## Purpose
Defines the SM8450 LPASS LPI pin controller variant data for the shared LPASS LPI pinctrl driver. It covers 23 low-power audio GPIO pins and 38 audio-oriented functions, including SoundWire, WSA/WSA2 SoundWire, DMIC1-4, I2S1-4, QUA MI2S, SLIMbus, external MCLK alternatives, and GPIO fallback for compatible `qcom,sm8450-lpass-lpi-pinctrl`.

## Important APIs, Types, and Functions
The `enum lpass_lpi_functions` values are referenced by the LPI macros. `sm8450_lpi_pins[]` lists GPIO0-GPIO22. Per-function group arrays define the valid pin names for each function. `sm8450_groups[]` uses `LPI_PINGROUP()` to bind each pin to mux alternatives and a slew offset or `LPI_NO_SLEW`. `sm8450_functions[]` exports the non-GPIO functions. `sm8450_lpi_data` is the `struct lpi_pinctrl_variant_data` attached to the OF match entry and consumed by `lpi_pinctrl_probe()`.

## Control Flow
`module_platform_driver(lpi_pinctrl_driver)` registers the driver. On OF match with `qcom,sm8450-lpass-lpi-pinctrl`, the platform core calls `lpi_pinctrl_probe()`, which reads the match data and registers the LPASS LPI pinctrl/GPIO provider. Runtime mux and configuration operations are implemented in `pinctrl-lpass-lpi`, while this file only supplies the SM8450 variant tables. Remove delegates to `lpi_pinctrl_remove()`.

## State and Persistence Behavior
All variant information is static const data. The common LPI core owns runtime state, MMIO mappings, GPIO registration, and active pinctrl states. Pins with numeric slew offsets have per-pin slew programming support; pins with `LPI_NO_SLEW` intentionally omit it. The active mux, GPIO, and electrical state lives in LPASS LPI hardware registers rather than in this file.

## Dependencies and Integration Points
Depends on Linux GPIO, module, platform-device APIs, and `pinctrl-lpass-lpi.h`. Integrates with audio subsystem device-tree pinctrl states for SoundWire TX/RX, WSA and WSA2 amplifiers, DMICs, I2S buses, QUA MI2S, SLIMbus, and external master clock routes. Group names must match pin names exactly because the common pinctrl core resolves functions by string groups.

## Risks
The SM8450 table has many overlapping audio functions on the same pins, so board-level pinctrl states must avoid conflicting simultaneous selections. Enum ordering, group-array names, and `LPI_PINGROUP()` macro expansion are tightly coupled. Small formatting or naming mistakes in group strings can make functions invisible to consumers. Incorrect slew offsets, especially around added pins 14-22, would program the wrong LPI register or expose unsupported slew controls.

## Test Signals
Build with the LPASS LPI core, probe `qcom,sm8450-lpass-lpi-pinctrl`, inspect debugfs for 23 pins and 38 functions, apply SoundWire TX/RX, WSA/WSA2, DMIC1-4, I2S1-4, QUA MI2S, SLIMbus, external MCLK, and GPIO states, verify slew behavior only on supported pins, and unbind/rebind the platform device to exercise remove/probe cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sm8450-lpass-lpi.c -->
