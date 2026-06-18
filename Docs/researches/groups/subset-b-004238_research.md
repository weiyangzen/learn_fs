# subset-b-004238 research

Grouped research report for the requested MFD driver files under `sources/distributed-fs/ceph-client/drivers/mfd`. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/acer-ec-a500.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/acer-ec-a500.c

Purpose: implements the Acer Iconia Tab A500 embedded-controller MFD driver over I2C. It exposes the KB930 controller through a custom regmap bus, creates battery and LED child devices, and optionally registers system power-off and restart hooks when the device tree marks the EC as the system power controller.

Important APIs and functions: `a500_ec_probe` initializes the regmap and MFD cells; `a500_ec_remove` unregisters power hooks. The regmap bus is backed by `a500_ec_read` and `a500_ec_write`, which issue SMBus word transactions with retry sleeps. Power hooks are `a500_ec_poweroff` and `a500_ec_restart_notify`; child cells are `"acer-a500-iconia-battery"` and `"acer-a500-iconia-leds"`.

Control flow: probe builds a devm regmap with 8-bit registers and 16-bit little-endian values, then calls `devm_mfd_add_devices`. If `of_device_is_system_power_controller()` is true, it stores the I2C client in the file-global `a500_ec_client_pm_off`, registers a restart notifier, and installs `pm_power_off` only if no handler is already present. Reads and writes retry up to five times with a 500 ms delay; current reads add an extra 10 ms delay for `REG_CURRENT_NOW`. Power-off and restart commands write fixed opcodes then block for one second.

State and persistence: persistent device state is in the external EC registers and firmware. Kernel state is a devm-managed regmap plus the global power-management I2C client pointer and restart notifier. There is no software cache beyond regmap defaults, and remove only clears `pm_power_off` if this driver owns it.

Dependencies and integration points: depends on Linux I2C SMBus, regmap custom bus support, MFD core, device-tree power-controller discovery, reboot notifier infrastructure, and the child battery/LED drivers named by the MFD cells. It integrates with system shutdown by writing EC reboot/shutdown registers directly instead of using child drivers.

Risks: the global `a500_ec_client_pm_off` assumes only one active system-power-controller instance. The power-off/restart paths ignore SMBus write failures and then delay, so failure diagnostics may be weak during shutdown. The custom regmap callbacks do unaligned pointer casts from `void *` buffers, which is common in old regmap bus code but sensitive to architecture assumptions. Retry delays are long enough to stall callers for seconds on an unresponsive bus.

Test signals: useful validation includes kernel build coverage with the OF compatible `acer,a500-iconia-ec`, probe with battery and LED child creation, SMBus failure injection for retry/error logs, system power-off and warm/cold reboot behavior on A500 hardware, and current-read timing behavior for the battery child.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/acer-ec-a500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/act8945a.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/act8945a.c

Purpose: provides the I2C MFD core for the Active-semi ACT8945A PMIC. It creates a regmap for 8-bit register access and instantiates regulator and charger child devices.

Important APIs and functions: `act8945a_i2c_probe` is the single runtime entry point. It calls `devm_regmap_init_i2c`, stores the regmap with `i2c_set_clientdata`, and calls `devm_mfd_add_devices` for `"act8945a-regulator"` and `"act8945a-charger"`; the charger cell has OF compatible `"active-semi,act8945a-charger"`.

Control flow: the driver registers at `subsys_initcall` rather than through `module_i2c_driver`, so it appears early enough for regulator consumers. Probe validates only regmap creation and child-device registration; there is no chip-ID check or IRQ setup.

State and persistence: all software state is devm-managed and limited to the regmap stored as client data. Device register persistence is entirely handled by the PMIC hardware and child drivers.

Dependencies and integration points: depends on I2C, regmap, OF matching for `"active-semi,act8945a"`, and MFD core. Integration is through the two child drivers that consume the parent regmap.

Risks: the lack of hardware identity verification means a mismatched compatible can bind and expose invalid children. There is no IRQ domain or resource wiring for charger events in this core. The early initcall is appropriate for regulators but can expose probe-order issues if the I2C adapter is not ready.

Test signals: build with ACT8945A support, probe on a board with the PMIC, child regulator and charger devices appearing, regulator enable/voltage operations through the child, and negative testing for I2C/regmap initialization errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/act8945a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/adp5520.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/adp5520.c

Purpose: implements the base I2C driver for ADP5520/ADP5501 PMIC-style devices, exposing shared register helpers, interrupt notification, and optional platform-data child devices for keys, GPIO, LEDs, and backlight.

Important APIs and functions: exported child-facing APIs are `adp5520_read`, `adp5520_write`, `adp5520_set_bits`, `adp5520_clr_bits`, `adp5520_register_notifier`, and `adp5520_unregister_notifier`. Internal helpers perform SMBus byte reads/writes and W1C interrupt acknowledgements. `adp5520_irq_thread` reports events through a blocking notifier chain. Probe registers child platform devices based on `struct adp5520_platform_data`.

Control flow: probe requires SMBus byte-data support and non-null platform data. It allocates `struct adp5520_chip`, requests a threaded low-triggered IRQ if present, writes `ADP5520_nSTNBY` to leave standby, and creates requested child platform devices. Child creation is sequential; any failure unregisters already created children and frees the IRQ. Suspend saves only backlight/dim/standby bits from `ADP5520_MODE_STATUS`, writes zero to the mode register, and resume restores the saved subset.

State and persistence: `struct adp5520_chip` stores the I2C client, device, register mutex, notifier chain, IRQ number, chip ID, and saved suspend mode. Hardware register state is not fully cached; callers perform live SMBus operations. Child platform devices own their copied platform data.

Dependencies and integration points: depends on legacy platform data in `linux/mfd/adp5520.h`, I2C SMBus byte operations, platform-device children, IRQ threading, mutexes, and blocking notifiers. Children integrate through exported register accessors and notifier registration.

Risks: no device-tree probing path is present; missing platform data makes probe fail. Raw read/write exports are not mutex-protected, so child drivers must avoid conflicting read-modify-write sequences unless they use set/clear helpers. Event registration enables only masked event bits and relies on unregister callers to pass the same event mask. Error text says "SMBUS Word Data" although the check is byte data.

Test signals: compile with dependent child drivers, probe with ADP5520 and ADP5501 IDs, child registration based on each platform-data pointer, IRQ notification delivery for keypad/GPI/OVP/comparator events, W1C interrupt clearing, and suspend/resume restoration of backlight mode bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/adp5520.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/adp5585.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/adp5585.c

Purpose: implements the I2C MFD core for ADP5585 and ADP5589 I/O expander, PWM, and keypad-controller variants. It selects variant-specific register maps/defaults, validates firmware-described unlock/reset events, manages shared pin usage, handles event FIFO interrupts, and creates GPIO, PWM, and key child devices when firmware properties request them.

Important APIs and functions: core probe is `adp5585_i2c_probe`. Variant setup is handled by `adp5585_fill_variant_config`; firmware parsing by `adp5585_parse_fw`, `adp5585_unlock_ev_parse`, `adp5585_reset_ev_parse`, and `adp5585_parse_ev_array`; hardware setup by `adp5585_setup`; child creation by `adp5585_add_devices`; IRQ flow by `adp5585_irq_enable`, `adp5585_irq`, and `adp5585_report_events`. Shared parent state is `struct adp5585_dev` from the public MFD header.

Control flow: probe allocates state, reads the OF match data into a variant enum, fills a duplicated regmap config with the correct raw defaults and volatile range, enables the `vdd` regulator, optionally toggles a reset GPIO, initializes regmap, checks the manufacturer ID, allocates the `pin_usage` bitmap, parses firmware properties, programs reset/unlock/event polling configuration, instantiates requested children, and finally enables threaded IRQ handling. The IRQ handler reads `ADP5585_INT_STATUS`, logs overflow, reads FIFO event count from `ADP5585_STATUS`, notifies registered listeners for each FIFO record, and writes status back to acknowledge.

State and persistence: state includes variant identity, register-layout pointer, regmap, device, IRQ, notifier chain, pin-usage bitmap, event arrays, reset configuration bits, unlock timer, oscillator reference setup, and capability flags such as `has_unlock` and `has_pin6`. Regmap uses MAPLE caching with raw defaults; suspend switches the cache to cache-only, and resume marks it dirty and syncs hardware.

Dependencies and integration points: depends on OF device properties, `linux/mfd/adp5585.h`, I2C regmap, regulator framework, optional reset GPIO, MFD core, and blocking notifiers consumed by keypad/GPIO-related children. Firmware properties such as `#pwm-cells`, `#gpio-cells`, `adi,keypad-pins`, `adi,unlock-events`, `adi,reset1-events`, `adi,reset2-events`, and timing/polarity properties drive the exposed functions.

Risks: event validation is variant-sensitive, especially ADP5585 devices without row/pin 6; incorrect firmware can make probe fail. Child functions share pins through a bitmap but final conflict avoidance depends on child drivers honoring `pin_usage`. The reset GPIO timings are explicitly undocumented "reasonable values." IRQ absence is tolerated, but event-driven consumers may not work. Regcache sync failures on resume leave IRQ disabled until the caller handles the PM error path.

Test signals: build with ADP5585/ADP5589 variants, probe each OF compatible, validate rejection of invalid reset/unlock events, check child creation only when corresponding firmware properties exist, exercise event FIFO delivery and overflow logging, suspend/resume with regcache sync, and confirm PWM/GPIO/keypad children respect reserved reset/unlock pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/adp5585.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/altera-a10sr.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/altera-a10sr.c

Purpose: provides SPI MFD access to the Altera Arria 10 development kit MAX5 system resource chip. It exposes GPIO and reset child devices backed by an 8-bit regmap with explicit readability, writability, and volatility rules.

Important APIs and functions: `altr_a10sr_spi_probe` allocates `struct altr_a10sr`, configures SPI mode 3 with 8-bit words, initializes a SPI regmap, and registers `"altr_a10sr_gpio"` and `"altr_a10sr_reset"` children. Register access policy is defined by `altr_a10sr_reg_readable`, `altr_a10sr_reg_writeable`, and `altr_a10sr_reg_volatile`.

Control flow: on probe, the driver sets SPI transport parameters, calls `spi_setup`, stores driver data, creates a regmap using single-byte read/write with read flag bit set, and then calls `devm_mfd_add_devices`. It is registered as a built-in SPI driver through `builtin_driver`.

State and persistence: software state is the devm-managed `struct altr_a10sr` with the SPI device and regmap. Hardware state is in the MAX5 resource chip registers; no regcache is used (`REGCACHE_NONE`).

Dependencies and integration points: depends on SPI core, `linux/mfd/altera-a10sr.h`, regmap SPI, OF matching for `"altr,a10sr"`, and child GPIO/reset drivers. The regmap access tables protect reserved or unsupported resource-chip registers from generic child access.

Risks: `spi_setup` return value is ignored, so transport configuration failures may surface later as regmap I/O errors. The `max_register` is `ALTR_A10SR_WR_KEY_REG`, which can exclude newer registers if the header grows without updating the core. No IRQ chip is provided for pushbutton/switch status despite volatile IRQ registers.

Test signals: probe on Arria10 DevKit hardware, SPI mode verification, regmap readable/writable filtering, GPIO and reset child creation, register access failure injection, and build coverage for built-in registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/altera-a10sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/altera-sysmgr.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/altera-sysmgr.c

Purpose: implements the Altera/Intel SoCFPGA System Manager regmap provider. It supports direct MMIO access for older system managers and secure-monitor-call mediated access for protected Stratix 10 registers, then exports lookup-by-phandle for other drivers.

Important APIs and functions: exported API is `altr_sysmgr_regmap_lookup_by_phandle(struct device_node *np, const char *property)`. Probe is `sysmgr_probe`. Secure callbacks are `s10_protected_reg_read` and `s10_protected_reg_write`, which issue `arm_smccc_smc` calls with Intel SIP SMC function IDs.

Control flow: core init registers the platform driver. Probe allocates `struct altr_sysmgr`, reads the MMIO resource, computes `max_register`, and either initializes a custom regmap using the physical base as context for `"altr,sys-mgr-s10"` or maps the resource and initializes a fast MMIO regmap otherwise. Lookup resolves a phandle or the node itself, finds the bound platform device by OF node, retrieves `sysmgr->regmap`, drops the device reference, and returns the regmap.

State and persistence: state is a per-device `struct altr_sysmgr` holding only the regmap. Hardware state persists in system manager registers; no cache is configured. The S10 path uses the physical resource start as opaque regmap context for secure calls.

Dependencies and integration points: depends on OF, platform devices, regmap, MMIO mapping, ARM SMCCC, and `linux/mfd/altera-sysmgr.h`. Consumers call the exported lookup helper to share the system-manager regmap without duplicating mappings.

Risks: SMC read writes `result.a1` into `*val` before checking status, so callers must trust the returned status. The lookup helper returns a regmap after `put_device(dev)`; this follows syscon-like lifetime assumptions but relies on the provider staying bound. Probe logs regmap init failure with `pr_err` rather than device context. `devm_ioremap` is used instead of resource-managed exclusive mapping on the non-S10 path.

Test signals: boot on `"altr,sys-mgr"` and `"altr,sys-mgr-s10"` systems, phandle lookup by consumer drivers including probe-defer behavior, SMC success/error paths, register read/write alignment with 32-bit stride, and module unload when built modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/altera-sysmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/arizona-core.c

Purpose: implements the shared core for Wolfson/Cirrus Arizona-class audio codec MFDs. It performs regulator and reset sequencing, chip identification, firmware/register patch application, 32 kHz clock management, runtime/system PM, IRQ initialization, GPIO/micbias defaults, and MFD child registration for codec, GPIO, haptics, PWM, microphone supply, and LDO children.

Important APIs and functions: exported APIs are `arizona_dev_init`, `arizona_dev_exit`, `arizona_clk32k_enable`, `arizona_clk32k_disable`, and exported PM ops `arizona_pm_ops`. Important helpers include `arizona_poll_reg`, `arizona_wait_for_boot`, `arizona_enable_reset`, `arizona_disable_reset`, free-running SYSCLK helpers, `wm5102_apply_hardware_patch`, `wm5110_apply_sleep_patch`, DCVDD isolation/connect helpers, clock error IRQ handlers, and device-tree platform-data parsing.

Control flow: `arizona_dev_init` stores driver data, reads platform data or OF GPIO defaults, gets optional MCLKs, sets regmap cache-only mode, chooses core supplies, adds early LDO1 child where applicable, gets regulators and reset GPIO, enables supplies, releases reset, verifies/reset/boots the chip, reads ID and revision, selects chip-specific patch function and child cell array, applies patches, writes GPIO and micbias defaults, enables runtime PM, initializes IRQs, requests core diagnostic IRQs, and adds main children. Failure paths unwind IRQs, runtime PM, 32 kHz clock, reset, regulators, DCVDD, and early children.

State and persistence: `struct arizona` holds regmap, device type/revision, clocks, regulator handles, reset GPIO, platform data, clock reference count protected by `clk_lock`, IRQ state, runtime PM flags, and power state such as `external_dcvdd` and `has_fully_powered_off`. Regmap cache is used aggressively: cache-only during low-power/power-off states, dirty marking on suspend, and sync on resume.

Dependencies and integration points: depends on codec-specific regmap/patch tables declared in `arizona.h`, regulator and clock frameworks, GPIO descriptors, runtime PM, MFD core, regmap, `arizona-irq.c`, and child drivers. Transport drivers (`arizona-i2c.c` and `arizona-spi.c`) allocate `struct arizona`, initialize bus regmap, set type/IRQ/dev, and call this core.

Risks: power sequencing is complex and highly chip-variant dependent; mismatched type/compatible can be corrected after ID read but only when the needed Kconfig support is built. Runtime suspend may fully power off the chip when jack detection is inactive, so resume depends on reset, boot polling, patch reapplication, and regcache sync all succeeding. `arizona_clk32k_disable` warns on underflow but still decrements. Some `regmap_write` calls for defaults ignore return values. `arizona_dev_exit` disables IRQ before calling `arizona_irq_exit`, so ordering must stay compatible with nested IRQ teardown.

Test signals: build across WM5102, WM5110/WM8280, WM8997, WM8998/WM1814, WM1831, and CS47L24 configurations; probe with I2C and SPI transports; boot-done timeout behavior; patch application and free-running SYSCLK restoration; runtime suspend/resume with external and internal DCVDD; jack-detect active and inactive paths; 32 kHz clock refcounting; diagnostic IRQ logging; and child-device enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/arizona-i2c.c

Purpose: provides the I2C transport binding for Arizona-class codecs. It selects a chip-specific I2C regmap configuration from match data and delegates all common initialization and teardown to the Arizona core.

Important APIs and functions: `arizona_i2c_probe` handles allocation and regmap setup; `arizona_i2c_remove` calls `arizona_dev_exit`. Match tables cover `wm5102`, `wm5110`, `wm8280`, `wm8997`, `wm8998`, and `wm1814` I2C IDs and OF compatibles.

Control flow: probe obtains match data via `i2c_get_match_data`, selects the appropriate regmap config only if matching Kconfig support is enabled, allocates `struct arizona`, initializes `devm_regmap_init_i2c`, stores type/device/IRQ, and calls `arizona_dev_init`. Remove fetches the core state from device driver data and tears it down.

State and persistence: this file owns only the bus-specific allocation and I2C regmap lifetime. Persistent codec state, PM state, IRQ domains, child devices, and regulators are owned by `arizona-core.c`.

Dependencies and integration points: depends on I2C, regmap, PM runtime hooks through `arizona_pm_ops`, OF/I2C matching, and the regmap config symbols declared in the local Arizona header. It has a soft dependency on `arizona_ldo1`.

Risks: unsupported Kconfig combinations produce `-EINVAL` even if the hardware is present. The I2C path does not support WM1831/CS47L24, which are SPI-only in this file. Correct IRQ number and reset/regulator descriptors must come from board firmware for core initialization to succeed.

Test signals: I2C modalias and OF matching for each supported type, failure when a disabled Kconfig variant is matched, regmap initialization errors, shared core probe/remove behavior, runtime PM callbacks through the I2C driver, and module soft dependency ordering with LDO1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona-irq.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/arizona-irq.c

Purpose: implements interrupt support for Arizona-class codecs. It maps the physical IRQ line into a two-entry virtual IRQ domain for always-on and main interrupt domains, attaches variant-specific regmap IRQ chips, exposes child-facing IRQ request/free/wake helpers, and handles top-level threaded dispatch with runtime PM.

Important APIs and functions: exported APIs are `arizona_request_irq`, `arizona_free_irq`, `arizona_set_irq_wake`, `arizona_irq_init`, and `arizona_irq_exit`. Key internals are `arizona_map_irq`, `arizona_irq_thread`, `arizona_irq_map`, `arizona_boot_done`, and `arizona_ctrlif_err`.

Control flow: initialization chooses AOD and main regmap IRQ chips based on codec type and revision, disables wake sources, derives IRQ trigger flags if platform data did not specify them, configures IRQ polarity, creates a linear IRQ domain with AOD and main mappings, attaches regmap IRQ chips, optionally translates legacy GPIO IRQs, requests the physical threaded IRQ, and requests core boot-done/control-interface-error nested IRQs. The top-level thread runtime-resumes the codec, checks AOD status, dispatches the AOD nested IRQ when needed, checks main IRQ pin status, dispatches main nested IRQ, optionally polls GPIO pin level for legacy edge emulation, and runtime-autosuspends.

State and persistence: state is stored in `struct arizona`: physical IRQ, virtual IRQ domain, regmap IRQ chip data pointers, `ctrlif_error`, platform IRQ flags, and optional legacy IRQ GPIO. Hardware interrupt masks/status are managed through regmap IRQ chips.

Dependencies and integration points: depends on regmap IRQ, Linux IRQ domains, nested threaded IRQs, runtime PM, optional legacy GPIO, and variant IRQ chip tables declared in `arizona.h`. Child drivers use the exported helper APIs with Arizona logical IRQ numbers instead of directly touching regmap IRQ data.

Risks: teardown always calls `regmap_del_irq_chip` for AOD mapping even when `aod_irq_chip` is NULL; this relies on safe NULL behavior in surrounding paths and mappings. The default branch uses a `BUG_ON("Unknown Arizona class device" == NULL)` expression that is intentionally false and then returns `-EINVAL`, which is unusual. Runtime resume failure in the top-level IRQ returns `IRQ_NONE`, which can matter for shared IRQ diagnostics. IRQ polarity corrections must match board wiring, especially ACPI SPI boards fixed in `arizona-spi.c`.

Test signals: nested IRQ delivery for AOD and main domains, boot-done IRQ unmasking across resume, wake-source control via `arizona_set_irq_wake`, variant/revision IRQ chip selection, active-low and active-high IRQ polarity, legacy GPIO polling behavior, runtime PM interaction during IRQ storms, and clean teardown on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona-spi.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/arizona-spi.c

Purpose: provides the SPI transport binding for Arizona-class codecs, including special ACPI board handling for WM5102 devices. It selects chip-specific SPI regmap configuration, fills platform data quirks for ACPI systems, and delegates common initialization to the Arizona core.

Important APIs and functions: `arizona_spi_probe` and `arizona_spi_remove` are the driver lifecycle functions. ACPI helpers include `arizona_spi_acpi_probe`, `arizona_spi_acpi_windows_probe`, `arizona_spi_acpi_android_probe`, and lookup-table cleanup `arizona_spi_acpi_remove_lookup`. Static ACPI microphone-detect ranges provide AOSP button resistance mappings.

Control flow: probe gets match data from SPI/OF/ACPI, selects a regmap config for WM5102, WM5110/WM8280, or WM1831/CS47L24 if enabled, allocates `struct arizona`, initializes SPI regmap, stores type/device/IRQ, applies ACPI quirks when present, and calls `arizona_dev_init`. Windows-style ACPI setup maps reset/LDO GPIO resources, adds lookup-table entries for SoC GPIOs, invokes a CLKE ACPI method, sets IRQ trigger low, and populates mic-detect/headphone-detect defaults. Android-style ACPI setup defers when reset GPIO lookup is not yet available.

State and persistence: bus-specific state is the allocated `struct arizona` and SPI regmap. ACPI paths may install devm-managed GPIO mappings and platform-data fields before core initialization. Persistent codec power/register state is managed by `arizona-core.c`.

Dependencies and integration points: depends on SPI, regmap, OF, ACPI, GPIO descriptor/machine lookup APIs, input key codes for mic button mappings, PM ops from the core, and chip regmap configs declared in `arizona.h`. It has a soft dependency on `arizona_ldo1`.

Risks: ACPI board quirk behavior is broad and assumes known Windows/Android firmware patterns. The driver forces ACPI IRQ flags to active-low level because falling-edge DSDT entries are known broken; unsupported hardware with true edge-only wiring would need another workaround. Probe deferral for Android reset GPIO depends on external lookup-table providers. Unsupported Kconfig variants fail before core probe.

Test signals: SPI modalias/OF/ACPI matching, regmap initialization for supported chip types, Windows and Android ACPI board probe paths, reset/LDO GPIO mapping, CLKE method warnings, IRQ trigger correction, mic-detect button reporting through child drivers, and core probe/remove behavior over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona.h -->
# sources/distributed-fs/ceph-client/drivers/mfd/arizona.h

Purpose: declares private Arizona MFD internals shared between the transport, core, IRQ, and chip table files. Despite the old guard name `_WM5102_H`, it covers the wider Arizona family.

Important APIs and types: declares external regmap configurations for WM5102, WM5110, CS47L24, WM8997, and WM8998 transports; exported PM ops; regmap IRQ chips for each supported codec family; and internal lifecycle functions `arizona_dev_init`, `arizona_dev_exit`, `arizona_irq_init`, and `arizona_irq_exit`.

Control flow: bus drivers include this header to select regmap configs and call the core lifecycle functions. The core and IRQ implementation include it to access variant-specific patch/table objects compiled from other files.

State and persistence: the header owns no state. It expresses cross-translation-unit linkage for shared constant tables and lifecycle functions.

Dependencies and integration points: depends on `linux/of.h`, `linux/regmap.h`, and `linux/pm.h`, and assumes `struct arizona` is visible from the public Arizona core header in including files. It is the internal boundary among Arizona MFD compilation units.

Risks: one declaration pair, `wm8998_aod` and `wm8998_irq`, is non-const while other IRQ chips are const, so implementations must match this mutability. The guard and comment still mention WM5102, which can confuse maintainers. Missing declarations here break transport/core links rather than runtime behavior.

Test signals: compile/link coverage for all enabled Arizona Kconfig combinations, especially combinations with only one codec family enabled; sparse/const mismatch checks; and module dependency coverage between transport modules and table objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/as3711.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/as3711.c

Purpose: implements the I2C MFD core for the AMS AS3711 PMIC. It provides an 8-bit regmap, validates the ASIC ID, and creates regulator and backlight child devices with optional platform-data payloads.

Important APIs and functions: `as3711_i2c_probe` is the lifecycle entry point. Register access policy is encoded in `as3711_volatile_reg`, `as3711_precious_reg`, and `as3711_readable_reg`. Child cells are `"as3711-regulator"` and `"as3711-backlight"`.

Control flow: probe obtains platform data for non-OF systems or allocates an empty platform-data structure for OF systems, allocates `struct as3711`, initializes regmap with MAPLE cache, reads `AS3711_ASIC_ID_1` and `_2`, verifies ID1 is `0x8b`, conditionally fills static child-cell platform data fields, and registers the children. IRQ presence is only logged as unsupported.

State and persistence: software state is `struct as3711` plus a regmap. The static `as3711_subdevs` array is mutated during probe to point at the current platform data, relying on the comment that I2C devices are not probed simultaneously. Interrupt status registers are marked precious so debug/cache code does not accidentally consume W1C-like status.

Dependencies and integration points: depends on I2C, regmap, MFD core, OF matching for `"ams,as3711"`, and child regulator/backlight drivers. Platform-data consumers receive copied child data through MFD registration.

Risks: using a mutable static child-cell array is fragile for multiple devices or unusual concurrent probe paths. IRQs are not supported, so charger/status events cannot be surfaced through this core. OF probing allocates empty platform data but does not parse properties in this file. Only ID1 is validated; ID2 is informational.

Test signals: probe with platform-data and OF configurations, ID mismatch handling, regulator/backlight child creation and platform-data propagation, regmap cache behavior for volatile/precious registers, and confirmation that systems with an IRQ line still operate without IRQ functionality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/as3711.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/as3722.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/as3722.c

Purpose: implements the I2C MFD core for AMS AS3722 PMICs. It validates device identity, configures pull-up and AC-OK behavior from device tree, registers a regmap IRQ chip, creates pinctrl/regulator/RTC/ADC/power-off/watchdog children, and provides suspend wake handling.

Important APIs and functions: lifecycle functions are `as3722_i2c_probe`, `as3722_i2c_suspend`, and `as3722_i2c_resume`. Helpers include `as3722_check_device_id`, `as3722_configure_pullups`, and `as3722_i2c_of_probe`. The regmap IRQ chip maps four interrupt-status/mask registers, with named child resources for RTC alarm and ADC interrupts.

Control flow: probe allocates `struct as3722`, requires a device-tree node and valid IRQ data, reads DT booleans and IRQ trigger flags, initializes an 8-bit MAPLE regmap with access tables, verifies `AS3722_ASIC_ID1_REG == 0x0c`, registers `devm_regmap_add_irq_chip` on the PMIC IRQ, configures internal INT/I2C pull-ups, sets optional AC-OK power-on bit, adds MFD children with the regmap IRQ domain, and initializes device wakeup. Suspend enables IRQ wake if allowed and disables the chip IRQ; resume reverses that ordering.

State and persistence: `struct as3722` holds device pointer, IRQ number, IRQ flags, pull-up/power-on booleans, regmap, and regmap IRQ data. Hardware state includes I/O voltage pull-up bits, AC-OK sequencer bit, child-controlled regulator/RTC/ADC state, and interrupt masks/status.

Dependencies and integration points: depends on OF, I2C, regmap and regmap IRQ, IRQ trigger discovery, MFD core, PM sleep hooks, and AS3722 helper APIs/macros from the MFD header. Child devices receive interrupts through `regmap_irq_get_domain`.

Risks: the probe path requires device tree and a valid IRQ; there is no no-IRQ fallback. Readable/writable/volatile tables must stay synchronized with child register use or regmap will reject legitimate operations. Suspend disables the physical IRQ after enabling wake; incorrect wake policy can prevent alarm/onkey wake. Device ID validation is strict and will reject compatible variants not represented by this driver.

Test signals: OF probe with each DT boolean combination, IRQ domain creation and child IRQ delivery for RTC/ADC/GPIO/watchdog events, ID mismatch tests, pull-up and AC-OK register updates, wake-from-suspend with RTC/onkey events, and regulator/pinctrl child functionality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/as3722.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/at91-usart.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/at91-usart.c

Purpose: provides a mode-selecting MFD wrapper for AT91 USART blocks that can operate either as a serial controller or as an SPI controller. It creates exactly one child device based on the `atmel,usart-mode` firmware property.

Important APIs and functions: `at91_usart_mode_probe` reads the mode and calls `devm_mfd_add_devices`. Child cells are `"at91_usart_spi"` for `AT91_USART_MODE_SPI` and `"atmel_usart_serial"` for `AT91_USART_MODE_SERIAL`.

Control flow: probe defaults to serial mode if `atmel,usart-mode` is absent. It switches on the resulting value, rejects unknown modes with `-EINVAL`, and registers the selected child with automatic platform ID.

State and persistence: this wrapper keeps no private state. The selected child driver owns the hardware registers and runtime state after MFD creation.

Dependencies and integration points: depends on AT91 USART DT binding constants, device properties, OF platform matching for AT91 USART compatibles, and MFD core. It is the arbitration point that prevents both serial and SPI children from binding to the same hardware instance.

Risks: an omitted property silently selects serial mode, which is compatible with legacy bindings but can hide firmware mistakes. The wrapper does not validate pinctrl or clock resources; failures appear in the child driver. Changing mode at runtime is not supported.

Test signals: DT probe with absent, serial, SPI, and invalid `atmel,usart-mode` values; child driver binding for serial/SPI; and build coverage for both AT91 USART child drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/at91-usart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atc260x-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/atc260x-core.c

Purpose: implements interface-independent core support for Actions ATC2603C and ATC2609A PMICs. It selects variant-specific regmap/IRQ/child-cell configuration, initializes interrupt hardware, detects chip revision, registers a regmap IRQ chip, and creates regulator, power-controller, and onkey children.

Important APIs and functions: exported APIs are `atc260x_match_device` and `atc260x_device_probe`. Helpers include custom `regmap_lock_mutex`/`regmap_unlock_mutex`, `atc260x_cmu_reset`, and `atc260x_dev_init`. Variant tables define 16-bit register maps, one-register IRQ chips, onkey IRQ resources, MFD cells, and reset/pad register addresses.

Control flow: bus drivers allocate `struct atc260x`, set `dev` and `irq`, call `atc260x_match_device` to fill regmap config and variant fields, initialize bus regmap, then call `atc260x_device_probe`. The probe path requires an IRQ, resets the interrupt block through CMU registers, masks all interrupts, enables the EXTIRQ pad, reads and validates the chip revision, derives an alphabetic revision from the one-hot revision value, registers the regmap IRQ chip, and adds child devices with the IRQ domain.

State and persistence: `struct atc260x` stores type, revision, regmap, IRQ, regmap IRQ data, cell table, type name, revision register, init register pointers, and a custom regmap mutex. The PMIC hardware retains regulator/power/interrupt state; this core does not use regcache.

Dependencies and integration points: depends on OF match data, regmap, regmap IRQ, MFD core, Linux interrupt support, and public ATC260x core macros/types. The custom regmap lock is designed to improve late shutdown/poweroff behavior on slow buses when interrupts are disabled.

Risks: `regmap_lock_mutex` uses `mutex_trylock` in late atomic-ish paths but `regmap_unlock_mutex` always unlocks, so correctness relies on trylock succeeding when invoked. No-IRQ configurations fail probe. Revision decoding assumes `chip_rev + 1` has a valid set bit and rejects values above 31. Manual `regmap_del_irq_chip` on `devm_mfd_add_devices` failure is unusual because the IRQ chip was devm-registered.

Test signals: probe both ATC2603C and ATC2609A OF compatibles, verify interrupt reset/mask/pad writes, chip revision detection, onkey IRQ delivery, child regulator/power-controller operation, no-IRQ failure behavior, and shutdown/poweroff code paths that exercise the custom regmap lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atc260x-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atc260x-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/atc260x-i2c.c

Purpose: provides the I2C transport binding for Actions ATC260x PMICs. It allocates the shared core state, obtains variant configuration from OF match data, initializes an I2C regmap, and delegates to `atc260x_device_probe`.

Important APIs and functions: `atc260x_i2c_probe` is the only runtime entry point. It calls `atc260x_match_device` and `devm_regmap_init_i2c`, then stores client data and invokes the core.

Control flow: probe allocates `struct atc260x`, sets device and IRQ from the I2C client, fills a local `struct regmap_config` through the core matcher, stores the state as client data, creates the regmap, and finishes through `atc260x_device_probe`.

State and persistence: this transport owns no state beyond the devm-allocated shared `struct atc260x` and bus regmap lifetime. All variant, IRQ, and child state is controlled by `atc260x-core.c`.

Dependencies and integration points: depends on I2C, OF matching for `"actions,atc2603c"` and `"actions,atc2609a"`, regmap, and the exported ATC260x core functions.

Risks: there is no ACPI or I2C ID fallback; match data must come from OF. No remove callback is needed because devm and MFD core handle resources, but behavior depends on the core's devm usage. Missing IRQ will cause the core probe to fail.

Test signals: I2C probe for both OF compatibles, regmap initialization errors, handoff to core with IRQ present/absent, child registration, and module load/unload coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atc260x-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atmel-flexcom.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/atmel-flexcom.c

Purpose: configures an Atmel/Microchip Flexcom block into one selected serial function and populates its child devices from device tree. Flexcom can expose USART, SPI, or TWI functionality, but only the selected function is clocked and muxed.

Important APIs and functions: `atmel_flexcom_probe` reads `atmel,flexcom-mode`, maps the register block, enables the clock, writes the mode register, disables the clock, and calls `devm_of_platform_populate`. `atmel_flexcom_resume_noirq` rewrites the selected mode after low-level resume.

Control flow: probe validates that the mode is between `ATMEL_FLEXCOM_MODE_USART` and `ATMEL_FLEXCOM_MODE_TWI`, obtains MMIO and clock resources, temporarily enables the clock to write `FLEX_MR_OPMODE(opmode)` to `FLEX_MR`, then populates children declared below the node. Resume repeats the mode write before child resume paths run.

State and persistence: `struct atmel_flexcom` stores MMIO base, selected opmode, and clock pointer. Hardware mode register state may be lost across system suspend, so the noirq resume hook restores it.

Dependencies and integration points: depends on DT binding constants, platform resources, OF platform population, MMIO, and clock framework. Child nodes under the Flexcom DT node bind to the actual USART/SPI/TWI drivers after the wrapper selects mode.

Risks: the driver does not keep the clock enabled after configuration, assuming children manage their own clocks. An invalid or missing `atmel,flexcom-mode` fails probe. If resume mode restoration fails because the clock cannot enable, child drivers may access an unconfigured block.

Test signals: probe with USART/SPI/TWI modes, invalid mode rejection, clock enable/write/disable tracing, child OF population, system suspend/resume preserving mode, and register readback of `FLEX_MR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atmel-flexcom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atmel-hlcdc.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/atmel-hlcdc.c

Purpose: implements the MFD core for Atmel/Microchip HLCDC/XLCDC display blocks. It creates a custom MMIO regmap with synchronization-aware writes, gathers shared clocks and IRQ, and registers PWM and display-controller children.

Important APIs and functions: `atmel_hlcdc_probe` initializes `struct atmel_hlcdc` and MFD cells. Custom regmap callbacks are `regmap_atmel_hlcdc_reg_write` and `regmap_atmel_hlcdc_reg_read`; writes to low control registers wait for `ATMEL_HLCDC_SIP` to clear before writing.

Control flow: probe maps registers, gets IRQ 0, obtains `periph_clk`, obtains either `sys_clk` or fallback `lvds_pll_clk`, obtains `slow_clk`, initializes the custom 32-bit stride regmap, stores shared state as driver data, and adds `"atmel-hlcdc-pwm"` and `"atmel-hlcdc-dc"` children.

State and persistence: shared state includes IRQ, clocks, and regmap in `struct atmel_hlcdc`. The custom regmap context stores MMIO base and device for error reporting. Hardware display/PWM state is managed by children.

Dependencies and integration points: depends on platform resources, clock framework, regmap custom callbacks, MFD core, and HLCDC register definitions from `linux/mfd/atmel-hlcdc.h`. Child display and PWM drivers use the shared regmap and clocks from parent driver data.

Risks: synchronization polling uses an atomic timeout of 100 microseconds for certain registers; slow hardware or wrong clocking can produce write failures. The clock selection fallback requires one of `sys_clk` or `lvds_pll_clk`; firmware names must match. Child resource creation has no explicit IRQ domain, so children rely on parent state rather than MFD resources for interrupt access.

Test signals: probe on each OF compatible, clock-resource combinations for RGB/MIPI and LVDS systems, regmap write timeout behavior while SIP is set, PWM and display child binding, display modeset tests, and XLCDC-compatible build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atmel-hlcdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atmel-smc.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/atmel-smc.c

Purpose: provides exported helper functions for configuring Atmel SMC/HSMC chip-select timing registers through a syscon/regmap. It is not a probing driver; it is a shared encoding/apply/get library for memory-controller consumers.

Important APIs and functions: exported functions include `atmel_smc_cs_conf_init`, timing field setters `atmel_smc_cs_conf_set_timing`, `set_setup`, `set_pulse`, `set_cycle`, apply/get helpers for SMC and HSMC, and `atmel_hsmc_get_reg_layout`. Internal `atmel_smc_cs_encode_ncycles` performs the datasheet split-MSB/LSB timing encoding with saturation.

Control flow: consumers initialize `struct atmel_smc_cs_conf`, call setter helpers to encode cycle counts into setup/pulse/cycle/timings fields, then apply the completed config to either legacy SMC register offsets or HSMC layout-based offsets. Getter helpers read current register values back into the same config structure. Layout lookup matches the controller DT node and returns NULL for legacy SMC, a layout pointer for SAMA5D2/D3 HSMC, or `ERR_PTR(-EINVAL)` for unknown nodes.

State and persistence: this file owns no runtime state. It mutates caller-owned config structures and writes persistent hardware controller registers through the supplied regmap.

Dependencies and integration points: depends on exported GPL symbols, OF matching, regmap, and register layout macros from `linux/mfd/syscon/atmel-smc.h`. NAND, memory, or bus drivers use these helpers after acquiring the SMC syscon regmap.

Risks: setter helpers update the encoded field even when returning `-ERANGE`, using the maximum representable value; callers must check the return if exact timing matters. Invalid shift values return `-EINVAL` without changing the relevant field. Apply/get helpers ignore regmap read/write return codes, so bus errors are silent. The function comments for pulse/cycle mention storing in `setup` though the code correctly writes `pulse`/`cycle`.

Test signals: unit-style tests for timing encoding boundaries and saturation, DT layout lookup for at91sam9260/sama5d2/sama5d3 compatibles, regmap write sequences for SMC and HSMC chip selects, consumers checking `-ERANGE`, and hardware memory timing validation with attached NAND/SRAM devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atmel-smc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/axp20x-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/axp20x-i2c.c

Purpose: provides the I2C transport binding for X-Powers AXP PMICs supported by the AXP20x MFD core. It allocates shared state, matches the PMIC variant, initializes an I2C regmap, and delegates device setup/removal to the core.

Important APIs and functions: `axp20x_i2c_probe` and `axp20x_i2c_remove` are the lifecycle functions. Match tables cover many OF compatibles from AXP152 through AXP15060 and ACPI ID `INT33F4` for AXP288.

Control flow: probe allocates `struct axp20x_dev`, sets device and IRQ, stores driver data, calls `axp20x_match_device` to fill variant-specific regmap/cell/IRQ-chip pointers, initializes I2C regmap using the chosen config, and calls `axp20x_device_probe`. Remove calls `axp20x_device_remove`.

State and persistence: transport state is only the devm-allocated `struct axp20x_dev` and I2C regmap. Variant, IRQ, child, and power-off state are owned by `axp20x.c`.

Dependencies and integration points: depends on I2C, OF and ACPI match data, regmap, and exported AXP20x core functions. It is the path for non-RSB PMIC variants and x86 AXP288 ACPI systems.

Risks: the I2C ID table entries do not carry driver data, so non-OF/non-ACPI I2C instantiation may not provide a variant through `device_get_match_data`. Remove always calls core removal, which deletes IRQ chip state only if it was created. Correct no-IRQ behavior depends on the core's fallback cell selection.

Test signals: OF probe for each listed compatible, ACPI `INT33F4` AXP288 probe, no-IRQ fallback behavior, regmap init failure handling, child creation per variant, and remove/unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/axp20x-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/axp20x-rsb.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/axp20x-rsb.c

Purpose: provides the sunxi RSB transport binding for X-Powers AXP PMICs. It supports Allwinner boards where the PMIC is accessed over the reduced serial bus and delegates common behavior to the AXP20x core.

Important APIs and functions: `axp20x_rsb_probe` and `axp20x_rsb_remove` mirror the I2C transport but use `devm_regmap_init_sunxi_rsb` and `sunxi_rsb_device_get_drvdata`. OF matches cover AXP223, AXP717, AXP803, AXP806, AXP809, and AXP813.

Control flow: probe allocates `struct axp20x_dev`, sets device and RSB IRQ, stores driver data, calls `axp20x_match_device`, initializes a sunxi RSB regmap using the selected config, and calls `axp20x_device_probe`. Remove calls the shared core removal path.

State and persistence: no transport-specific persistent state exists beyond the shared AXP20x state and bus regmap. PMIC register state and child devices are controlled by the core.

Dependencies and integration points: depends on `sunxi-rsb`, OF match data, regmap, and AXP20x core functions. It is the integration point for Allwinner PMICs on RSB rather than I2C.

Risks: only OF matching is supported. RSB addressing quirks such as AXP806 master/slave address-extension setup are handled later by the core, so incorrect firmware properties can leave the PMIC inaccessible after initial setup. No-IRQ child fallback follows the same core behavior as I2C.

Test signals: RSB probe on supported Allwinner boards, AXP806 master/self-working/slave configurations, IRQ and no-IRQ child registration, regmap read/write access over RSB, and remove/unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/axp20x-rsb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/axp20x.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/axp20x.c

Purpose: implements the interface-independent MFD core for many X-Powers AXP PMIC variants. It defines variant-specific regmap access tables, regmap IRQ chips, child-device cell arrays, no-IRQ fallbacks, AXP806 bus address-extension handling, and a system power-off handler.

Important APIs and functions: exported APIs are `axp20x_match_device`, `axp20x_device_probe`, and `axp20x_device_remove`. `axp20x_power_off` writes the shutdown bit to the correct shutdown register. Static tables define model names, writable/volatile register ranges, regmap configs, IRQ resources, regmap IRQ chips, and MFD child arrays for AXP152, AXP192, AXP20x/22x, AXP288, AXP313A/323, AXP717, AXP803/806/809/813, and AXP15060.

Control flow: transport drivers set `dev`, `irq`, and regmap, then call `axp20x_match_device`, which reads match data, selects cells/regmap config/IRQ chip/flags, handles AXP806 cell variants, and substitutes regulator-only or variant-specific no-IRQ cell arrays when no CPU IRQ is present. `axp20x_device_probe` programs AXP806 master/slave register address extension, registers a regmap IRQ chip if an IRQ exists, adds selected MFD children, and registers a devm power-off handler for non-AXP288 variants. Removal unregisters children and the regmap IRQ chip.

State and persistence: `struct axp20x_dev` stores variant, model-specific cell table, regmap config, regmap IRQ chip data, IRQ flags, and regmap. PMIC hardware persists regulator, charger, ADC, fuel gauge, GPIO, PEK, Type-C, and shutdown state. Regmap caches are MAPLE for most variants with explicit volatile ranges.

Dependencies and integration points: depends on OF/ACPI match data from transports, regmap and regmap IRQ, MFD core, regulator and power-supply child drivers, reboot/sys-off infrastructure, and AXP20x public macros/types. Child devices receive named IRQ resources but the MFD add call does not pass the IRQ domain directly; resources map through regmap IRQ infrastructure.

Risks: the large declarative variant tables are easy to desynchronize with hardware headers or child driver expectations. No-IRQ fallback intentionally drops most children because many require interrupts, which can surprise board bring-up. `axp20x_device_remove` calls `regmap_del_irq_chip` even when no IRQ chip was registered, relying on the core data pointer state. Power-off writes ignore errors and then delays 500 ms. AXP806 address-extension mode depends on firmware properties and can affect bus accessibility for chained PMICs.

Test signals: build and probe each variant through I2C/RSB/ACPI where applicable, verify selected cell arrays including no-IRQ fallback, IRQ delivery for PEK/charger/USB/fuel-gauge events, regmap access-table enforcement, AXP806 master/slave mode writes, AXP813 IRQ mapping correction, power-off behavior for shutdown-capable variants, and child regulator/ADC/power-supply smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/axp20x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bcm2835-pm.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/bcm2835-pm.c

Purpose: implements the Broadcom BCM2835/BCM2711/BCM2712 PM MFD parent. It maps PM and optional ASB register ranges, always creates a watchdog child, and conditionally creates a power-domain child when hardware resources indicate full PM support.

Important APIs and functions: `bcm2835_pm_probe` allocates and initializes shared `struct bcm2835_pm`; `bcm2835_pm_get_pdata` maps register resources in new `reg-names` or old positional DT layouts. Child cells are `"bcm2835-wdt"` and `"bcm2835-power"`.

Control flow: probe stores SoC match data, maps the PM base plus optional `asb` and `rpivid_asb` regions, registers the watchdog child, then registers the power child if ASB registers are available or the SoC is BCM2712. Old DTBs without `reg-names` are supported by positional resources.

State and persistence: `struct bcm2835_pm` stores device pointer, SoC type, PM base, ASB base, and RP1/RPi video ASB base. The parent does not directly manipulate hardware state beyond mapping resources; children perform watchdog and power-domain operations.

Dependencies and integration points: depends on OF platform matching, platform MMIO resources, MFD core, and public BCM2835 PM definitions. It integrates with downstream watchdog and power-domain drivers through parent driver data and MFD children.

Risks: optional ASB mappings silently become NULL on mapping errors, disabling or reducing power-domain support rather than failing probe. Old positional resource fallback is necessary for compatibility but easy to break with DT changes. The file lacks an explicit `MODULE_LICENSE`, which is unusual for a module source.

Test signals: probe with old and new DT resource layouts, watchdog child creation on all compatibles, power child creation only when ASB or BCM2712 conditions are met, BCM2711/BCM2712 resource coverage, and child watchdog/power-domain functional tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bcm2835-pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bcm590xx.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/bcm590xx.c

Purpose: implements the Broadcom BCM59054/BCM59056 PMU MFD core. It creates primary and secondary I2C regmaps, verifies PMU identity and revision, and registers the voltage-regulator child.

Important APIs and functions: `bcm590xx_i2c_probe` performs allocation, regmap setup, dummy secondary I2C creation, identity parsing, and child creation. `bcm590xx_parse_version` reads `BCM590XX_REG_PMUID` and `BCM590XX_REG_PMUREV`, validating compatible match data and storing digital/analog revision nibbles.

Control flow: probe allocates `struct bcm590xx`, stores primary client, gets PMU ID from OF match data, initializes primary regmap, creates a secondary dummy I2C client at primary address OR BIT(2), initializes secondary regmap, validates PMU ID/revision, and adds `"bcm590xx-vregs"`. Error paths unregister the secondary dummy device after it has been created.

State and persistence: software state includes primary and secondary I2C clients, primary and secondary MAPLE regmaps, PMU ID, and revision fields. Device register state persists in the PMU; this core does not create IRQ state.

Dependencies and integration points: depends on I2C, OF matching for `"brcm,bcm59054"`/`"brcm,bcm59056"`, regmap, MFD core, and the regulator child driver. The secondary I2C client exposes registers at the PMU's second slave address.

Risks: there is no remove callback to unregister the secondary dummy I2C device on normal driver removal, which can leak the dummy client until device teardown. Non-OF I2C ID matching lacks PMU ID match data. No IRQ chip is provided. A mismatched compatible fails probe after secondary client creation but the error path handles that case.

Test signals: probe both PMU compatibles, primary/secondary regmap access, PMU ID mismatch handling, regulator child registration, module unload behavior for the dummy secondary client, and I2C error handling for ID/revision reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bcm590xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bd9571mwv.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/bd9571mwv.c

Purpose: implements the ROHM BD9571MWV-M and BD9574MWF-M PMIC MFD core. It identifies the product, selects variant-specific regmap access tables and child cells, registers a regmap IRQ chip, and exposes regulator and GPIO children.

Important APIs and functions: `bd9571mwv_probe` is the lifecycle entry point; `bd957x_identify` validates vendor/product/revision registers after regmap creation. Static tables define BD9571MWV and BD9574MWF readable/writable/volatile ranges, regmap configs, shared IRQ bits, variant IRQ chips, and child cell arrays.

Control flow: probe reads product code with raw SMBus before regmap setup, selects the BD9571 or BD9574 configuration, initializes I2C regmap, validates vendor and revision registers, registers a one-register regmap IRQ chip with `IRQF_ONESHOT`, and adds variant-specific regulator/GPIO children with the IRQ domain.

State and persistence: the core does not allocate a private state structure; devm owns the regmap and IRQ data. Hardware state includes PMIC voltage, GPIO, DVFS, backup mode, and interrupt registers, with volatile status ranges excluded from cache.

Dependencies and integration points: depends on I2C, regmap and regmap IRQ, MFD core, ROHM generic headers, and child regulator/GPIO drivers. IRQ resources are provided through the regmap IRQ domain.

Risks: if `client->irq` is zero, `devm_regmap_add_irq_chip` will likely fail and prevent even regulator-only use. Product selection happens before regmap access filtering, so I2C read failures abort early. `bd957x_identify` reads product and revision but only validates vendor code. The driver name and I2C ID table only name BD9571MWV despite OF supporting BD9574MWF.

Test signals: probe BD9571 and BD9574 products, vendor mismatch handling, IRQ chip delivery for PMIC interrupt bits, regulator/GPIO child binding, no-IRQ board behavior, and regmap table coverage for DVFS/GPIO/interrupt registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bd9571mwv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bq257xx.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/bq257xx.c

Purpose: implements the MFD core for TI BQ25703A/BQ257xx buck-boost charger devices. It creates a 16-bit little-endian I2C regmap and registers regulator and charger child devices.

Important APIs and functions: `bq257xx_probe` allocates `struct bq257xx_device`, initializes regmap, stores client data, and calls `devm_mfd_add_devices`. The regmap config defines read-only manufacturer/status ranges, volatile control/status/ADC ranges, and MAPLE caching.

Control flow: probe allocates state, stores the I2C client, initializes the BQ25703 regmap with 8-bit register addresses and 16-bit little-endian values, attaches state to the client, and creates `"bq257xx-regulator"` and `"bq257xx-charger"` children.

State and persistence: parent state is `struct bq257xx_device` with client and regmap. Charger and regulator runtime state is owned by children; hardware register state persists in the charger IC.

Dependencies and integration points: depends on I2C, regmap, MFD core, and child drivers for charger and regulator functions. OF compatible is `"ti,bq25703a"` and I2C ID is `"bq25703a"`.

Risks: no device-ID check is performed even though manufacturer/device ID registers are defined read-only. No IRQ support or resources are provided. The writeable table is represented as "all except readonly range"; if future status registers appear outside that range, regmap may permit unintended writes.

Test signals: probe on BQ25703A hardware, 16-bit endian register reads/writes, child charger/regulator binding, rejection of writes to read-only manufacturer/status range, and error handling for regmap or child registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bq257xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cgbc-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/cgbc-core.c

Purpose: implements the Congatec Board Controller core driver for selected x86 Congatec modules. It discovers supported boards by DMI, registers a platform device with fixed I/O-port resources, manages a controller session, exports a command transport helper, exposes firmware version through sysfs, and registers watchdog, GPIO, I2C, hwmon, and backlight children.

Important APIs and functions: exported command API is `cgbc_command`. Lifecycle functions are `cgbc_init`, `cgbc_exit`, `cgbc_probe`, and `cgbc_remove`. Session helpers include `cgbc_wait_device`, `cgbc_session_command`, `cgbc_session_request`, and `cgbc_session_release`; command-port locking helpers are `cgbc_command_lock` and `cgbc_command_unlock`. `cgbc_get_version` reads firmware revision using command `0x21`.

Control flow: module init checks the DMI table for conga-SA7 or conga-SA8, registers a synthetic platform device with session and command I/O-port ranges, then registers the driver. Probe maps both I/O-port windows, initializes a mutex, requests a valid controller session handle, queries firmware revision, and adds child devices. `cgbc_command` serializes access, locks the command interface with the session handle, waits for strobe readiness, writes command bytes plus XOR checksum in manual/auto modes, strobes execution, reads status/data/checksum, validates the response checksum, unlocks, and returns optional status.

State and persistence: `struct cgbc_device_data` holds device, mapped I/O windows, mutex, session handle, and firmware version. The controller session persists from probe until remove; child devices share the exported command helper and parent state. Hardware command/session state lives in fixed I/O ports.

Dependencies and integration points: depends on DMI matching, platform devices, I/O-port mapping, polling helpers, sysfs attributes, MFD core, and child drivers named `"cgbc-wdt"`, `"cgbc-gpio"`, two `"cgbc-i2c"` instances, `"cgbc-hwmon"`, and `"cgbc-backlight"`. Child drivers call `cgbc_command` to transact with the board controller.

Risks: module init registers the platform device before the platform driver and does not unregister it if driver registration fails. Fixed I/O-port ranges assume no conflicts. Command framing is timing-sensitive and uses short polling timeouts; firmware stalls produce transport errors. Response data larger than the caller buffer is truncated before checksum comparison, which can cause checksum mismatch or hide extra data depending on firmware behavior. Session release happens before `mfd_remove_devices` in remove, so child teardown must not issue commands after release.

Test signals: DMI-gated module load on supported/unsupported boards, I/O resource mapping, firmware version sysfs output, command checksum success/failure injection, concurrent child command serialization, watchdog/GPIO/I2C/hwmon/backlight child binding, and remove/unload ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cgbc-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cros_ec_dev.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/cros_ec_dev.c

Purpose: implements the ChromeOS EC platform MFD "device" layer. It creates a stable class device under the `chromeos` class, detects dedicated MCU roles and EC features, and hotplug-adds feature-specific and platform EC child devices such as char device, debugfs, hwmon, sysfs, sensor hub, USB-PD, GPIO, RTC, LED, watchdog, UCSI, charger control, lightbar, peripheral charger, and VBC NVRAM.

Important APIs and functions: module lifecycle is `cros_ec_dev_init`/`cros_ec_dev_exit`; platform lifecycle is `ec_device_probe`/`ec_device_remove`; class release is `cros_ec_class_release`. Detection uses `cros_ec_check_features`, `cros_ec_get_sensor_count`, `cros_ec_cmd` with `EC_CMD_PCHG_COUNT`, DMI match for legacy Link lightbar, and OF property `"google,has-vbc-nvram"`.

Control flow: module init registers the `chromeos` class and platform driver. Probe allocates `struct cros_ec_dev`, links it to parent `ec_dev`, initializes feature cache sentinels, creates a class device named from platform data, detects whether the EC is a fingerprint/ISH/SCP/touchpad MCU and adjusts the exposed EC name, adds sensorhub if sensors exist, iterates feature-to-cell mappings, adds USB-PD charger/logging unless UCSI already supplies power information, adds lightbar by feature or Link DMI quirk, adds OF-only USB-PD notifier, queries peripheral charger count, adds always-present platform children, and adds VBC child if the parent OF node advertises it. Remove removes MFD children and unregisters the class device.

State and persistence: `struct cros_ec_dev` stores parent EC device pointer, command offset, class device, feature cache, and platform device linkage. Child devices are hotplug MFD devices and may persist only while this platform device is bound. EC firmware features and peripheral charger count are queried live from the EC.

Dependencies and integration points: depends on the lower-level ChromeOS EC transport/protocol device as parent driver data, platform data (`struct cros_ec_platform`), DMI, OF, MFD hotplug APIs, ChromeOS EC command definitions, and the child drivers named by the cell tables. The `chromeos` class gives userspace a stable namespace for EC/MCU devices.

Risks: many child-add failures are logged but non-fatal, so partial EC functionality is expected and must be diagnosed from logs. Feature detection requires EC command support; older firmware may rely on quirks like DMI Link lightbar or platform cells. The code assumes platform data is present and contains `cmd_offset`/`ec_name`. USB-PD charger is intentionally skipped when UCSI is present to avoid duplicate power-supply providers. Class device lifetime uses manual `device_initialize`/`device_add`/`put_device` plus kzalloc release, so error paths are sensitive.

Test signals: class registration and `/sys/class/chromeos` device creation, feature-cache queries for each `EC_FEATURE_*`, child enumeration with ECs that support sensors, USB-PD, UCSI, GPIO, RTC, LED, charger, hang detect, lightbar, PCHG, and VBC; old Link DMI lightbar behavior; failure injection for individual `mfd_add_hotplug_devices`; and remove/unload cleanup without leaked class devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cros_ec_dev.c -->
