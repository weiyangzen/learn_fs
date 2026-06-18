# subset-b-005065 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-39x.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-39x.c

Purpose: this file is the Armada 39x SoC table driver for the shared MVEBU pinctrl core. It describes the 60 MPP pins on mv88f6920, mv88f6925, and mv88f6928 devices and maps each pin's 4-bit mux value to functions such as GPIO, UART, I2C, SPI, SDIO, SMI/XSMI, SATA presence, PCIe reset/clock request, GE, LED, TDM, audio, NAND, and DRAM signals.

Important APIs, types, and functions: the central data is `armada_39x_mpp_modes[]`, built from `MPP_MODE()` and `MPP_VAR_FUNCTION()` entries with variant masks `V_88F6920`, `V_88F6925`, and `V_88F6928`. `armada_39x_mpp_controls[]` exposes pins 0-59 as one unnamed `mvebu_mmio_mpp_ctrl` range, so the core creates one group per pin (`mpp0` ... `mpp59`). `armada_39x_mpp_gpio_ranges[]` registers two GPIO ranges. `armada_39x_pinctrl_probe()` fills `mvebu_pinctrl_soc_info` and calls `mvebu_pinctrl_simple_mmio_probe()`.

Control flow: the builtin platform driver matches one of three compatible strings, derives the variant from `device_get_match_data()`, installs the static controls, modes, and GPIO ranges as platform data, maps the single MMIO resource through the shared helper, and delegates registration to `mvebu_pinctrl_probe()`. Runtime mux requests are handled entirely by the core: DT `marvell,function` plus `marvell,pins` maps to a setting, and the core writes the selected nibble through `mvebu_mmio_mpp_ctrl_set()`.

State and persistence behavior: there is no private runtime state beyond the shared static `armada_39x_pinctrl_info` and the device-managed MMIO control-data array allocated by the simple probe helper. Pin state persists in the hardware MPP registers until changed by pinctrl or reset. There is no suspend/resume save path in this file.

Dependencies and integration points: this driver depends on the MVEBU pinctrl core, platform/OF matching, MMIO resource mapping, and Linux pinctrl/GPIO range registration. Consumers are board DTS pinctrl nodes using function names exactly as listed in the table.

Risks and test signals: the main risk is table correctness. Variant masks gate SATA, TDM, audio, and higher-end pins, so the same DTS can be accepted or rejected depending on compatible. `soc->nmodes` is set from the control pin count, which assumes a one-to-one mode table for pins 0-59. Test by booting each compatible, applying representative UART/I2C/SPI/SDIO/GE/SATA/PCIe muxes, checking debugfs available functions, and verifying GPIO ranges 0-31 and 32-59.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-39x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-ap806.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-ap806.c

Purpose: this is the Armada AP806 pinctrl table driver. It exposes the application processor's 20 MPP pins to the MVEBU pinctrl core, covering GPIO plus SDIO, SPI0, I2C0, UART0, and UART1 functions.

Important APIs, types, and functions: `armada_ap806_mpp_modes[]` is the complete pin/function table. `armada_ap806_mpp_controls[]` defines pins 0-19 as an unnamed `mvebu_regmap_mpp_ctrl` range. `armada_ap806_mpp_gpio_ranges[]` maps all 20 pins as GPIO-capable. `armada_ap806_pinctrl_probe()` validates that the pinctrl node has a parent syscon device, populates `armada_ap806_pinctrl_info`, and invokes `mvebu_pinctrl_simple_regmap_probe(pdev, parent, 0)`.

Control flow: after OF match on `marvell,ap806-pinctrl`, probe expects the parent node to provide the syscon regmap holding the MPP registers. The shared regmap helper creates one control-data entry per control with offset zero, then the common MVEBU core builds groups, functions, DT maps, pinmux operations, pinconf operations, and GPIO ranges. All runtime get/set operations are regmap reads or masked writes of 4-bit MPP fields.

State and persistence behavior: software state is the static SoC info plus device-managed regmap control data. Hardware mux values persist in the parent syscon registers. There are no variants, no explicit locking in this file, and no suspend/resume handling.

Dependencies and integration points: dependencies are the parent syscon/MFD device, MVEBU core, OF platform matching, and standard pinctrl clients. Integration is through DTS `marvell,function` and `marvell,pins`; the exposed names include a likely typo-like subname `i2c0` `"sdk"` for MPP5, which is part of the ABI once consumed by debug output or documentation.

Risks and test signals: probe fails with `-ENODEV` if the DT hierarchy omits the parent syscon. Because all pins share offset zero, any future AP806 register-layout change would need a different offset or control split. Test signals include successful regmap lookup, SDIO 8-bit and reset/power pins, SPI0 chip selects, UART0/1 muxing, GPIO request on all 20 pins, and DT rejection for unsupported functions on GPIO-only pins 13-18.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-ap806.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-cp110.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-cp110.c

Purpose: this driver describes the Armada CP110/CP115 pin controller used by Armada 7K and 8K communication processor blocks. It provides a single 63-pin MPP table with functions for device bus, audio, GE/XG/MII, TDM, MSS peripherals, PTP, PCIe, SATA, SDIO, UART, LED, SyncE, and CP-to-CP links.

Important APIs, types, and functions: `armada_cp110_mpp_modes[]` holds pin modes for MPP0-62. The variant enum distinguishes `V_ARMADA_7K`, `V_ARMADA_8K_CPM`, `V_ARMADA_8K_CPS`, and `V_CP115_STANDALONE`. `armada_cp110_mpp_controls[]` is one unnamed `mvebu_regmap_mpp_ctrl` range. `mvebu_pinctrl_assign_variant()` mutates all settings in a mode to the computed availability mask. `armada_cp110_pinctrl_probe()` allocates per-device `mvebu_pinctrl_soc_info` and calls the simple regmap probe against the parent syscon.

Control flow: probe matches the compatible to a CP flavor, validates a parent syscon, allocates SoC info, and iterates the mode table assigning availability by MPP index: 0-31 are 7K/CPS/standalone, 32-38 are 7K/CPM/standalone, 39-43 are CPM/standalone only, and 44-62 are 7K/CPM/standalone. The common MVEBU core then filters unsupported settings by `soc->variant`, builds unique function lists, and programs 4-bit mux fields through regmap.

State and persistence behavior: the per-device SoC info is managed, but the mode table itself is static and is rewritten at probe with variant masks. Hardware state persists in syscon registers. No GPIO ranges are registered in this file, so GPIO integration depends on the pinctrl mux table rather than explicit ranges here.

Dependencies and integration points: dependencies are parent syscon regmap access, MVEBU core semantics, OF compatibles for Armada 7K/8K CPM/CPS and CP115 standalone, and DTS pinctrl function/group naming. It integrates with many platform controllers because CP110 carries most board-facing I/O.

Risks and test signals: mutating the global mode table at probe is risky if multiple CP110 instances with different variants probe in one kernel; the last probe's variant assignments affect the shared array used by all devices. The comment says MPP39-43 are unavailable on Armada 7K, and that policy is implemented only by the probe-time mutation. Test both CPM and CPS instances in an Armada 8K system, check function availability in debugfs for MPP39-43, validate SDIO pins 56-62, and exercise regmap write/readback on a few mux values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-cp110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-xp.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-xp.c

Purpose: this file supports Armada XP and related 98DX switch SoC pinmuxing. It handles mv78230 with 49 pins, mv78260/mv78460 with 67 pins, and 98DX3236/3336/4251-style devices with a separate 33-pin table.

Important APIs, types, and functions: `armada_xp_mpp_modes[]` defines the Armada XP table, while `mv98dx3236_mpp_modes[]` defines the switch-family table. Variant masks include `V_MV78230_PLUS`, `V_MV78260_PLUS`, and `V_98DX3236_PLUS`. Per-variant `mvebu_mpp_ctrl` and `pinctrl_gpio_range` arrays describe pin count and GPIO range splits. `armada_xp_pinctrl_probe()` selects the table/ranges by compatible. `armada_xp_pinctrl_suspend()` and `armada_xp_pinctrl_resume()` save and restore raw MPP registers through `mpp_saved_regs`.

Control flow: OF match provides a variant. Probe selects controls, modes, GPIO ranges, computes the number of MPP registers, allocates the save buffer, attaches SoC info as platform data, and uses the simple MMIO probe. Runtime muxing is shared-core nibble read/write. Legacy platform suspend reads each MPP register from the first control base; resume writes the saved values back.

State and persistence behavior: the selected SoC info is stored in a static `armada_xp_pinctrl_info`, and suspend state is held in the global `mpp_saved_regs` buffer allocated for the probed device. Hardware muxing persists in MMIO registers but can be restored after suspend. The global buffer/static info design assumes one active instance.

Dependencies and integration points: dependencies are MMIO MPP registers, platform PM callbacks, the MVEBU pinctrl core, and DTS compatibles. Integrations include Ethernet, LCD, SPI, SDIO, UART, TDM, SATA presence/activity, PCIe clock/reset, NAND/device bus, and switch-specific SMI/dev pins.

Risks and test signals: the static save buffer and static SoC info are not multi-instance friendly. Suspend/resume assumes `soc->control_data[0].base` is valid and that `soc->nmodes` maps to contiguous 4-bit registers. Variant table correctness is important because some pins are GPO only and some 98DX4251-only SDIO functions share values with other functions. Test each compatible, GPIO ranges at 0/32/64 boundaries, switch-family GPO behavior, and suspend/resume register restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-xp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-dove.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-dove.c

Purpose: this is the Dove SoC pinctrl driver, including both ordinary MPP nibble muxing and several Dove-specific mux controls spread across PMU, MPP4, global configuration, SSP, TWSI, NAND, and audio registers.

Important APIs, types, and functions: custom get/set helpers include `dove_pmu_mpp_ctrl_get/set()`, `dove_mpp4_ctrl_get/set()`, `dove_nand_ctrl_get/set()`, `dove_audio0_ctrl_get/set()`, `dove_audio1_ctrl_get/set()`, and `dove_twsi_ctrl_get/set()`. `dove_audio1_ctrl_gpio_req()` and `dove_audio1_ctrl_gpio_dir()` implement special GPIO request/direction semantics for MPP52-57. `dove_mpp_controls[]` mixes unnamed per-pin controls with named grouped controls such as `mpp_camera`, `mpp_sdio0`, `mpp_audio1`, `mpp_nand`, `audio0`, and `twsi`.

Control flow: probe gets and enables the PDMA clock, maps the base MPP resource, allocates control data, maps MPP4 and PMU resources or falls back to hardcoded offsets, obtains `marvell,dove-global-config` syscon or creates an MMIO regmap fallback, warns if firmware omitted resources, and calls `mvebu_pinctrl_probe()`. Runtime muxing can set standard MPP nibbles, PMU-backed function values with `CONFIG_PMU`, grouped GPIO/function selector bits, and multi-bit audio/TWSI combinations.

State and persistence behavior: static globals store `mpp4_base`, `pmu_base`, `gconfmap`, and `clk`. Register state persists across the involved MMIO and syscon blocks. There is no remove path disabling the clock and no suspend/resume in this file.

Dependencies and integration points: dependencies include the MVEBU core, clock framework, MMIO resources, optional legacy hardcoded register layout, regmap/syscon, and global config compatible lookup. Integration is broad: camera, SDIO, SPI, UART1, NAND, PMU wake/power pins, audio0/audio1, SSP, TWSI, SATA, LCD, and GPIO ranges 0-71.

Risks and test signals: fallback hardcoded resources preserve old DTBs but can hide firmware bugs. Several `regmap_read()` calls ignore errors. Audio1 GPIO availability depends on the active compound mode and intentionally does not force GPIO on request. Test modern DT resources versus fallback, PMU functions on MPP0-15, grouped selectors for camera/SDIO/SPI/UART/NAND, audio1 GPIO subsets, TWSI option bits, and PDMA clock availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-dove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-kirkwood.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-kirkwood.c

Purpose: this file is the Kirkwood/Discovery Innovation table driver for MV88F6180, 6190, 6192, 6281, 6282, 98DX4122, and 98DX1135 pinmuxing. It exposes a shared MPP table with variant masks and per-SoC pin counts/GPIO ranges.

Important APIs, types, and functions: the `V()` macro encodes seven variant bits. `mv88f6xxx_mpp_modes[]` lists MPP0-49 with functions including GPIO/GPO, NAND, SPI, UART, SATA, LCD, PTP, TWSI, SDIO, audio, TS, TDM, GE/MII, and switch-specific NAND signals. `mv88f6180_info`, `mv88f6190_info`, `mv88f6192_info`, `mv88f6281_info`, `mv88f6282_info`, `mv98dx4122_info`, and `mv98dx1135_info` bind variants to control ranges and GPIO ranges. `kirkwood_pinctrl_probe()` delegates to `mvebu_pinctrl_simple_mmio_probe()`.

Control flow: OF match returns the prebuilt SoC info. Probe stores it as platform data, maps one MMIO MPP resource through the shared helper, and the MVEBU core filters settings by variant while building functions. Pinmux requests are simple 4-bit MMIO updates.

State and persistence behavior: all SoC data is static. Device-managed control data contains the MMIO base. Hardware mux values persist in MPP registers. There is no suspend/resume, no remove-time state handling, and no runtime PM.

Dependencies and integration points: dependencies are the MVEBU core, OF compatible matching, and one contiguous MPP MMIO resource. The driver integrates with legacy Kirkwood board DTS files and peripheral drivers through named pinctrl functions.

Risks and test signals: the variant mask table is dense and includes duplicate mux values with different names on different variants; table mistakes can silently expose the wrong function. Some variants use GPO where others use GPIO, affecting `gpio_set_direction()` support. Test each compatible's debugfs function list, GPIO ranges with holes and high pins, SDIO/SATA/LCD functions on 6282, switch variants 98DX4122/1135, and unsupported-function rejection on smaller 619x pin counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-kirkwood.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-mvebu.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-mvebu.c

Purpose: this is the shared Marvell MVEBU pinctrl core used by the SoC table drivers in this directory. It turns `mvebu_pinctrl_soc_info` tables into Linux pinctrl groups, functions, pinconf callbacks, pinmux callbacks, DT maps, and GPIO ranges, and provides generic MMIO/regmap MPP field accessors.

Important APIs, types, and functions: runtime structures are `struct mvebu_pinctrl`, `struct mvebu_pinctrl_group`, and `struct mvebu_pinctrl_function`. Hardware helpers are `mvebu_mmio_mpp_ctrl_get/set()` and `mvebu_regmap_mpp_ctrl_get/set()`. Lookup helpers find groups and settings by pin id, name, mux value, or GPIO capability. `mvebu_pinctrl_probe()` is the main registration path. `mvebu_pinctrl_simple_mmio_probe()` and `mvebu_pinctrl_simple_regmap_probe()` allocate control data and then call the main probe.

Control flow: SoC drivers attach `mvebu_pinctrl_soc_info` as platform data. The core validates controls and modes, initializes each control's pin array, creates one group per named control or one group per pin for unnamed controls, attaches mode settings to groups, derives GPIO/GPI/GPO flags from setting names, builds unique functions and their group lists, registers `pinctrl_desc`, then registers GPIO ranges. DT map parsing reads `marvell,function` and `marvell,pins` and emits `PIN_MAP_TYPE_MUX_GROUP` entries. Setting a mux finds the named setting in the target group and writes the setting value through that group's control callback.

State and persistence behavior: state is device-managed memory tied to the platform device. The core does not keep a shadow copy of mux registers; pinconf get reads hardware. Hardware state is persistent register state. There is no locking around register read/modify/write in the generic MMIO path, so serialization relies on pinctrl core usage and platform assumptions.

Dependencies and integration points: dependencies include Linux pinctrl, pinmux, pinconf, GPIO range APIs, OF property parsing, platform devices, MMIO, regmap, and syscon. SoC-specific drivers supply controls, modes, variants, and optional custom GPIO request/direction callbacks.

Risks and test signals: `mvebu_pinctrl_dt_node_to_map()` sets `*num_maps = nmaps` even when invalid pins/functions were skipped, which can leave partially initialized map entries. Function building assumes the number of unique functions is no greater than pin count. GPIO capability is inferred by exact names `gpio`, `gpi`, and `gpo`. Test with valid and invalid DT maps, variant-filtered settings, GPI-only/GPO-only direction requests, debugfs output, regmap error propagation, and concurrent users of adjacent MPP nibbles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-mvebu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-mvebu.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-mvebu.h

Purpose: this header defines the table contract between MVEBU SoC-specific pinctrl drivers and the shared core. It describes MPP control callbacks, mux settings, pin modes, SoC-level pinctrl data, and the macros used to build compact pin/function tables.

Important APIs, types, and functions: `struct mvebu_mpp_ctrl_data` stores either an MMIO base or a regmap plus offset. `struct mvebu_mpp_ctrl` describes a controllable pin or pin group and its get/set/GPIO callbacks. `struct mvebu_mpp_ctrl_setting` stores the hardware mux value, function name, debug subname, variant mask, and computed GPIO capability flags. `struct mvebu_mpp_mode` binds a pin id to its settings. `struct mvebu_pinctrl_soc_info` is the SoC descriptor consumed by `mvebu_pinctrl_probe()`.

Control flow: SoC files use `MPP_FUNC_CTRL()` or `MPP_FUNC_GPIO_CTRL()` to declare controls, `MPP_FUNCTION()` or `MPP_VAR_FUNCTION()` to declare settings, `MPP_MODE()` to terminate each setting list, and `MPP_GPIO_RANGE()` to describe GPIO ranges. The core later fills control pin arrays, filters settings by `variant`, infers GPIO flags, and invokes exported get/set helpers.

State and persistence behavior: the header itself has no runtime state, but it establishes which fields are mutable. Notably, `flags` in settings and `pins` arrays in controls are written by the core, and some SoC drivers also mutate `variant` fields at probe. Register persistence is delegated to the implementation helpers.

Dependencies and integration points: this header depends on Linux pinctrl GPIO range types, regmap declarations from included users, and platform driver declarations. It is included by all MVEBU pinctrl table drivers and by `pinctrl-mvebu.c`.

Risks and test signals: `MPP_FUNC_CTRL()` allocates a compound-literal pin array inside static initializers; the core mutates it, so const-correctness is deliberately relaxed. `MPP_VAR_FUNCTION()` drops `subname` when debugfs is disabled, changing debug detail but not function names. The ABI relies on exact string names. Test by building with and without `CONFIG_DEBUG_FS`, compiling all SoC table drivers, and checking that every mode list is sentinel-terminated by `MPP_MODE()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-mvebu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-orion.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-orion.c

Purpose: this driver supports Orion 88F5181, 88F5181L, 88F5182, and 88F5281 pinmuxing. It is mostly a table driver, but it needs custom register access because MPP0-15 and MPP16-19 are not laid out contiguously.

Important APIs, types, and functions: `orion_mpp_ctrl_get()` and `orion_mpp_ctrl_set()` read/write low pins from `mpp_base` and high pins from `high_mpp_base`. Variant masks `V_5181`, `V_5182`, `V_5281`, and `V_ALL` filter the `orion_mpp_modes[]` table. The three SoC info objects provide variant-specific GPIO ranges, with 88F5182 exposing 19 GPIOs and the others 16.

Control flow: probe obtains SoC info from the OF match, maps two MMIO resources, and calls `mvebu_pinctrl_probe()` directly because the generic simple helper cannot describe the split high register. The common core builds groups and functions, while runtime muxing uses the custom control callback to select the right register block.

State and persistence behavior: `mpp_base` and `high_mpp_base` are file-static MMIO pointers. Mux state persists in hardware registers. There is no suspend/resume and no per-device private wrapper beyond the core allocation.

Dependencies and integration points: dependencies include two DT MMIO resources, MVEBU core callbacks, and OF compatibles. Integrated functions include PCIe/PCI, GPIO, boot NAND/NAND, SATA presence/activity LEDs, GE, and UART1 on variant-specific high pins.

Risks and test signals: the high-register path computes shift from `pid % 8`, so pins 16-19 occupy low nibbles in the high register. Static MMIO globals assume a single instance. Variant filtering is essential because GPIO on MPP16-19 is 88F5182-only. Test with all compatibles, verify both resources are required, read/write muxes below and above pin 16, and confirm GPIO range differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-orion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/Kconfig

Purpose: this Kconfig file exposes configuration switches for ST-Ericsson ABx500 mixed-signal chip pinctrl/GPIO support and Nomadik/U8500 SoC pinctrl support.

Important APIs, types, and functions: it defines `PINCTRL_ABX500`, `PINCTRL_AB8500`, `PINCTRL_AB8505`, `PINCTRL_NOMADIK`, `PINCTRL_STN8815`, and `PINCTRL_DB8500`. `PINCTRL_ABX500` depends on `AB8500_CORE` and selects `GENERIC_PINCONF`. `PINCTRL_NOMADIK` depends on OF and selects `PINMUX`, `PINCONF`, `GPIOLIB`, and `GPIO_NOMADIK`.

Control flow: Kconfig visibility is split by architecture guards. ABx500 options are visible for `ARCH_U8500` or `COMPILE_TEST`. Nomadik options are visible for `ARCH_U8500`, `ARCH_NOMADIK`, or `COMPILE_TEST`. The AB8500 and AB8505 table drivers depend on the common ABx500 core option.

State and persistence behavior: Kconfig has no runtime state, but it controls which object files and init functions are built into the kernel. Because these are bool options, enabled drivers are built-in rather than modules in this configuration fragment.

Dependencies and integration points: this file integrates the pinctrl drivers with architecture selection, the AB8500 MFD core, generic pinconf, gpiolib, and Nomadik GPIO support.

Risks and test signals: `PINCTRL_ABX500` selects generic pinconf but not `PINMUX` explicitly, relying on broader pinctrl dependencies. COMPILE_TEST coverage can expose missing includes or MFD stubs. Test with U8500, Nomadik, and COMPILE_TEST builds, including AB8500-only, AB8505-only, and both table-driver combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/Makefile

Purpose: this Makefile maps Nomadik and ABx500 Kconfig symbols to their pinctrl object files.

Important APIs, types, and functions: it builds `pinctrl-abx500.o` for `CONFIG_PINCTRL_ABX500`, `pinctrl-ab8500.o` for `CONFIG_PINCTRL_AB8500`, `pinctrl-ab8505.o` for `CONFIG_PINCTRL_AB8505`, `pinctrl-nomadik.o` for `CONFIG_PINCTRL_NOMADIK`, `pinctrl-nomadik-stn8815.o` for `CONFIG_PINCTRL_STN8815`, and `pinctrl-nomadik-db8500.o` for `CONFIG_PINCTRL_DB8500`.

Control flow: Kbuild includes objects conditionally via `obj-$(CONFIG_...)`. The common ABx500 core and each selected AB850x data table are compiled as separate objects, matching the header's init-function stubs.

State and persistence behavior: there is no runtime state. Build selection determines whether the core initcall and SoC data providers are present.

Dependencies and integration points: this file integrates with the Linux Kbuild system and the Kconfig symbols in the same directory.

Risks and test signals: if `PINCTRL_ABX500` is enabled without the needed AB8500 or AB8505 table, the core still builds but no supported compatible can supply SoC data except through enabled subdrivers. Test by building each symbol combination and checking undefined references for `abx500_pinctrl_ab8500_init()`/`ab8505_init()` are avoided by header stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-ab8500.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-ab8500.c

Purpose: this is the AB8500-specific pin inventory and mux table for the ABx500 pinctrl/GPIO core. It names GPIO-capable balls, groups them by default/alternate function columns, maps functions to groups, describes mux register bit encodings, and lists interrupt-capable GPIO clusters.

Important APIs, types, and functions: `ab8500_pins[]` lists GPIO1-42 with holes at GPIO5 and GPIO33. `ab8500_pinranges[]` maps GPIO number ranges to the altsetting needed for GPIO mode. `ab8500_groups[]` and `ab8500_functions[]` expose functions such as `sysclkreq`, `ycbcr`, `gpio`, `pwmout`, `adi1`, `usbuicc`, `dmic`, `extcpena`, `apespi`, `modsclsda`, `hiqclkena`, `i2ctrig`, and `usbvdat`. `ab8500_alternate_functions[]` describes GPIOSEL/ALTFUN bit usage per GPIO. `abx500_pinctrl_ab8500_init()` returns `ab8500_soc`.

Control flow: the common ABx500 probe calls `abx500_pinctrl_ab8500_init()` for compatible `stericsson,ab8500-gpio`. The core then registers pins, groups, functions, GPIO ranges, and uses the alternate-function table whenever a pinmux or GPIO request changes a pin mode.

State and persistence behavior: all AB8500 data is static. Runtime state is maintained by the common core and AB8500 hardware registers. The table has no write path except returning a pointer to the static SoC descriptor.

Dependencies and integration points: dependencies include `pinctrl-abx500.h`, pinctrl pin descriptors, and AB8500 interrupt constants. It integrates with AB8500 MFD IRQ domains through clusters for GPIO6-13, GPIO24-25, and GPIO36-41.

Risks and test signals: holes require the core's homogeneous GPIO numbering to include absent offsets while pin descriptors omit them. Some pins share one GPIOSEL bit across multiple GPIOs, especially GPIO17-20, so mux changes can affect grouped pins. Test GPIO requests across all ranges, IRQ mapping for each cluster, default versus ALT_A/B/C muxing, and DT group/function names for multi-group functions like YCbCr and USBUICC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-ab8500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-ab8505.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-ab8505.c

Purpose: this file provides AB8505-specific pin, group, function, alternate-function, and interrupt-cluster data to the common ABx500 pinctrl/GPIO driver.

Important APIs, types, and functions: `ab8505_pins[]` lists sparse GPIO-capable pins up to GPIO53. `ab8505_pinranges[]` maps sparse ranges to the altsetting needed for GPIO. `ab8505_groups[]` covers default, ALT_A, ALT_B, and ALT_C groups for sysclkreq, GPIO, PWM, ADI2, external control, modem I2C, reset/service, high-quality clock, PDM, UART data, external vibrator PWM, and USB VDAT. `ab8505_functions[]` maps function names to those groups. `ab8505_alternate_functions[]` encodes GPIOSEL and ALTFUN bits. `ab8505_gpio_irq_cluster[]` maps interrupt-capable GPIO clusters. `abx500_pinctrl_ab8505_init()` returns `ab8505_soc`.

Control flow: when the common core probes `stericsson,ab8505-gpio`, it calls this file's init function and then uses the returned table for pinctrl registration, GPIO range registration, pinmux changes, pin configuration, and GPIO-to-IRQ mapping.

State and persistence behavior: the file is table-only and keeps no runtime state. Mux and GPIO state persists in AB8505 hardware registers accessed by the common ABx500 core.

Dependencies and integration points: dependencies include the ABx500 header and AB8500/AB9540 interrupt constants from the MFD headers. It integrates with the AB8500 MFD IRQ domain through clusters for GPIO10-11, 13, 40-41, 50, and 52-53.

Risks and test signals: the GPIO number space is very sparse, so absent GPIOs must not be requested even though `ngpio` spans the highest range. `ab8505_functions[]` contains `FUNCTION(extvibra)` twice, which exposes duplicate function entries and may confuse function-count/debug users. Test sparse GPIO request failures, GPIO-to-IRQ mapping for AB9540 interrupt constants, ALT_B/ALT_C encoding on GPIO13 and GPIO50, and duplicate function behavior in pinctrl debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-ab8505.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-abx500.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-abx500.c

Purpose: this is the common ABx500 pinctrl and GPIO driver for ST-Ericsson AB8500/AB8505 mixed-signal chips. It registers a gpiolib chip, a pinctrl provider, pinmux operations, generic pinconf support, DT map parsing, debugfs display, and GPIO-to-IRQ translation using SoC data supplied by `pinctrl-ab8500.c` or `pinctrl-ab8505.c`.

Important APIs, types, and functions: `struct abx500_pinctrl` stores the device, pinctrl device, selected SoC data, `gpio_chip`, parent `struct ab8500`, and IRQ clusters. Register helpers `abx500_gpio_get_bit()` and `abx500_gpio_set_bits()` access AB8500 MISC bank registers through interruptible MFD APIs. GPIO operations include get/set, direction input/output, and `abx500_gpio_to_irq()`. Pinmux is handled by `abx500_set_mode()`, `abx500_pmx_set()`, and `abx500_gpio_request_enable()`. DT parsing is implemented by `abx500_dt_node_to_map()` and helpers. Pinconf set supports bias disable, pull-down, pull-up placeholder behavior, and output level.

Control flow: `core_initcall()` registers the platform driver. Probe validates DT, allocates state, gets the AB8500 parent, selects AB8500 or AB8505 SoC tables from match data, computes a homogeneous `ngpio` from GPIO ranges, registers the GPIO chip, registers pinctrl, adds pin ranges with an offset correction for no GPIO0, and stores driver data. Runtime GPIO requests call into pinctrl's GPIO enable hook, which finds the SoC range and programs the needed altsetting. Pinmux requests program all pins in a group. GPIO-to-IRQ scans the SoC cluster table and creates a mapping in the parent IRQ domain.

State and persistence behavior: driver state is device-managed except the gpiochip is manually removed on errors/remove. Hardware state persists in ABx500 MISC registers. There is no software shadow, locking, suspend/resume, or runtime PM in this file.

Dependencies and integration points: dependencies include AB8500 MFD register and IRQ-domain services, gpiolib, pinctrl core, generic pinconf parsing, OF, and SoC data providers. DT subnodes use `function`/`groups` for mux and `pins` plus generic pinconf properties for configs.

Risks and test signals: several paths rely on GPIO numbering offset corrections; `abx500_gpio_get()` subtracts one while `abx500_gpio_set()` does not, so read/write consistency deserves hardware testing. `abx500_set_mode()` writes `af.alt_bit2` twice in the ALT_C case, likely ignoring `alt_bit1`. Pull-up config only switches to input and does not program a pull-up value. DT config maps call `abx500_find_pin_name()` but do not reject a NULL result before adding maps. Test GPIO read/write/direction across banks, ALT_A/B/C muxing, GPIO holes, IRQ clusters, DT parsing errors, and generic pinconf behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-abx500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-abx500.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-abx500.h

Purpose: this header defines the data model shared by the ABx500 common driver and AB8500/AB8505 SoC table files.

Important APIs, types, and functions: package IDs `PINCTRL_AB8500` and `PINCTRL_AB8505` select SoC data. `enum abx500_pin_func` defines default, ALT_A, ALT_B, and ALT_C modes. Pull and voltage enums describe supported GPIO electrical configuration values. `struct abx500_function`, `struct abx500_pingroup`, `struct alternate_functions`, `struct abx500_gpio_irq_cluster`, `struct abx500_pinrange`, and `struct abx500_pinctrl_soc_data` describe all static SoC inputs. Macros `ALTERNATE_FUNCTIONS()`, `GPIO_IRQ_CLUSTER()`, and `ABX500_PINRANGE()` initialize those tables.

Control flow: the common probe chooses a package ID and calls `abx500_pinctrl_ab8500_init()` or `abx500_pinctrl_ab8505_init()` to obtain a `struct abx500_pinctrl_soc_data`. If a table driver is disabled, inline stubs leave the pointer unchanged, allowing the core to report invalid SoC data instead of failing to link.

State and persistence behavior: the header has no runtime state. It defines table fields that the common driver treats as read-only, although the `alternate_functions` and IRQ cluster pointers are not declared const in the SoC descriptor.

Dependencies and integration points: dependencies include Linux types and pinctrl pin descriptors. It is the integration contract for Kconfig combinations where the common ABx500 core may be built with either, both, or neither SoC table object.

Risks and test signals: the alternate-function model must handle inconsistent ABx500 mux encodings, so per-pin values are easy to get wrong. GPIO range `offset` values are one-based to match ABx500 GPIO numbering, while gpiolib ranges are adjusted later. Test build combinations with disabled subdrivers, table bounds for `GPIO_MAX_NUMBER + 1`, and compiler coverage for const mismatches or missing init functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-abx500.h -->
