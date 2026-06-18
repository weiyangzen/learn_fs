# subset-b-005083 Research

This grouped report covers Qualcomm pinctrl driver sources under `sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/`. Each section is bounded for reconciliation into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc8180x.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc8180x.c

## Purpose

`pinctrl-sc8180x.c` is the Qualcomm SC8180x TLMM pinctrl/GPIO description consumed by the shared MSM pinctrl core. It describes the SoC's TLMM pin numbers, alternate mux functions, GPIO register layout, tile placement, special SD/UFS groups, wake interrupt mapping, and DT/ACPI platform binding. The file is data-heavy, but it also has an SC8180x-specific ACPI resource-splitting probe path because ACPI firmware exposes TLMM as one memory resource while the shared MSM core expects named tile resources.

## Important APIs, Types, and Data

- Includes `pinctrl-msm.h` and publishes `struct msm_pinctrl_soc_data` instances for the generic Qualcomm MSM pinctrl driver.
- `sc8180x_tiles[]` names the three TLMM tiles: `south`, `east`, and `west`; the tile enum indexes the same names.
- `struct tile_info` and `sc8180x_tile_info[]` record ACPI-only offsets/sizes used to split a monolithic TLMM memory range into tile resources.
- `PINGROUP_OFFSET()` and `PINGROUP()` generate ordinary `struct msm_pingroup` entries with mux, pull, drive, output-enable, input/output, and interrupt bit positions. `PINGROUP_OFFSET()` handles banks whose register offsets do not match the simple `REG_SIZE * id` pattern.
- `SDC_QDSD_PINGROUP()` describes non-GPIO SD-card/QDSD pin groups with no mux or interrupt support and fixed pull/drive bit fields.
- `UFS_RESET()` describes the UFS reset pseudo group with output control but no normal mux/interrupt fields.
- `sc8180x_pins[]`, `DECLARE_MSM_GPIO_PINS()`, per-function `*_groups[]`, `enum sc8180x_functions`, `sc8180x_functions[]`, and `sc8180x_groups[]` form the pinctrl core's visible pin, function, and group database.
- `sc8180x_acpi_reserved_gpios[]` reserves firmware-owned GPIOs for ACPI operation.
- `sc8180x_pdc_map[]` maps GPIO lines to PDC wake interrupt lines.
- `sc8180x_pinctrl` is the DT data path: pins, functions, groups, 191 GPIOs, tile names, and wake map.
- `sc8180x_acpi_pinctrl` is the ACPI data path: pins, groups, reserved GPIOs, 190 GPIOs, and tile names, but no function table or PDC wake map.
- `sc8180x_pinctrl_of_match[]` binds `qcom,sc8180x-tlmm`; `sc8180x_pinctrl_acpi_match[]` binds ACPI ID `QCOM040D` with driver data pointing at the ACPI SoC data.

## Control Flow

The platform driver is registered at `arch_initcall()` by `sc8180x_pinctrl_init()` and unregistered by the module exit function. Probe calls `device_get_match_data()` to choose the DT or ACPI `msm_pinctrl_soc_data`; if no match data exists, probe fails with `-EINVAL`.

Before handing off to `msm_pinctrl_probe()`, probe runs `sc8180x_pinctrl_add_tile_resources()`. For DT nodes, that helper returns immediately because DT already models the TLMM tiles as separate resources. For ACPI devices, it allocates a replacement resource table, copies non-memory resources, finds the single memory resource, creates three named tile memory resources by applying `sc8180x_tile_info[]`, inserts those resources into the parent resource tree, removes the original monolithic memory resource, and installs the new resource table with `platform_device_add_resources()`. After this transformation, the shared MSM core can map tiles as if firmware had described them natively.

After resource preparation, all pinctrl, pinmux, GPIO, and IRQ behavior is delegated to the MSM core through `msm_pinctrl_probe()`.

## State and Persistence

The driver has no runtime-persistent state of its own beyond static const tables and the devm-allocated ACPI replacement resources. Pin configuration, direction, mux, drive strength, pull, GPIO data, and interrupt configuration persist in TLMM hardware registers managed through the shared core. ACPI probing mutates the platform device resource list for the lifetime of the device, replacing a firmware-provided single memory resource with three named tile resources. The source's static SoC data is shared across probes and is not dynamically modified.

## Dependencies and Integration Points

This file depends on the Linux platform bus, OF/ACPI matching, resource management, and `drivers/pinctrl/qcom/pinctrl-msm.*`. Its tables must match Qualcomm SC8180x TLMM hardware and the binding names consumed by device trees or ACPI tables. It integrates with the generic pinctrl, pinmux, gpiochip, and irqchip paths exposed by the MSM core. Wake behavior depends on correct GPIO-to-PDC mapping. ACPI behavior depends on `device_get_match_data()` returning the `kernel_ulong_t` driver data from the ACPI table and on safe resource-tree surgery before `msm_pinctrl_probe()`.

## Risks and Edge Cases

- The ACPI resource split is the main behavioral risk: incorrect offsets/sizes or resource-tree insertion/removal failures can break all TLMM register mappings on ACPI systems.
- `insert_resource()` return values are ignored; conflicts in the resource tree may go unnoticed before the old resource is removed.
- DT and ACPI data differ: ACPI omits the function table and wake map and reserves several GPIOs. Any shared-core assumption that functions or wake data always exist could affect ACPI operation.
- The table is large and index-sensitive. Pin array indexes, `gpioN_pins`, group array order, function enum values, and `msm_mux_*` names must remain aligned.
- `PINGROUP_OFFSET()` encodes many nonuniform offsets near the end of the GPIO range. A wrong offset can silently target the wrong register block.
- Special SD/UFS groups have many bit fields set to `-1`; consumers must treat them as limited-capability groups.
- Wake entries include duplicate GPIOs mapped to multiple PDC lines, so wake handling must preserve all intended rows.

## Test Signals

Useful build signals are `W=1`/sparse checks for table initializer mistakes, successful module/platform driver compilation with OF and ACPI enabled, and absence of missing `msm_mux_*` symbols. Runtime signals include successful probe for `qcom,sc8180x-tlmm` DT systems, successful ACPI probe for `QCOM040D`, named tile resources visible to the shared core, GPIO line count/reservation behavior matching firmware expectations, pinmux state application from device tree, GPIO direction/value tests through gpiolib, and wake-capable GPIO suspend/resume tests using the PDC map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc8180x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc8280xp-lpass-lpi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc8280xp-lpass-lpi.c

## Purpose

`pinctrl-sc8280xp-lpass-lpi.c` describes the Low Power Island LPASS audio pin controller for Qualcomm SC8280XP. It is a compact variant table for the shared `pinctrl-lpass-lpi` driver, covering 19 LPI GPIOs used by SoundWire, DMIC, I2S/MI2S, WSA SoundWire, and external MCLK functions. The file contains no custom register access or probe logic; all behavior is delegated to the generic LPI pinctrl core.

## Important APIs, Types, and Data

- Includes `pinctrl-lpass-lpi.h`, which provides `struct lpi_pingroup`, `struct lpi_function`, `struct lpi_pinctrl_variant_data`, `LPI_PINGROUP()`, and `LPI_FUNCTION()`.
- `enum lpass_lpi_functions` defines mux IDs for the exported audio functions plus `gpio` and placeholder `__` entries used by the macro-generated group tables.
- `sc8280xp_lpi_pins[]` exposes pins `gpio0` through `gpio18`.
- Per-function group arrays map function names to legal pin names, for example `swr_tx_data` on `gpio1`, `gpio2`, and `gpio14`, `qua_mi2s_data` on `gpio2` through `gpio5`, and `ext_mclk1_*` on selected pins.
- `sc8280xp_groups[]` defines one `LPI_PINGROUP()` per pin. The second macro argument is either a slew-rate register selector/offset or `LPI_NO_SLEW`. The function slots encode the mux alternatives accepted by the shared LPI core.
- `sc8280xp_functions[]` lists each selectable function with `LPI_FUNCTION()`.
- `sc8280xp_lpi_data` packages pins, groups, and functions for the generic driver.
- `lpi_pinctrl_of_match[]` binds `qcom,sc8280xp-lpass-lpi-pinctrl` and attaches `sc8280xp_lpi_data`.
- `lpi_pinctrl_driver` uses `lpi_pinctrl_probe` and `lpi_pinctrl_remove` directly.

## Control Flow

`module_platform_driver(lpi_pinctrl_driver)` registers the platform driver. Matching is OF-only. On probe, the generic LPI probe reads the matched variant data pointer, registers pinctrl/pinmux/gpio resources, and uses this file's static tables to service mux and configuration requests. Remove is delegated to `lpi_pinctrl_remove`.

## State and Persistence

This file holds only immutable descriptor tables. Runtime state, register mappings, GPIO chip state, and pinctrl handles are owned by the shared LPI core and device-managed resources. Pin mux and configuration settings persist in LPASS LPI hardware registers until changed or reset.

## Dependencies and Integration Points

The driver depends on the platform bus, OF matching, Linux module infrastructure, gpiolib, and the Qualcomm LPI pinctrl core. It integrates with SC8280XP audio device-tree nodes that reference the LPI pinctrl provider for SoundWire, DMIC, I2S, MI2S, WSA, and MCLK pin states. Function/group names must match binding and board DTS usage.

## Risks and Edge Cases

- The table relies on exact mux-slot ordering expected by LPI hardware; wrong slot placement can select the wrong audio function.
- Several pins share related functions, such as SoundWire data lanes and MI2S data lanes, so a group membership error may only appear when a specific audio topology is enabled.
- `LPI_NO_SLEW` pins cannot be slew-configured; DTS states expecting slew control on those pins would not behave as intended.
- There is no custom validation in this file, so errors are usually discovered as failed audio routing, failed pin state selection, or silent hardware misconfiguration.

## Test Signals

Build coverage should confirm all `LPI_MUX_*` symbols referenced by `LPI_PINGROUP()` exist and the variant data compiles. Runtime signals include successful probe of `qcom,sc8280xp-lpass-lpi-pinctrl`, expected pins/functions under debugfs pinctrl output, successful application of board audio pinctrl states, and audio path tests for SoundWire, DMIC, I2S/MI2S, WSA, and MCLK consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc8280xp-lpass-lpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc8280xp.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc8280xp.c

## Purpose

`pinctrl-sc8280xp.c` is the Qualcomm SC8280XP TLMM pinctrl/GPIO driver data source for the shared MSM pinctrl core. It describes a large application-processor TLMM block with GPIOs, alternate functions, wake interrupt mapping, eGPIO support, two UFS reset groups, and SDC/QDSD groups. The file is almost entirely static SoC metadata plus the platform driver wrapper that registers the metadata with the common MSM pinctrl implementation.

## Important APIs, Types, and Data

- Uses `pinctrl-msm.h` and exports a `struct msm_pinctrl_soc_data` named `sc8280xp_pinctrl`.
- `PINGROUP()` generates normal GPIO-capable `struct msm_pingroup` records with eight mux slots, standard TLMM register offsets (`REG_SIZE * id`), GPIO input/output bits, IRQ bits, and eGPIO presence/enable bits.
- `SDC_QDSD_PINGROUP()` handles SD-card/QDSD groups with pull/drive configuration but no mux, GPIO, or IRQ capability.
- `UFS_RESET()` handles `ufs_reset` and `ufs1_reset` pseudo groups with output control at fixed offsets and no normal IRQ/mux fields.
- `sc8280xp_pins[]` contains GPIO descriptors and special non-GPIO descriptors up to the SDC groups.
- `DECLARE_MSM_GPIO_PINS()`, `enum sc8280xp_functions`, per-function `*_groups[]`, `sc8280xp_functions[]`, and `sc8280xp_groups[]` define the pin/function/group graph used by pinctrl clients.
- Function coverage includes QUP serial engines, I3C, QSPI, PCIe clock requests, USB/USB4 sideband pins, display hotplug and vsync, Ethernet MAC/RGMII, LPASS audio, QDSS, DDR test/debug functions, PRNG/PLL/test hooks, and eGPIO.
- `sc8280xp_pdc_map[]` maps many TLMM GPIO lines to PDC wake IRQ numbers.
- `sc8280xp_pinctrl` sets `.ngpios = 230`, includes the wake map, and sets `.egpio_func = 7`, matching `PINGROUP()`'s eGPIO mux slot placement and eGPIO register bit fields.
- OF matching binds `qcom,sc8280xp-tlmm`; the platform driver name is `sc8280xp-tlmm`.

## Control Flow

The driver registers at `arch_initcall()` with `platform_driver_register()`. OF matching instantiates the platform device for `qcom,sc8280xp-tlmm`. Probe is a thin wrapper that calls `msm_pinctrl_probe(pdev, &sc8280xp_pinctrl)`. From that point, the shared MSM core maps resources, registers the pinctrl device, GPIO chip, and IRQ support, and interprets the static tables when clients request pin states or GPIO operations. Module exit unregisters the platform driver.

## State and Persistence

This source stores no mutable driver-local state. Runtime state is held in the generic MSM pinctrl instance created during probe. Hardware configuration persists in TLMM registers. The static SoC table is not modified after compile time. eGPIO state is controlled through the common core using the mux slot and register bit metadata in each pingroup.

## Dependencies and Integration Points

The file depends on Linux platform/OF/module support and the common Qualcomm MSM pinctrl core. It integrates with SC8280XP device trees, pinctrl clients for serial, storage, display, USB, Ethernet, PCIe, debug, and audio peripherals, gpiolib users, and interrupt wake paths through PDC. The `.egpio_func` field and per-group `.egpio_enable`/`.egpio_present` bits require shared-core support for eGPIO handling.

## Risks and Edge Cases

- eGPIO support is table-driven and sensitive to mux slot numbering. `.egpio_func = 7` must match the final function slot in each relevant `PINGROUP()`.
- The file has a very large function/group surface. Typos in function names or group membership can break only one peripheral mode and may not be caught by generic compile tests.
- `.ngpios = 230` excludes the special SDC/UFS descriptors even though the pin array extends beyond ordinary GPIOs; off-by-one changes here can expose non-GPIO groups as GPIO lines or hide valid GPIOs.
- PDC wake map correctness is critical for suspend/resume wake behavior and is hard to verify without hardware.
- Special UFS and SDC groups intentionally disable many bit fields with `-1`; they must only be used through supported configuration paths.

## Test Signals

Build signals include successful compile with no missing `msm_mux_*` references and no initializer warnings. Runtime signals include successful probe for `qcom,sc8280xp-tlmm`, expected 230 GPIO lines exposed by gpiolib, debugfs visibility of functions and groups, pinctrl state application for QUP/I3C/QSPI/PCIe/USB/display/Ethernet/storage/audio clients, eGPIO selection tests where board hardware uses external GPIO functionality, and wake-from-suspend tests for GPIOs listed in `sc8280xp_pdc_map[]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc8280xp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm660-lpass-lpi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm660-lpass-lpi.c

## Purpose

`pinctrl-sdm660-lpass-lpi.c` describes the Qualcomm SDM660 LPASS Low Power Island pin controller variant for the shared LPI pinctrl driver. It exposes 32 LPI GPIOs and maps audio functions for PDM, DMIC, MCLK, comparator receive, and GPIO use. A source comment notes the driver is based on limited downstream information and requests schematic verification, which makes the table provenance an explicit research risk.

## Important APIs, Types, and Data

- Uses `pinctrl-lpass-lpi.h` and the LPI core macros/types.
- `enum lpass_lpi_functions` defines mux IDs for `comp_rx`, `dmic1_*`, `dmic2_*`, `mclk0`, `pdm_*`, `gpio`, and placeholder `__`.
- `sdm660_lpi_pinctrl_pins[]` defines `gpio0` through `gpio31`.
- Per-function group arrays map audio functions to pins: PDM clock/MCLK around `gpio18`, PDM sync/tx/rx around `gpio19` to `gpio25`, comparator RX on `gpio22`/`gpio24`, and DMIC functions on `gpio26` to `gpio29`.
- `sdm660_lpi_pinctrl_groups[]` uses `LPI_PINGROUP_OFFSET()` for every group, with explicit register offsets from `0x0000` through `0xb010`. Pins `0` to `17`, `30`, and `31` are described as GPIO-only/no alternate function in the table.
- `sdm660_lpi_pinctrl_functions[]` publishes the named alternate functions.
- `sdm660_lpi_pinctrl_data` sets `LPI_FLAG_SLEW_RATE_SAME_REG | LPI_FLAG_USE_PREDEFINED_PIN_OFFSET`, telling the core that slew configuration shares the same register and group offsets are precomputed rather than derived.
- OF match binds `qcom,sdm660-lpass-lpi-pinctrl`; the platform driver delegates probe/remove to the LPI core.

## Control Flow

The `module_platform_driver()` macro registers the platform driver. When a matching OF node appears, the platform bus invokes `lpi_pinctrl_probe`, which consumes `sdm660_lpi_pinctrl_data` from the match table. All pinctrl registration, GPIO registration, and register I/O are handled by the common LPI driver. Removal calls `lpi_pinctrl_remove`.

## State and Persistence

This file has only static variant metadata. Runtime state is allocated and owned by the LPI pinctrl core. LPASS LPI hardware registers hold the persistent pin mux/configuration state until reconfigured or reset. Because predefined offsets are used, the static offset table is effectively part of the hardware ABI for this variant.

## Dependencies and Integration Points

The source depends on the Linux platform and OF subsystems and on Qualcomm's LPI pinctrl implementation. It integrates with SDM660 audio DTS pinctrl consumers, especially PDM/DMIC capture/playback and MCLK users. The function and group names must match device-tree pin state names. The offset flags require the shared LPI core to interpret explicit offsets correctly.

## Risks and Edge Cases

- The explicit note about limited downstream information means mux assignments and offsets have higher validation risk than table data sourced from full documentation.
- `LPI_FLAG_USE_PREDEFINED_PIN_OFFSET` makes each offset entry critical; any typo routes register writes to the wrong pin.
- Many pins are GPIO-only placeholders with explicit offsets. Clients selecting unavailable alternate functions should fail rather than silently misconfigure.
- `LPI_FLAG_SLEW_RATE_SAME_REG` changes how the core writes slew fields; using the wrong flag can corrupt unrelated config bits.
- Audio failures may be topology-specific, for example PDM RX lanes on `gpio21`, `gpio23`, and `gpio25` may need separate board-level validation.

## Test Signals

Compile tests should verify all macro references resolve. Runtime tests should verify probe of `qcom,sdm660-lpass-lpi-pinctrl`, pinctrl debugfs pin/function visibility, GPIO-only pins behaving as GPIOs, and audio validation for PDM clock/sync/tx/rx, DMIC1/DMIC2, comparator RX, and MCLK0. Register trace or hardware readback is especially useful because this variant depends on predefined offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm660-lpass-lpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm660.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm660.c

## Purpose

`pinctrl-sdm660.c` is the Qualcomm SDM660/SDM630 TLMM pinctrl data driver for the shared MSM pinctrl core. It describes 114 ordinary GPIOs plus SD-card groups, the three TLMM tiles, alternate functions, and an MPM wake interrupt map. The source is table-oriented with a thin platform driver wrapper.

## Important APIs, Types, and Data

- Includes `pinctrl-msm.h` and provides `sdm660_pinctrl`, a `struct msm_pinctrl_soc_data`.
- `sdm660_tiles[]` names `north`, `center`, and `south`; the enum values are embedded in each `PINGROUP()` row.
- `PINGROUP()` generates standard TLMM groups with ten mux slots, register offsets based on `REG_SIZE * id`, the tile selector, GPIO data bits, and IRQ bit positions.
- `SDC_QDSD_PINGROUP()` defines non-GPIO SD card groups with pull/drive fields and disabled mux/GPIO/IRQ fields.
- `sdm660_pins[]` defines GPIO descriptors for GPIO 0 through 113 and special SD card descriptors for SDC1/SDC2 clock, command, data, and SDC1 return clock.
- `DECLARE_MSM_GPIO_PINS()`, `enum sdm660_functions`, per-function group arrays, `sdm660_functions[]`, and `sdm660_groups[]` describe the multiplexing graph.
- Function coverage includes BLSP/QUP, CCI, camera clocks, MDP vsync, TSIF, MI2S/SLIMbus/LPASS audio, UIM, WLAN/ADC/test signals, QDSS, USB, PCIe, SD write protect, and debug/test hooks.
- `sdm660_mpm_map[]` maps GPIOs to MPM wake interrupt numbers.
- `sdm660_pinctrl` sets pins, functions, groups, `.ngpios = 114`, tiles, and the MPM wake map.
- OF matching supports both `qcom,sdm660-pinctrl` and `qcom,sdm630-pinctrl`.

## Control Flow

`sdm660_pinctrl_init()` registers the platform driver at `arch_initcall()`. OF match creates the platform device for either SDM660 or SDM630 compatible strings. Probe calls `msm_pinctrl_probe(pdev, &sdm660_pinctrl)`, after which the shared MSM core performs resource mapping, pinctrl/gpio registration, and IRQ setup using this file's static data. Exit unregisters the platform driver.

## State and Persistence

The source contains no driver-local mutable state. Static tables define the SoC contract. Runtime state is created by the MSM core and hardware state persists in TLMM registers. Wake state uses MPM mapping data supplied here and is managed by the core and interrupt subsystem.

## Dependencies and Integration Points

The file depends on the Linux OF/platform/module stack and the common MSM pinctrl core. It integrates with SDM660 and SDM630 device trees, gpiolib, pinctrl consumers for camera/display/audio/serial/storage/debug peripherals, and MPM wake interrupt routing. Tile names must match memory resource names in the platform description.

## Risks and Edge Cases

- One data table is used for both SDM660 and SDM630 compatibles; any silicon differences not represented here can cause board-specific pinmux or wake issues.
- Tile assignment is part of each pingroup. A wrong tile can map otherwise correct register offsets into the wrong memory region.
- Wake mapping uses MPM rather than PDC; incorrect GPIO-to-MPM rows break suspend wake without affecting normal GPIO tests.
- `.ngpios = 114` must remain aligned with the ordinary GPIO range, excluding SDC-only groups.
- SD card groups disable most GPIO/IRQ fields and should only be used for supported pull/drive configuration.

## Test Signals

Build signals include successful compilation and no missing `msm_mux_*` references. Runtime signals include driver probe on both `qcom,sdm660-pinctrl` and `qcom,sdm630-pinctrl` boards, expected 114 GPIO lines, debugfs function/group visibility, pin state application for serial/camera/display/audio/storage clients, SD card pull/drive behavior, and suspend/resume wake tests for entries in `sdm660_mpm_map[]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm660.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm670-lpass-lpi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm670-lpass-lpi.c

## Purpose

`pinctrl-sdm670-lpass-lpi.c` describes the Qualcomm SDM670 LPASS LPI pin controller variant for the shared LPI pinctrl driver. It exposes 32 LPI GPIOs and audio/control functions including PDM, DMIC, I2S1, SLIMbus clock, MCLK0, comparator receive, and an LPASS codec reset function. It is a static descriptor file with no custom probe logic.

## Important APIs, Types, and Data

- Includes `pinctrl-lpass-lpi.h`.
- `enum lpass_lpi_functions` declares mux IDs for `comp_rx`, `dmic1_*`, `dmic2_*`, `i2s1_*`, `lpi_cdc_rst`, `mclk0`, `pdm_*`, `slimbus_clk`, `gpio`, and placeholder `__`.
- `sdm670_lpi_pinctrl_pins[]` defines pins `gpio0` through `gpio31`.
- Per-function group arrays bind functions to pins: I2S1 on `gpio8` to `gpio11`, SLIMbus clock on `gpio18`, MCLK/PDM around `gpio19` to `gpio25`, DMIC on `gpio26` to `gpio29`, and `lpi_cdc_rst` on `gpio29`.
- `sdm670_lpi_pinctrl_groups[]` contains one `LPI_PINGROUP()` per pin; many early and trailing pins expose no alternate functions, while audio-capable pins include one or more mux slots.
- `sdm670_lpi_pinctrl_functions[]` publishes the alternate functions to pinctrl clients.
- `sdm670_lpi_pinctrl_data` provides pins/groups/functions and sets `LPI_FLAG_SLEW_RATE_SAME_REG`.
- OF matching binds `qcom,sdm670-lpass-lpi-pinctrl`, with probe/remove delegated to the LPI core.

## Control Flow

The platform driver is registered via `module_platform_driver()`. On OF match, `lpi_pinctrl_probe` consumes the variant data and registers the provider. Pin state selection, GPIO operations, and register access are implemented by the common LPI pinctrl core. Remove is handled by `lpi_pinctrl_remove`.

## State and Persistence

This source is immutable table data only. Device state lives in the generic LPI core instance. Pin settings persist in LPASS LPI hardware registers. The slew-rate flag changes core write behavior but no local state is updated in this file.

## Dependencies and Integration Points

The driver depends on platform/OF/module support and the Qualcomm LPI pinctrl core. It integrates with SDM670 audio and codec-related device-tree pin states. Function/group names are part of the DTS-facing ABI for audio routing and codec reset control.

## Risks and Edge Cases

- `gpio29` supports both `dmic2_data` and `lpi_cdc_rst`; board pin states must choose the correct mux for the audio or reset use case.
- `LPI_FLAG_SLEW_RATE_SAME_REG` must match hardware layout; otherwise configuration writes may affect the wrong bits.
- Many GPIOs have no alternate functions, so attempting to use them for unsupported audio routes should fail predictably.
- Audio table errors may not show in generic GPIO tests; they require active audio/codec pin states.

## Test Signals

Build checks should catch unresolved LPI mux names. Runtime signals include successful probe for `qcom,sdm670-lpass-lpi-pinctrl`, expected 32 pins in debugfs, correct function/group listings, and board-level validation of I2S1, PDM, DMIC, SLIMbus clock, MCLK0, comparator RX, and codec reset pin states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm670-lpass-lpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm670.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm670.c

## Purpose

`pinctrl-sdm670.c` is the Qualcomm SDM670 TLMM pinctrl/GPIO driver data source for the shared MSM pinctrl core. It describes the SDM670 TLMM register layout, pin descriptors, alternate functions, dummy/uncontrolled groups, UFS and SDC groups, reserved GPIOs, PDC wake mapping, and driver binding. The source has a simple platform probe wrapper but important table-level hardware policy.

## Important APIs, Types, and Data

- Includes `pinctrl-msm.h` and provides `sdm670_pinctrl`, a `struct msm_pinctrl_soc_data`.
- Base constants `NORTH`, `SOUTH`, and `WEST` are absolute TLMM tile offsets folded directly into each group register address rather than represented as named tile resources.
- `PINGROUP()` creates normal GPIO groups with ten mux slots and standard TLMM mux/config/IRQ bit positions.
- `PINGROUP_DUMMY()` defines pin groups that have no controllable registers or alternate functions; all control bits are set to `-1`.
- `SDC_QDSD_PINGROUP()` and `UFS_RESET()` define special storage-related groups with limited capabilities.
- `sdm670_pins[]`, `DECLARE_MSM_GPIO_PINS()`, per-function group arrays, `enum sdm670_functions`, `sdm670_functions[]`, and `sdm670_groups[]` provide the pinctrl database.
- Function coverage includes QUP, camera/CCI, MDP/eDP, TSIF, PCIe, USB PHY/test, UIM, LPASS/MI2S/SLIMbus/audio, QDSS, DDR/test, WLAN ADC, GPS/navigation, and modem-related signals.
- `sdm670_reserved_gpios[]` reserves GPIOs 58-64, 69-74, and 104, terminated by `-1`.
- `sdm670_pdc_map[]` maps GPIO lines to PDC wake IRQs.
- `sdm670_pinctrl` sets `.ngpios = 151`, reserved GPIOs, wake map, and `.wakeirq_dual_edge_errata = true`.
- OF matching binds `qcom,sdm670-tlmm`.

## Control Flow

The driver registers at `arch_initcall()` and unregisters at module exit. OF matching creates the platform device, and `sdm670_pinctrl_probe()` delegates directly to `msm_pinctrl_probe(pdev, &sdm670_pinctrl)`. The shared MSM core maps registers, registers pinctrl/GPIO/IRQ providers, applies reserved GPIO policy, and uses the wake map and dual-edge errata flag for interrupt behavior.

## State and Persistence

There is no mutable local state. Static tables define the hardware model. Runtime state belongs to the MSM core, and TLMM register values persist in hardware. Reserved GPIOs constrain gpiolib exposure/usage through the core. Dummy groups intentionally represent pins that cannot be controlled by this driver.

## Dependencies and Integration Points

The file depends on Linux platform/OF/module infrastructure and the Qualcomm MSM pinctrl core. It integrates with SDM670 device trees, pinctrl clients, gpiolib, and PDC wake interrupt support. The reserved GPIO list and dummy groups are important integration boundaries with firmware or inaccessible hardware.

## Risks and Edge Cases

- Absolute base offsets are embedded in every group; a base constant error affects an entire tile's register accesses.
- Dummy groups must remain nonfunctional. Accidentally adding control bits could cause writes to offset zero or unrelated registers.
- Reserved GPIO handling is required to avoid exposing firmware-owned or unavailable lines.
- Dual-edge wake errata handling changes interrupt programming; omitting or misusing the flag can produce missed or repeated wake events.
- `.ngpios = 151` excludes special groups after the GPIO range; changing this can expose UFS/SDC descriptors as normal GPIOs.
- Wake map validation requires suspend/resume hardware testing and will not be proven by compile coverage.

## Test Signals

Useful signals include compile success, successful probe for `qcom,sdm670-tlmm`, expected GPIO count with reserved GPIOs unavailable, debugfs confirmation of dummy/special groups, pinctrl state application for QUP/camera/display/audio/storage consumers, GPIO IRQ tests including dual-edge cases, and suspend/resume wake tests for GPIOs listed in `sdm670_pdc_map[]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm670.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm845.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm845.c

## Purpose

`pinctrl-sdm845.c` is the Qualcomm SDM845 TLMM pinctrl/GPIO data driver for the shared MSM pinctrl core. It describes SDM845 GPIOs, alternate functions, storage special groups, UFS reset, PDC wake interrupt mapping, ACPI-specific reserved GPIO handling, and both DT and ACPI platform binding. Unlike many table-only TLMM files, its probe path explicitly chooses between DT and ACPI SoC data.

## Important APIs, Types, and Data

- Includes `linux/acpi.h` plus the standard module/OF/platform headers and `pinctrl-msm.h`.
- Base constants `NORTH`, `SOUTH`, and `EAST` are absolute register offsets for TLMM regions.
- `PINGROUP()` creates normal `struct msm_pingroup` records with eleven mux slots and standard GPIO/IRQ bit positions.
- `SDC_QDSD_PINGROUP()` describes SDC2 clock/command/data groups with pull/drive support but no mux/GPIO/IRQ behavior.
- `UFS_RESET()` describes the UFS reset pseudo group at fixed registers.
- `sdm845_pins[]`, `DECLARE_MSM_GPIO_PINS()`, `enum sdm845_functions`, function group arrays, `sdm845_functions[]`, and `sdm845_groups[]` define the full pinctrl graph.
- Function coverage includes QUP, CCI/camera, MDP/eDP, TSIF, PCIe, USB PHY/test, UIM, LPASS/MI2S/SLIMbus/audio, QDSS, DDR/test, WLAN ADC, GPS/navigation, modem signals, and other SoC test/debug functions.
- `sdm845_acpi_reserved_gpios[]` reserves GPIOs `0-3` and `81-84` for ACPI systems.
- `sdm845_pdc_map[]` maps GPIO lines to PDC wake IRQs.
- `sdm845_pinctrl` is the DT path with functions, wake map, 151 GPIOs, and `.wakeirq_dual_edge_errata = true`.
- `sdm845_acpi_pinctrl` is the ACPI path with pins/groups, reserved GPIOs, and 150 GPIOs but no function table or wake map.
- ACPI matching uses ID `QCOM0217`; OF matching uses `qcom,sdm845-pinctrl`.
- The platform driver supplies `&msm_pinctrl_dev_pm_ops`, integrating generic suspend/resume handling.

## Control Flow

`sdm845_pinctrl_init()` registers the platform driver at `arch_initcall()`. In `sdm845_pinctrl_probe()`, DT devices call `msm_pinctrl_probe()` with `sdm845_pinctrl`. ACPI devices detected by `has_acpi_companion()` call `msm_pinctrl_probe()` with `sdm845_acpi_pinctrl`. Devices with neither firmware description fail with `-EINVAL` after logging an error. The shared MSM core then owns all pinctrl, GPIO, IRQ, and PM behavior. Exit unregisters the platform driver.

## State and Persistence

The file contains immutable hardware tables only. The generic MSM core owns runtime state and maps TLMM registers. Pin mux/configuration and interrupt settings persist in hardware registers. ACPI operation changes exposed capabilities through a separate SoC-data table rather than modifying the DT table in place.

## Dependencies and Integration Points

The source depends on Linux ACPI, OF, platform driver, module, pinctrl, GPIO, IRQ, and PM infrastructure through the MSM core. It integrates with both `qcom,sdm845-pinctrl` device trees and ACPI `QCOM0217` platforms. PDC wake mapping and dual-edge errata handling integrate with suspend/resume wake support. The ACPI table's reserved GPIOs integrate with firmware ownership constraints.

## Risks and Edge Cases

- DT and ACPI data expose different capabilities. ACPI lacks function and wake map data and reserves GPIOs; consumers must not assume the DT function table is present on ACPI systems.
- The probe branch logs and fails if neither OF nor ACPI is present, which is correct but makes firmware matching mandatory.
- Absolute base offsets in group tables can silently misroute register accesses if a tile base is wrong.
- `.wakeirq_dual_edge_errata = true` is essential for correct dual-edge wake handling on affected GPIOs.
- `.ngpios` differs between DT and ACPI (`151` vs `150`), and the pin array also includes UFS/SDC descriptors. Off-by-one changes can expose unsupported pins.
- Special SDC/UFS groups disable many bit fields and must not be treated as normal GPIO-capable groups.

## Test Signals

Compile tests should cover both OF and `CONFIG_ACPI` builds. Runtime signals include successful probe for DT compatible `qcom,sdm845-pinctrl` and ACPI ID `QCOM0217`, correct GPIO counts/reservations for each firmware path, pinctrl debugfs function/group visibility on DT systems, ACPI GPIO availability matching reserved lists, pin state application for major peripherals, PM suspend/resume through `msm_pinctrl_dev_pm_ops`, GPIO IRQ tests including dual-edge behavior, and PDC wake tests using `sdm845_pdc_map[]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdm845.c -->
