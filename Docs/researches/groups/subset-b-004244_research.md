# subset-b-004244 research

Grouped research for Linux MFD driver sources under `sources/distributed-fs/ceph-client/drivers/mfd`. Each section is self-contained for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lp3943.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/lp3943.c

Purpose: this is the MFD core for the TI/National LP3943, a 16-output device that exposes the same pins as GPIOs and PWM channels. The file owns the I2C binding, shared `struct lp3943` setup, and child device registration for `lp3943-pwm` and `lp3943-gpio`.

Important APIs, types, and functions: `lp3943_mux_cfg[]` maps all 16 outputs to 2-bit mux fields across `LP3943_REG_MUX0..3`; child drivers consume it through `lp3943->mux_cfg`. `lp3943_read_byte()`, `lp3943_write_byte()`, and `lp3943_update_bits()` are exported GPL helpers over the shared regmap. `lp3943_regmap_config` is an 8-bit register/value map with `LP3943_MAX_REGISTERS`. `lp3943_probe()` allocates state, initializes `devm_regmap_init_i2c()`, stores platform data and the mux table, and calls `devm_mfd_add_devices()`.

Control flow: module load registers an I2C driver for `"lp3943"` and OF compatible `"ti,lp3943"`. Probe is straight-line: allocate, create regmap, publish client data, then add PWM/GPIO cells. There is no remove path because devres tears down regmap and children.

State and persistence: runtime state is the in-memory `struct lp3943` plus hardware register contents. The driver does not cache policy beyond the regmap and has no suspend/resume handling. Mux/pin state persists in chip registers until changed or reset.

Dependencies and integration points: depends on I2C, regmap, MFD core, GPIO/PWM child drivers, `linux/mfd/lp3943.h`, platform data, and optional device tree child matching via `.of_compatible`.

Risks: there is no explicit chip ID check, so a bad I2C match may instantiate child devices against the wrong peripheral. Register bounds are minimal and child drivers rely on the exported helpers to pass valid addresses/masks. Tests should cover I2C probe, regmap failure propagation, child registration, mux bit updates for every channel, and DT population of the two child nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lp3943.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lp873x.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/lp873x.c

Purpose: this file is the I2C MFD core for TI LP8732/LP8733 PMICs. It initializes the shared register map, records the OTP revision, and creates regulator and GPIO child devices.

Important APIs, types, and functions: `lp873x_regmap_config` configures an 8-bit regmap up to `LP873X_REG_MAX`. `lp873x_cells[]` registers `lp873x-regulator` and `lp873x-gpio`. `lp873x_probe()` allocates `struct lp873x`, initializes the regmap, reads `LP873X_REG_OTP_REV`, stores `lp873->rev`, and calls `mfd_add_devices()`.

Control flow: the I2C driver matches `"ti,lp8733"`, `"ti,lp8732"`, or ID `"lp873x"`. Probe fails immediately on allocation, regmap, or OTP-read failure. If those pass, children are registered with `PLATFORM_DEVID_AUTO`. There is no explicit remove hook, so child removal is handled by normal device lifetime only when the driver is unbound.

State and persistence: persistent hardware state is the PMIC register file. The driver stores only `dev`, `regmap`, and OTP revision in `struct lp873x`; it does not perform reset, runtime PM, interrupt setup, or register caching policy beyond regmap defaults.

Dependencies and integration points: integrates with I2C, regmap, MFD core, `linux/mfd/lp873x.h`, LP873x regulator/GPIO drivers, OF matching, and platform-device child creation.

Risks: `mfd_add_devices()` is not devm-managed here, and there is no remove callback in this file, so unload/unbind behavior should be checked against kernel core cleanup expectations. There is no hardware ID validation beyond successful OTP read. Test signals include probe with missing I2C device, failed OTP read, correct `rev` extraction mask, and child device creation for both compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lp873x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lp87565.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/lp87565.c

Purpose: this is the TI LP87565/LP875xx-Q1 MFD core. It sets up I2C regmap access, handles an optional reset GPIO, records OTP revision/device type, and registers regulator and GPIO children.

Important APIs, types, and functions: `lp87565_regmap_config` defines an 8-bit regmap through `LP87565_REG_MAX`. `of_lp87565_match_table[]` maps DT compatibles to `LP87565_DEVICE_TYPE_*`. `lp87565_probe()` allocates `struct lp87565`, initializes regmap, toggles optional `"reset"` GPIO, reads `LP87565_REG_OTP_REV`, stores `rev` and `dev_type`, and calls `devm_mfd_add_devices()`. `lp87565_shutdown()` asserts reset during shutdown.

Control flow: probe is linear but includes a reset pulse if a GPIO is available: assert high, wait 2-4 ms, deassert low, wait 1.5-3 ms before I2C. `-EPROBE_DEFER` from reset GPIO is propagated. Other reset-GPIO errors are recorded in `ret` but do not abort unless the descriptor exists, which makes GPIO error handling worth auditing.

State and persistence: runtime state includes `regmap`, optional `reset_gpio`, OTP revision, and matched device type. The shutdown hook changes persistent hardware state by asserting reset. There is no runtime PM or IRQ state.

Dependencies and integration points: I2C, regmap, GPIO descriptors, MFD core, `linux/mfd/lp87565.h`, OF match data, and LP87565 regulator/GPIO child drivers.

Risks: undocumented reset timing is explicitly guessed, so board-specific reset requirements can be fragile. `i2c_get_match_data()` must return a valid type; plain I2C ID binding has less type information than OF. Tests should cover DT match variants, reset GPIO present/absent/deferred, OTP read failure, shutdown reset assertion, and child registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lp87565.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lp8788-irq.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/lp8788-irq.c

Purpose: this companion file implements the LP8788 interrupt controller for the LP8788 MFD core. It maps PMIC interrupt status bits into nested Linux IRQs used by LP8788 child devices.

Important APIs, types, and functions: `struct lp8788_irq_data` holds the parent `struct lp8788`, mutex, IRQ domain, and enabled-bit shadow. `_irq_to_addr()`, `_irq_to_enable_addr()`, `_irq_to_mask()`, and `_irq_to_val()` translate enum IRQ IDs to status/enable registers. `lp8788_irq_chip` provides enable/disable and bus lock/sync operations. `lp8788_irq_handler()` reads three interrupt-status bytes and calls `handle_nested_irq()` for active bits. `lp8788_irq_init()` creates a linear firmware-node IRQ domain and requests a falling-edge threaded parent IRQ. `lp8788_irq_exit()` frees the parent IRQ and removes the domain.

Control flow: child IRQ enable/disable only updates the in-memory `enabled[]` array; hardware enable bits are written in `irq_bus_sync_unlock()` under `irq_lock`. The top-level threaded handler bulk-reads status registers and reports each asserted bit through the domain mapping.

State and persistence: `enabled[]` mirrors desired IRQ mask state; hardware enable registers persist until changed. `lp->irq` and `lp->irqdm` link the core driver to this interrupt layer. No devm cleanup is used for `request_threaded_irq()`, so explicit exit is required.

Dependencies and integration points: depends on the LP8788 exported regmap helpers, Linux IRQ domains, nested threaded IRQ handling, and resources declared in `lp8788.c`.

Risks: the handler comment says it reports only enabled IRQs, but the code checks only status bits and not `enabled[]`; if masked hardware status still appears, nested IRQs may be invoked unexpectedly. `free_irq(lp->irq, lp->irqdm)` passes a different dev_id than the requested `irqd`, which is a cleanup-risk signal. Tests should include IRQ domain mapping, enable/disable register writes, parent IRQ status fan-out, invalid IRQ-number behavior, and remove/error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lp8788-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lp8788.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/lp8788.c

Purpose: this is the LP8788 MFD core, exposing a PMIC with bucks, LDOs, ADC, charger, RTC, backlight, vibrator, and key LED children over I2C.

Important APIs, types, and functions: `lp8788_devs[]` enumerates 4 buck regulators, 12 digital LDOs, 10 analog LDOs, and functional children. `chg_irqs[]` and `rtc_irqs[]` attach IRQ resource ranges to charger and RTC cells. Exported helpers `lp8788_read_byte()`, `lp8788_read_multi_bytes()`, `lp8788_write_byte()`, and `lp8788_update_bits()` wrap the shared regmap for child drivers. `lp8788_platform_init()` invokes optional platform init. `lp8788_probe()` creates the regmap, runs platform init, initializes IRQs, and registers all children.

Control flow: the driver is registered at `subsys_initcall`, earlier than a normal module init, so child regulators and power services are available early. Probe ordering is important: regmap, platform callback, IRQ domain, then child devices. On child-registration failure it calls `lp8788_irq_exit()`. Remove explicitly removes children and tears down IRQs.

State and persistence: `struct lp8788` stores regmap, platform data, device, parent IRQ, and IRQ domain. Hardware register state persists in the PMIC; this core does not implement suspend/resume or regcache.

Dependencies and integration points: I2C, regmap, MFD core, `linux/mfd/lp8788.h`, the custom IRQ layer in `lp8788-irq.c`, platform data callbacks, and child drivers named by `LP8788_DEV_*`.

Risks: many child cells are registered unconditionally, so missing child driver support or wrong board data can surface late. The optional platform init can mutate hardware before IRQ setup. Tests should cover helper functions, platform-init failure, IRQ failure, child resource ranges, remove cleanup, and early-init ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lp8788.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lpc_ich.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/lpc_ich.c

Purpose: this PCI MFD driver binds Intel ICH/PCH LPC bridge functions and exposes embedded watchdog, GPIO/pinctrl, and SPI flash controller devices. It covers a large PCI ID matrix from early ICH through Bay Trail, Avoton, Apollo Lake, Denverton, Gemini Lake, and related PCH families.

Important APIs, types, and functions: `lpc_chipset_info[]` maps enum chipsets to names, iTCO watchdog versions, GPIO versions, GPIO-info tables, and SPI types. `lpc_ich_priv` records config offsets and saved PCI config bytes. Static `mfd_cell`s represent `iTCO_wdt`, `gpio_ich`, and `intel-spi`; Apollo Lake and Denverton pinctrl cells use P2SB-derived MMIO resources. `lpc_ich_init_wdt()`, `lpc_ich_init_gpio()`, `lpc_ich_init_pinctrl()`, and `lpc_ich_init_spi()` discover resources and add children. `lpc_ich_restore_config_space()` restores ACPI/GPIO/PMC decode bits changed during probe.

Control flow: `lpc_ich_probe()` allocates private state, selects GPIO config offsets based on chipset generation, then independently attempts watchdog, legacy GPIO, pinctrl, and SPI initialization based on the chipset table. At least one child must register successfully. Each initializer reads PCI config or P2SB resources, validates ACPI/resource conflicts, enables decode where needed, fills resources/platform data, and calls `mfd_add_devices()`.

State and persistence: the driver temporarily changes PCI config decode bits for ACPI, GPIO, or PMC space and caches previous values for restore on remove or total probe failure. Child platform data includes watchdog version/name and GPIO capability data. Hardware BAR/decode state persists outside the driver unless restored.

Dependencies and integration points: PCI, ACPI conflict checks, MFD core, pinctrl, Intel P2SB helpers, iTCO watchdog platform data, intel-spi board info, software nodes, and downstream GPIO/pinctrl/SPI/watchdog drivers.

Risks: global static resource and cell objects are mutated (`num_resources`, starts/ends, platform data), so repeated bind/unbind and partial failures deserve scrutiny. Resource conflict handling intentionally ignores some conflicts and may register a reduced GPIO cell. SPI write-enable callbacks alter flash-protection bits. Tests should cover representative chipset entries for iTCO v1/v2/v3/v5, GPIO conflict paths, ACPI-present pinctrl skip, P2SB failures, SPI BYT/LPT/BXT resource discovery, config-space restore, and no-cell failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lpc_ich.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lpc_sch.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/lpc_sch.c

Purpose: this PCI MFD driver supports Intel Poulsbo SCH, Tunnel Creek, Centerton, and Quark X1000 LPC/ILB devices, exposing SMBus, GPIO, and watchdog children from LPC decode registers.

Important APIs, types, and functions: `sch_chipset_info[]` provides per-chipset I/O sizes. `lpc_sch_get_io()` reads a config dword, checks the enable bit, and fills an I/O resource. `lpc_sch_populate_cell()` allocates a resource, calls `lpc_sch_get_io()`, and fills an `mfd_cell`. `lpc_sch_probe()` builds up to three cells: `isch_smbus`, `sch_gpio`, and `ie6xx_wdt`.

Control flow: probe attempts each possible child in order. Return `LPC_NO_RESOURCE` or `LPC_SKIP_RESOURCE` skips a cell without failing; negative errors abort. If every cell is skipped, probe returns `-ENODEV`. Remove calls `mfd_remove_devices()`.

State and persistence: there is no long-lived private data. Resources are devm-allocated and cell arrays are stack-local during registration. Hardware decode register state is only read, not modified.

Dependencies and integration points: PCI IDs, MFD core, ACPI headers, and child drivers for Intel SCH SMBus, GPIO, and watchdog. Cells set `ignore_resource_conflicts = true`, reflecting legacy firmware/ACPI overlap expectations.

Risks: decode-disabled or zero base registers lead to missing child devices; the driver intentionally tolerates that until all resources are absent. Stack-local `mfd_cell` data must be fully copied by MFD core, which is the expected API contract but a point worth remembering. Tests should exercise each chipset's resource sizes, disabled decode warnings, zero-base skips, all-disabled failure, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lpc_sch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ls2k-bmc-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ls2k-bmc-core.c

Purpose: this is the Loongson-2K BMC PCI MFD core. It exposes framebuffer and IPMI child devices from BMC BAR resources and contains reset-recovery logic for the LS2K BMC/LS7A PCIe link.

Important APIs, types, and functions: `ls2k_bmc_cells[]` registers one `simple-framebuffer` and five `ls2k-ipmi-si` children. `struct ls2k_bmc_ddata` stores saved BMC and bridge PCI config values plus reset work. `ls2k_bmc_save_pci_data()` captures bridge/BMC config registers. `ls2k_bmc_recover_pci_data()` runs under `stop_machine()` to clear bridge BARs, wait for reset, restore config, retrain PCIe, wait for firmware/DDR, and restore BMC BAR/IRQ state. `ls2k_bmc_init()` wires PCIe and GPIO reset interrupts. `ls2k_bmc_parse_mode()` reads a mode string from BAR0 and fills `simplefb_platform_data`.

Control flow: probe enables the PCI device, allocates driver data, initializes interrupt/reset recovery, parses display mode from BAR0, removes conflicting firmware framebuffers, then registers children relative to BAR0. Reset interrupts are rate-limited by `LS2K_BMC_INT_INTERVAL` and schedule work; the work uses `stop_machine()` to avoid CPU access during PCIe loss.

State and persistence: the driver persists saved PCI config state in memory for reset recovery. It programs Loongson GPIO registers via ioremap to enable the reset interrupt. Framebuffer mode comes from a BAR memory string and child resources are offsets within the BMC BAR.

Dependencies and integration points: PCI, ACPI GSI registration, aperture conflict removal, simplefb platform data, platform devices, workqueues, stop_machine, virtual terminal console refresh, and LS2K IPMI child drivers.

Risks: reset recovery is hardware-specific and uses long delays including a 10-second wait under a reset work path. `ls2k_bmc_recover_pci_data()` is declared `int` but returns `false` in some paths, effectively `0`, which may hide failures from `stop_machine()`. Mode parsing trusts BAR content formatting. Tests should include BAR0 mode parsing, aperture removal errors, PCI config save/restore, interrupt throttling, GPIO/GSI setup, and reset recovery failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ls2k-bmc-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/macsmc.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/macsmc.c

Purpose: this platform MFD driver is the Apple Silicon SMC core. It talks to SMC firmware through Apple RTKit, exports SMC key read/write APIs, manages notification delivery, and registers input, power, GPIO, hwmon, reboot, and RTC children.

Important APIs, types, and functions: `apple_smc_cmd_locked()` formats mailbox messages with command, size, write size, sequence ID, and data fields, sends them via `apple_rtkit_send_message()`, waits for completion, validates sequence/result, and returns response size/data. `apple_smc_rw_locked()` handles read/write/RW key transactions and SRAM shared-memory transfers. Exported APIs include `apple_smc_read()`, `apple_smc_write()`, `apple_smc_rw()`, `apple_smc_get_key_by_index()`, `apple_smc_get_key_info()`, `apple_smc_enter_atomic()`, and `apple_smc_write_atomic()`. RTKit callbacks handle crash, shared-memory setup, early replies, and notifications.

Control flow: probe maps the SRAM resource, initializes RTKit, wakes firmware, starts endpoint `0x20`, sends initialize, waits for boot shared-memory reply, reads key count, enables notifications, and registers child cells. Normal commands use `smc->mutex` and completions. Atomic shutdown writes use a spinlock, RTKit polling, and a pending flag.

State and persistence: `struct apple_smc` stores RTKit handle, SRAM mapping, shared-memory descriptor, boot stage, key count, sequence ID, completions, notifier chain, mutex/spinlock state, and atomic-mode flags. Hardware state includes SMC key values and notification enable key `NTAP`.

Dependencies and integration points: Apple RTKit, platform resources, OF compatible `"apple,t8103-smc"`/`"apple,smc"`, MFD core, blocking notifier chain, exported SMC key API for child drivers, and SRAM shared memory validation.

Risks: protocol sequencing is strict; missed completions or ID mismatch cause I/O failure. Atomic mode intentionally disables notifications and rejects normal commands. Shared-memory bounds checking must remain correct to avoid invalid SRAM access. Tests should cover boot timeout, RTKit crash, read/write small-vs-large payloads, key info decoding, notification fan-out, atomic write path, and child registration after key-count read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/macsmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/madera-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/madera-core.c

Purpose: this is the shared MFD core for Cirrus Logic Madera codec families. It handles power rails, reset sequencing, boot polling, chip identification, errata, runtime PM, 32 kHz clock setup, hardware patches, and child device registration.

Important APIs, types, and functions: child arrays define per-codec cells such as `madera-pinctrl`, `madera-irq`, `madera-micsupp`, `madera-gpio`, `madera-extcon`, and codec-specific ASoC children. `madera_name_from_type()` names enum variants. `madera_wait_for_boot_noack()` and `madera_wait_for_boot()` poll/ack boot status. `madera_soft_reset()`, `madera_enable_hard_reset()`, and `madera_disable_hard_reset()` implement reset policy. `madera_runtime_suspend()`/`madera_runtime_resume()` manage DCVDD, hard reset, regcache state, and cache sync. `madera_dev_init()` is the main initializer exported to bus drivers. `madera_dev_exit()` removes children and powers the device down.

Control flow: `madera_dev_init()` initializes shared state, copies platform data, gets optional clocks and reset GPIO, places regmaps in cache-only mode, adds LDO1 early for codecs that may supply DCVDD internally, requests regulators, enables supplies, releases reset, waits for boot, reads silicon ID, selects a patch function and child set, optionally soft-resets, reads revision, applies patch, enables MCLK2-derived 32 kHz clock, enables runtime PM, and registers children. Errors unwind regulators, reset, clock, and children in reverse order.

State and persistence: `struct madera` stores device type/name/revision, regmaps, regulators, clocks, reset GPIO, notifier, runtime-PM state, micbias counts, and reset errata. Register caches preserve state across runtime suspend and are synced on resume. Hardware reset/power state is actively changed.

Dependencies and integration points: I2C/SPI bus frontends, regmap configs and patch functions from codec-specific files, regulators, clocks, GPIO descriptors, MFD core, runtime PM, OF match table, and downstream audio/extcon/gpio/irq drivers.

Risks: power/reset sequencing is intricate and hardware-specific, especially CS47L15 reset errata and optional reset GPIO behavior. Child shutdown order intentionally avoids devm for some resources. Tests should cover each supported type, ID/type mismatch, missing MCLK2 warning, reset GPIO absent/present, LDO1 ordering, patch failure, runtime suspend/resume cache sync, and unwind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/madera-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/madera-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/madera-i2c.c

Purpose: this is the I2C transport frontend for Cirrus Logic Madera codecs. It chooses the correct 16-bit and 32-bit regmap configurations for the matched codec type and delegates device bring-up to `madera_dev_init()`.

Important APIs, types, and functions: `madera_i2c_probe()` obtains `type` from `i2c_get_match_data()`, selects codec-specific I2C regmap configs under the relevant `CONFIG_MFD_CS47L*` gate, allocates `struct madera`, initializes both regmaps with `devm_regmap_init_i2c()`, fills type/name/device/IRQ fields, and calls `madera_dev_init()`. `madera_i2c_remove()` calls `madera_dev_exit()`. `madera_i2c_id[]` lists all supported device names.

Control flow: unsupported or not-built-in codec types fail before allocation, with an error naming the missing codec support. Probe creates the 16-bit map first and the 32-bit map second; either failure aborts. Successful probe has no additional bus-specific side effects after entering the shared core.

State and persistence: bus-level state is minimal: a `struct madera` attached as driver data by the shared core and two regmaps over the same I2C device. Persistent codec state is managed by `madera-core.c`.

Dependencies and integration points: I2C, OF match table exported by `madera-core.c`, codec-specific regmap configs declared in `madera.h`, shared PM ops `madera_pm_ops`, and the Madera common core.

Risks: OF and I2C match data must agree with built-in codec support; otherwise probe returns `-EINVAL`. Remove assumes `madera_dev_init()` set driver data. Tests should cover every type-to-regmap selection, disabled Kconfig support, regmap init failures, IRQ propagation, and remove cleanup through `madera_dev_exit()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/madera-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/madera-spi.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/madera-spi.c

Purpose: this is the SPI transport frontend for Cirrus Logic Madera codecs. It mirrors the I2C frontend but initializes SPI regmaps and then uses the shared Madera core.

Important APIs, types, and functions: `madera_spi_probe()` uses `spi_get_device_match_data()`, selects codec-specific 16-bit and 32-bit SPI regmap configs, allocates `struct madera`, initializes regmaps with `devm_regmap_init_spi()`, stores `type`, `type_name`, `dev`, and `irq`, then calls `madera_dev_init()`. `madera_spi_remove()` calls `madera_dev_exit()`. `madera_spi_ids[]` lists the supported modaliases.

Control flow: selection and error flow are the same as the I2C frontend: unsupported type or missing Kconfig support fails early, then allocation and two regmap initializations must succeed before entering shared initialization. Remove relies on shared core driver data.

State and persistence: state consists of the shared `struct madera`, SPI-backed regmaps, and the SPI IRQ line. Power, reset, register cache, and child devices are owned by `madera-core.c`.

Dependencies and integration points: SPI core, regmap SPI support, shared Madera OF table and PM ops, codec-specific SPI regmap configs, and `madera_dev_init()`/`madera_dev_exit()`.

Risks: because I2C and SPI frontends are nearly parallel, fixes must remain consistent across both files. Bad match data or missing Kconfig produces `-EINVAL`; transport-specific regmap failures should be tested separately. Test signals include all codec type cases, absent support, 16-bit/32-bit regmap failures, IRQ propagation, PM ops binding, and remove ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/madera-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/madera.h -->
# sources/distributed-fs/ceph-client/drivers/mfd/madera.h

Purpose: this private header connects the Madera bus frontends, shared MFD core, and codec-specific regmap/patch implementations.

Important APIs, types, and functions: it forward-declares `struct madera`, exports `madera_pm_ops`, `madera_of_match`, `madera_dev_init()`, `madera_dev_exit()`, and `madera_name_from_type()`. It declares 16-bit and 32-bit regmap configurations for SPI and I2C variants of CS47L15, CS47L35, CS47L85, CS47L90, and CS47L92 families. It also declares patch functions `cs47l15_patch()`, `cs47l35_patch()`, `cs47l85_patch()`, `cs47l90_patch()`, and `cs47l92_patch()`.

Control flow: this header has no runtime control flow, but it defines the compile-time contract: bus drivers pick regmap configs and call the shared init/exit functions; the core chooses patch functions after hardware ID verification.

State and persistence: no state is stored here. The declarations represent shared state in other translation units, especially the regmap definitions and device initialization functions.

Dependencies and integration points: includes OF and PM headers and relies on public `linux/mfd/madera/core.h` users to define `enum madera_type`. It is included by `madera-core.c`, `madera-i2c.c`, and `madera-spi.c`, and by codec-specific implementation files providing the declared symbols.

Risks: missing or mismatched declarations lead to link-time failures across Kconfig combinations. Any new codec family needs both transport regmap declarations and patch/core handling kept in sync. Test signals are build-matrix coverage for each `CONFIG_MFD_CS47L*` option, I2C/SPI frontend compilation, and symbol export/link validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/madera.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max14577.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max14577.c

Purpose: this MFD core supports Maxim MAX14577 and MAX77836 MUIC/charger PMIC variants. It initializes MUIC and, for MAX77836, PMIC register maps and IRQ chips, exposes charger-current helper data, and registers variant-specific children.

Important APIs, types, and functions: `maxim_charger_currents[]` and `maxim_charger_calc_reg_current()` are exported for charger/regulator drivers. `max14577_devs[]` and `max77836_devs[]` define MUIC, regulator, charger, and battery cells. Regmap volatile callbacks distinguish MUIC/PMIC status registers. `max77836_init()` creates a dummy PMIC I2C device, initializes its regmap, unmasks interrupt sources, and adds a PMIC IRQ chip. `max14577_i2c_probe()` creates the primary regmap, selects variant cell/IRQ tables, adds IRQ chips, performs MAX77836 extra init, and registers children.

Control flow: OF or I2C match data selects `dev_type`. Probe requires platform data or allocates empty data for OF. It installs the primary IRQ chip first, then optional MAX77836 PMIC setup, then child cells. Remove tears down wakeup, children, IRQ chips, and the dummy PMIC device. Suspend enables wake if allowed and disables IRQ to avoid I2C access before resume.

State and persistence: `struct max14577` stores primary and optional PMIC I2C clients, regmaps, IRQ data, type, and wake state. Hardware interrupt mask/source registers are modified during initialization and suspend/resume changes IRQ wake state.

Dependencies and integration points: I2C, regmap, regmap-irq, MFD core, MAX14577 private headers, MUIC/regulator/charger/battery children, OF match data, and wakeup framework.

Risks: multiple IRQ chips share one physical IRQ for MAX77836, requiring correct `IRQF_SHARED` usage and cleanup. The charger-current helper uses compile-time checks to keep current tables consistent. Tests should cover current calculation edge cases, variant matching, dummy PMIC registration failure, interrupt unmasking, child registration, suspend/resume IRQ behavior, and cleanup after partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max14577.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max7360.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max7360.c

Purpose: this is the Maxim MAX7360 I2C IO expander MFD core. It resets the GPIO/PWM block, masks default-on interrupts, and registers pinctrl, PWM, keypad, rotary, GPO, and GPIO child devices.

Important APIs, types, and functions: `max7360_cells[]` enumerates six child cells. `max7360_regmap_config` uses an 8-bit cached regmap with volatile ranges for key FIFO and live status/config counters. `max7360_reset()` resets GPIO configuration, drops the GPIO cache range, clears autosleep, and resets debounce/GPO count. `max7360_mask_irqs()` masks per-port GPIO/PWM interrupts and reads `MAX7360_REG_GPIOIN` to acknowledge pending IRQs. `max7360_probe()` initializes regmap, resets/enables the chip, masks IRQs, and adds children.

Control flow: probe is ordered to make hardware quiet before children bind: reset, enable GPIO/PWM module, mask IRQs, then `devm_mfd_add_devices()`. Any failure returns through `dev_err_probe()` with context.

State and persistence: persistent hardware configuration is reset and rewritten at probe. Regmap cache uses `REGCACHE_MAPLE`, with explicit cache dropping after GPIO reset to avoid stale child-visible state. The core stores no private driver data.

Dependencies and integration points: I2C, regmap, MFD core, MAX7360 register definitions, and child drivers for pinctrl/PWM/keypad/rotary/GPO/GPIO.

Risks: masking all port interrupts before child drivers load avoids spurious shared interrupt behavior but can affect boot-time interrupt expectations. Resetting GPIO configuration at probe is destructive to firmware-set state. Tests should verify reset writes, cache drop, interrupt mask loop for all ports, GPIOIN ack read, child registration, and regmap volatile behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max7360.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77541.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max77541.c

Purpose: this Analog Devices/Maxim MFD core supports MAX77540 and MAX77541 PMICs. It creates a regmap, installs several regmap IRQ chips, initializes wakeup, and registers regulator plus optional ADC children.

Important APIs, types, and functions: `max77541_src_irq_chip`, `max77541_topsys_irq_chip`, `max77541_buck_irq_chip`, and `max77541_adc_irq_chip` model interrupt source, top-system, buck, and ADC interrupt registers. `max77540_devs[]` contains only a regulator cell; `max77541_devs[]` adds ADC. `max77541_pmic_irq_init()` registers the IRQ chips on the same I2C IRQ, adding ADC only for MAX77541. `max77541_pmic_setup()` selects children by ID, initializes IRQs, wakeup, and MFD cells. `max77541_probe()` allocates state, gets match data, initializes regmap, and calls setup.

Control flow: match data from OF/I2C selects MAX77540 or MAX77541. Probe fails for absent ID, regmap failure, IRQ setup failure, wakeup initialization failure, or child registration failure. Device-managed APIs perform cleanup.

State and persistence: `struct max77541` stores I2C client, chip ID, regmap, and regmap IRQ chip data. Hardware interrupt masks/status are managed by regmap-irq. Wakeup state is enabled via devm helper.

Dependencies and integration points: I2C, regmap, regmap-irq, device property matching, MFD core, MAX77541 headers, regulator and ADC child drivers.

Risks: several independent regmap IRQ chips share one physical IRQ; mask/status definitions must remain non-overlapping and child drivers need the correct virtual IRQ domains. Tests should cover both variants, missing match data, ADC IRQ omission for MAX77540, wakeup initialization, interrupt propagation, and child count selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77541.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77620.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max77620.c

Purpose: this built-in I2C MFD core supports Maxim MAX77620, MAX20024, and MAX77663 PMICs. It initializes regmap/IRQ handling, parses flexible power sequencer settings, exposes children for regulators, clocks, watchdog, GPIO, RTC, power, and thermal functions, and can register a system power-off hook.

Important APIs, types, and functions: variant child arrays and regmap configs define per-chip access ranges and cache policy. `max77620_top_irq_chip` maps top-level PMIC interrupts and uses `max77620_irq_global_mask()`/`max77620_irq_global_unmask()` to manipulate `GLBLM` around IRQ service. `max77620_get_fps_period_reg_value()`, `max77620_config_fps()`, and `max77620_initialise_fps()` parse DT `fps` child nodes and program FPS timing/event state. `max77620_read_es_version()` logs CID/OTP/ES version. `max77620_pm_power_off()` triggers soft reset/power-off via `ONOFFCNFG1`. Suspend/resume adjust FPS periods, sleep bits, WK_EN0, and IRQ state.

Control flow: probe selects variant-specific cells/regmap, initializes regmap, reads chip revision, installs regmap IRQ chip with driver data, initializes FPS, registers children with the IRQ domain, and optionally installs `pm_power_off`. The driver is registered with `builtin_i2c_driver()`, so it is not a normal unloadable module path.

State and persistence: `struct max77620_chip` stores chip ID, IRQ, regmap, FPS period arrays, sleep/LPM flags, top IRQ data, and power-off state. FPS configuration and sleep/wake bits persist in PMIC registers. Regmap uses Maple cache with defined volatile/cacheable ranges.

Dependencies and integration points: I2C, OF child nodes, regmap, regmap-irq, MFD core, child PMIC/regulator/clock/watchdog/GPIO/RTC/power/thermal drivers, global `pm_power_off`.

Risks: FPS parsing affects suspend/shutdown sequencing and must be validated per variant. The global `max77620_scratch` power-off pointer has singleton semantics. Tests should cover all chip IDs, readable/writable range restrictions, FPS node validation, suspend/resume period switching, IRQ global masking, power-controller DT behavior, and child IRQ resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77620.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77650.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max77650.c

Purpose: this is the MAX77650/MAX77651 charger/power-supply MFD core. It validates chip ID, disables low-power mode for Linux systems, installs a regmap IRQ chip, and registers regulator, charger, GPIO, LED, and onkey children.

Important APIs, types, and functions: `max77650_cells[]` defines children and named IRQ resources for charger, GPIO, and onkey. `max77650_irqs[]` maps global and charger interrupts, including GPIO edge type encoding with `type_in_mask`. `max77650_irq_chip` uses `init_ack_masked` and `clear_on_unmask`. `max77650_i2c_probe()` initializes regmap, reads `MAX77650_REG_CID`, checks supported CID variants, disables `SBIA_LPM`, adds IRQ chip, obtains its IRQ domain, and registers child devices.

Control flow: probe fails on regmap creation, unreadable CID, unsupported chip ID, power-mode update failure, IRQ-chip failure, or child registration failure. All allocations are device-managed.

State and persistence: no private struct is retained in this file; state is the regmap, regmap IRQ data, and hardware configuration. Probe changes the PMIC from low-power to normal mode, which persists until changed/reset.

Dependencies and integration points: I2C, regmap, regmap-irq, IRQ type handling, MFD core, MAX77650 child drivers, and OF compatible `"maxim,max77650"`.

Risks: forcing normal power mode may be unsuitable for ultra-low-power systems but is intentional. GPIO IRQ type encoding relies on correct mask bits. Tests should cover all accepted CID values, unsupported ID failure, low-power bit update, IRQ domain resource mapping, edge IRQ configuration, and child registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77650.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77686.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max77686.c

Purpose: this MFD core supports Maxim MAX77686 and MAX77802 PMIC families used on Samsung platforms. It sets up regmap access, PMIC interrupt handling, and PMIC/RTC/clock child devices.

Important APIs, types, and functions: `max77686_devs[]` and `max77802_devs[]` provide variant-specific child names. MAX77802 access/precious/volatile callbacks constrain regmap access and protect interrupt/update registers. `max77686_irq_chip` and `max77802_irq_chip` share the same IRQ mask table with different status/mask bases. `max77686_i2c_probe()` selects config/cells by OF match data, initializes regmap, checks `MAX77686_REG_DEVICE_ID`, adds a devm regmap IRQ chip, and registers children. Suspend/resume handles IRQ wake and disables IRQ during suspended I2C.

Control flow: OF match data selects variant. Probe validates that the device responds before installing IRQs. Child registration uses devm cleanup. Suspend enables wake if configured, then disables parent IRQ; resume reverses the sequence.

State and persistence: `struct max77686_dev` stores type, I2C client, dev, IRQ, regmap, and IRQ data. Regmap cache policy is simple for MAX77686 and Maple with access restrictions for MAX77802. IRQ wake state persists across system sleep.

Dependencies and integration points: I2C, OF, regmap, regmap-irq, MFD core, PM runtime headers, and child PMIC/RTC/clock drivers.

Risks: the driver relies on OF match data and lacks an I2C ID table path for non-DT matching. MAX77802 register accessibility tables must include all child-needed registers. Tests should cover both variants, ID-read failure, IRQ chip setup, child registration, suspend/resume ordering, and wakeup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77686.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77693.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max77693.c

Purpose: this MFD core supports the Maxim MAX77693 PMIC/MUIC/charger/haptic/LED device. It creates multiple I2C dummy clients and regmaps, installs several IRQ chips, unmasks interrupt sources, and registers functional child devices.

Important APIs, types, and functions: `max77693_devs[]` lists PMIC, charger, MUIC, haptic, and LED cells. Separate regmap configs cover PMIC, MUIC, and haptic address spaces. IRQ chips model LED, TOPSYS, charger, and MUIC interrupt blocks. `max77693_i2c_probe()` allocates `struct max77693_dev`, initializes the primary regmap, reads device ID, creates dummy MUIC and haptic I2C clients, initializes their regmaps, adds all IRQ chips, unmasks interrupt sources, and adds MFD children. Remove unwinds children, IRQ chips, and dummy clients.

Control flow: probe has a multi-stage error ladder because resources are not all devm-managed. Failures after dummy-client creation explicitly unregister clients and delete previously added IRQ chips. Runtime PM is marked active before adding children. Suspend/resume only disable/enable the IRQ when the device may wake the system.

State and persistence: `struct max77693_dev` holds primary/MUIC/haptic clients, regmaps, IRQ data pointers, type, and IRQ. Hardware interrupt source masks are changed at probe. PM runtime active state is set but not otherwise managed here.

Dependencies and integration points: I2C dummy devices, regmap, regmap-irq, MFD core, MAX77693 common/private headers, charger/MUIC/haptic/LED child drivers, and OF matching.

Risks: cleanup ordering is critical because multiple IRQ chips share one physical IRQ and multiple client addresses. Interrupt source unmask writes use bitwise complement cast and should be checked against register width expectations. Tests should cover each error label, dummy-device conflicts, IRQ fan-out, INTSRC unmasking, remove cleanup, and suspend/resume wake behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77693.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77705.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max77705.c

Purpose: this newer MAX77705 PMIC core initializes a constrained PMIC regmap, verifies hardware revision, sets active discharge, adds source IRQ handling, registers RGB/charger/haptic child devices, and enables wakeup.

Important APIs, types, and functions: `max77705_devs[]` defines OF-backed child cells. Regmap readable/writable range tables limit access through `max77705_regmap_config`. `max77705_irq_chip` maps top-level source interrupts for charger, TOP, fuel gauge, and USB-C. `max77705_i2c_probe()` allocates a `struct max77693_dev` reused for MAX77705, initializes regmap, reads `MAX77705_PMIC_REG_PMICREV`, requires `MAX77705_PASS3`, sets active discharge in `MAINCTRL1`, adds a regmap IRQ chip, registers children with its IRQ domain, and initializes wakeup. Suspend/resume disable IRQ and manage wake state.

Control flow: unsupported revision aborts with `-ENODEV`. Active discharge update does not check the return value, so later IRQ/child setup can proceed after a failed write. Device-managed resource handling handles cleanup.

State and persistence: state is the regmap, top IRQ domain, child devices, and wakeup configuration. Probe changes active-discharge hardware configuration. Suspend toggles IRQ wake state.

Dependencies and integration points: I2C, regmap, regmap-irq, MFD core, MAX77705 private definitions, MAX77693 common struct reuse, power-supply battery headers, and RGB/charger/haptic child drivers.

Risks: hard-gating to PASS3 means other silicon revisions will not bind. Ignoring active-discharge write failures is a potential diagnostic gap. Tests should cover revision filtering, regmap access tables, IRQ domain resources, active-discharge write error behavior, child registration, wake initialization, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77705.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77714.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max77714.c

Purpose: this MFD core supports Maxim MAX77714, exposing watchdog and RTC children and initializing top-level IRQ and 32 kHz oscillator behavior.

Important APIs, types, and functions: `max77714_cells[]` registers `max77714-watchdog` and `max77714-rtc`. Regmap access tables limit readable/writable registers to interrupt, oscillator, and global configuration ranges. `max77714_irq_chip` maps top-level ONOFF, RTC, GPIO, LDO, SD, and global interrupts. `max77714_setup_xosc()` sets `XOSC_RETRY`, reads oscillator status, decodes load-cap index, and logs internal/external oscillator selection. `max77714_probe()` initializes regmap, oscillator, IRQ chip, and children.

Control flow: probe fails on regmap, oscillator setup, IRQ-chip setup, or child registration failure. All resources are device-managed and there is no explicit remove or PM path.

State and persistence: the core retains no private state. It changes oscillator retry/configuration in hardware and creates a regmap IRQ domain for children. Regmap is uncached and constrained by access tables.

Dependencies and integration points: I2C, regmap, regmap-irq, MFD core, MAX77714 child watchdog/RTC drivers, and OF compatible `"maxim,max77714"`.

Risks: oscillator setup assumes reading status immediately after setting retry is adequate. GPIO/LDO/SD top IRQs are exposed in the IRQ chip but only watchdog/RTC children are registered here, so consumers must align with available children. Tests should cover oscillator status decode, regmap access restrictions, IRQ chip setup, child registration, and probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77714.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77759.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max77759.c

Purpose: this MFD core supports Maxim MAX77759, a companion PMIC for USB Type-C. It creates top, MaxQ, and charger regmaps, builds a hierarchical interrupt model, exposes MaxQ command APIs, and registers NVMEM, GPIO, and charger children.

Important APIs, types, and functions: three regmap configs define top, MaxQ, and charger access/volatile/cache tables. `max77759_pmic_irq_chip` is the parent source IRQ chip; `max77759_maxq_irq_chip`, `max77759_topsys_irq_chip`, and `max77759_chgr_irq_chip` are chained off parent virtual IRQs. `max77759_i2c_subdevs[]` describes same-address MaxQ and dummy-address charger subdevices. `max77759_maxq_command()` is an exported command/response API guarded by `maxq_lock`, using completions signaled by `apcmdres_irq_handler()`. `max77759_create_i2c_subdev()` initializes/attaches sub-regmaps. `max77759_probe()` validates PMIC ID, creates subdevices, installs IRQ hierarchy, registers block children, and finally adds top-level NVMEM.

Control flow: probe initializes the top regmap and verifies chip ID `59` before any subdevice work. Sub-regmaps are then created, with charger using a dummy I2C device at `0x69`. The parent PMIC IRQ chip is registered on the physical IRQ, then chained MaxQ/TOPSYS/charger IRQ chips are attached to parent virtual IRQs. MaxQ command completion requires APCmdRes IRQ handling.

State and persistence: `struct max77759` stores regmaps, a mutex, and command completion. Regmap caches are flat and include raw default counts. Hardware interrupt masks, MaxQ mailbox registers, and charger interrupt status are manipulated through regmap.

Dependencies and integration points: I2C, regmap, regmap-irq chained domains, MFD core, completions, mutex guards, MAX77759 public header, GPIO/charger/NVMEM child drivers, and OF/I2C matching.

Risks: hierarchical IRQ setup is sensitive to parent virtual IRQ mapping and domain suffixes. `max77759_maxq_command()` validates opcode echo but depends on timely APCmdRes IRQ completion; timeout or stale responses produce command failure. Tests should cover chip-ID rejection, dummy I2C creation, regmap access tables, IRQ hierarchy, MaxQ command timeout/opcode mismatch, child IRQ resource mapping, and cleanup through devm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77759.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77843.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max77843.c

Purpose: this MFD core supports the Maxim MAX77843 top-system/charger/fuel-gauge/MUIC/haptic device. It initializes top-system and charger regmaps, installs TOPSYS IRQ handling, unmasks interrupt sources, and registers child devices.

Important APIs, types, and functions: `max77843_devs[]` registers MUIC, regulator, charger, fuelgauge, and haptic children. `max77843_regmap_config` covers top-system registers; `max77843_charger_regmap_config` covers charger registers shared with charger regulator logic. `max77843_irq_chip` maps system undervoltage/overvoltage/thermal interrupts. `max77843_chg_init()` creates a dummy charger I2C client and regmap. `max77843_probe()` initializes the top regmap, IRQ chip, reads PMIC ID, initializes charger regmap, unmasks interrupt sources, registers children, and enables wakeup. Suspend/resume disables IRQ and toggles wake state.

Control flow: the driver uses `subsys_initcall()` for early I2C driver registration. Probe error handling removes the TOPSYS IRQ chip but does not have a remove callback in this file, so lifecycle details depend on driver-core/module behavior. `suppress_bind_attrs = true` prevents manual sysfs bind/unbind.

State and persistence: `struct max77693_dev` is reused to hold MAX77843 state, including top/charger clients, regmaps, IRQ data, type, and IRQ. Hardware interrupt masks are changed at probe and wake state changes during suspend/resume.

Dependencies and integration points: I2C dummy devices, regmap, regmap-irq, MFD core, MAX77693 common structs, MAX77843 private definitions, child drivers, and OF matching.

Risks: `max77843_chg_init()` creates a dummy I2C device but the probe error path shown here only deletes the top IRQ chip; charger dummy cleanup should be audited. Lack of a visible module exit/remove path after `subsys_initcall()` is also a lifecycle signal. Tests should cover charger dummy creation/regmap failure, PMIC ID read failure, interrupt unmasking, child registration, suspend/resume, and bind/unbind expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max77843.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max8907.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max8907.c

Purpose: this MFD core supports MAX8907 PMICs. It creates general and RTC regmaps, installs charger/on-off/RTC IRQ chips, registers regulator and RTC children, and optionally provides system power-off.

Important APIs, types, and functions: `max8907_cells[]` registers regulator and RTC children. Regmap callbacks mark interrupt/status/time registers volatile or precious and restrict writes. `max8907_chg_irq_chip`, `max8907_on_off_irq_chip`, and `max8907_rtc_irq_chip` model three interrupt blocks sharing the general IRQ. `max8907_power_off()` sets `MAX8907_MASK_POWER_OFF` in `MAX8907_REG_RESET_CNFG`. `max8907_i2c_probe()` checks platform/OF power-controller configuration, initializes general regmap, creates a dummy RTC I2C client and regmap, adds all IRQ chips, registers children, and optionally installs `pm_power_off`. Remove unregisters children, IRQ chips, and RTC dummy client.

Control flow: driver registration occurs at `subsys_initcall()` with explicit module exit. Probe has a structured unwind ladder for regmap, dummy client, IRQ chips, and MFD children. Power-off hook is installed only if requested and no existing global hook is set.

State and persistence: `struct max8907` stores general and RTC I2C clients/regmaps plus IRQ chip data. Static `max8907_pm_off` backs the global power-off hook. Regmap caches use Maple and preserve nonvolatile register state.

Dependencies and integration points: I2C, regmap, regmap-irq, MFD core, OF property `"maxim,system-power-controller"`, platform data `pm_off`, global `pm_power_off`, regulator and RTC child drivers.

Risks: three IRQ chips share a physical IRQ and must be unwound in reverse order. The global power-off pointer is not cleared on remove in this file, so removing a power-controller device could leave stale global state. Tests should cover dummy RTC creation failure, IRQ chip failures at each stage, child registration, power-off property behavior, remove cleanup, and regmap precious/volatile restrictions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max8907.c -->
