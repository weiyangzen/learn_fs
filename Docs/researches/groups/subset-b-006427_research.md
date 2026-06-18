# Research Group: subset-b-006427

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41-lib.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41-lib.c

Purpose: shared CS35L41 support code used by ASoC and HDA-facing drivers. It centralizes regmap policy, reset/errata setup, OTP trim unpacking, boost configuration, global enable sequencing, DSP memory description, firmware mailbox commands, GPIO configuration, and hibernate entry/exit.

Important APIs and data: `cs35l41_regmap_i2c` and `cs35l41_regmap_spi` export the 32-bit big-endian regmap shape and cache defaults. Register access callbacks classify a large register surface as readable, volatile, or precious, including DSP RAM and OTP windows. `cs35l41_test_key_unlock()` and `cs35l41_test_key_lock()` write the test-key sequences needed for protected registers. `cs35l41_otp_unpack()` reads `CS35L41_OTPID`, selects `otp_map_1` or `otp_map_2`, bulk-reads OTP memory, extracts bitfields across word boundaries, and writes trim fields into live registers. `cs35l41_register_errata_patch()` applies revision-specific A0/B0/B2 patches. `cs35l41_set_channels()`, `cs35l41_init_boost()`, `cs35l41_safe_reset()`, `cs35l41_global_enable()`, `cs35l41_mdsync_up()`, `cs35l41_gpio_config()`, `cs35l41_configure_cs_dsp()`, `cs35l41_set_cspl_mbox_cmd()`, `cs35l41_write_fs_errata()`, `cs35l41_enter_hibernate()`, and `cs35l41_exit_hibernate()` are exported helper entry points.

Control flow: initialization consumers unlock protected registers, apply errata, unpack OTP, lock again, then configure boost and GPIO. Boost setup validates inductor, capacitance, and peak-current ranges before programming coefficient/slope/peak-current registers. Global enable has three paths: internal boost toggles `GLOBAL_EN` and polls PUP/PDN; shared boost stages MDSYNC and completes activation after a PLL-lock IRQ via `cs35l41_mdsync_up()`; external boost walks protected safe-to-active or active-to-safe sequences and may use a DSP mailbox `SPK_OUT_ENABLE` command for newer firmware. Hibernate safe-resets where supported, programs wake source, sends the firmware hibernate mailbox without waiting for ACK, and exit retries `OUT_OF_HIBERNATE` before re-entering low-power state.

State and persistence: persistent state is hardware register state plus regcache policy owned by callers. The file allocates only transient OTP memory. DSP configuration fills a caller-provided `cs_dsp` with memory regions and lock policy. Mailbox functions rely on firmware status state in `DSP_MBOX_2`; hibernate relies on wake and power-management status bits.

Dependencies and integration: depends on Linux regmap, regulator types, firmware WMFW definitions, and public `sound/cs35l41.h`. It is consumed by the CS35L41 codec driver and bus drivers, and its exported symbols can also serve non-ASoC CS35L41 clients.

Risks: protected test-key sequences and magic errata writes are order-sensitive. OTP map extraction can silently mis-trim hardware if IDs or bit offsets drift. `cs35l41_global_enable()` has timeout-sensitive PUP/PDN polling and special cases for older firmware. Shared boost depends on PLL-lock IRQ timing. Some regmap writes ignore return values, so lower-level bus failures can be partially hidden.

Test signals: no in-file tests. Coverage should come from probe on each revision, OTP unpack validation, boost-type matrix testing, suspend/resume hibernate loops, DSP mailbox status injection, and IRQ-driven shared-boost activation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41-lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41-spi.c

Purpose: SPI transport binding for CS35L40/41/51/53-compatible devices using the shared CS35L41 ASoC core.

Important APIs and data: `cs35l41_id_spi` exposes SPI modaliases. `cs35l41_spi_probe()` allocates `struct cs35l41_private`, sets `spi->max_speed_hz` to `CS35L41_SPI_MAX_FREQ`, creates the SPI regmap from `cs35l41_regmap_spi`, stores `dev` and `irq`, and calls `cs35l41_probe()`. `cs35l41_spi_remove()` calls `cs35l41_remove()`. OF compatibles include `cirrus,cs35l40` and `cirrus,cs35l41`; ACPI IDs include `CSC3541` and `CLSA3541`. The driver binds PM through exported `cs35l41_pm_ops`.

Control flow: kernel SPI matching enters probe, allocates device-private state with devres, applies SPI setup, initializes regmap, then delegates all hardware bring-up to the common codec probe. Removal only recovers drvdata and delegates teardown. Module registration uses `module_spi_driver()`.

State and persistence: this file owns no persistent hardware state beyond storing the common private pointer in SPI drvdata. Any platform data returned by `dev_get_platdata()` is passed through as optional `cs35l41_hw_cfg`; otherwise the core parses firmware properties.

Dependencies and integration: depends on SPI, ACPI/OF matching, regmap SPI support, and `cs35l41.h`. It imports the shared regmap config and core probe/remove exported by the library/core files.

Risks: `dev_err_probe(cs35l41->dev, ...)` is used before `cs35l41->dev` is assigned if `devm_regmap_init_spi()` fails, which depends on a null-safe device pointer path and is suspicious compared with using `&spi->dev`. `spi_setup()` failure aborts early, but max-speed forcing can override board settings. The ID table lists multiple related part names while the common probe still validates chip IDs.

Test signals: probe/remove can be tested by SPI modalias or OF/ACPI enumeration, regmap initialization failure injection, and validation that runtime/system PM callbacks from the shared core are wired through the bus driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41.c

Purpose: ALSA SoC component driver for CS35L41 smart amplifiers. It exposes the DAI, controls, DAPM graph, DSP preload/audio events, IRQ recovery, firmware naming, probe/remove, and PM behavior around the shared CS35L41 library.

Important APIs and data: tables map PLL/reference clock values, sample rates, and FS monitor windows. Controls expose digital/analog volume, noise gate parameters, clock-force switches, inversion, zero-crossing, and WM_ADSP preload/firmware controls. DAPM widgets and routes model ASP RX/TX, monitor ADCs, DSP paths, DRE/Class-H, main amplifier, and optional external boost VSPK control. DAI ops are `cs35l41_set_dai_fmt()`, `cs35l41_pcm_hw_params()`, `cs35l41_dai_set_sysclk()`, and `cs35l41_set_channel_map()`. Exported public functions are `cs35l41_probe()` and `cs35l41_remove()`.

Control flow: DAPM DSP preload uses `wm_adsp_early_event()` and `wm_adsp_event()` depending on preload/boot/running state. DSP audio POST_PMU validates firmware mailbox status and sends RESUME; PRE_PMD sends PAUSE. Main amplifier DAPM events write PUP/PDN patches and call `cs35l41_global_enable()`. IRQ handling resumes runtime PM, reads four status/mask registers, releases latched protection errors, temporarily disables/re-enables boost for boost faults, and completes shared-boost activation on PLL lock. Probe parses or copies hardware config, enables VA/VP regulators, handles optional/shared reset GPIO, waits for OTP boot, validates chip ID/revision, unlocks protected access, applies errata and OTP unpack, configures GPIO/IRQ masks, requests IRQ, initializes boost/pdata/system name/DSP, enables runtime PM, and registers the component and DAI.

State and persistence: `struct cs35l41_private` holds DSP state, hardware config, regmap, regulators, IRQ, and reset GPIO. `dsp.system_name` is dynamically allocated from ACPI subsystem ID, HID fallback, or `cirrus,subsystem-id` property and freed on remove. Runtime suspend hibernates DSP only when preloaded and running, sets regcache cache-only, and marks dirty; resume wakes firmware, syncs cache under test-key unlock, exits DSP hibernate, and reinitializes boost.

Dependencies and integration: depends on ASoC, DAPM, regmap, GPIO, regulator, ACPI/device properties, runtime PM, WM_ADSP/HALO, and CS35L41 shared helpers. It integrates with bus wrappers through `cs35l41_probe/remove` and with machine drivers through DAI/component registration.

Risks: hardware sequencing is timing-sensitive around OTP boot, protected register unlock, PUP/PDN polling, and shared boost PLL-lock completion. Some `regmap_update_bits()` calls do not check failures. The probe error path calls `cs35l41_safe_reset()` and powers off even after partial initialization, which is correct but sensitive to valid `hw_cfg.bst_type`. Firmware name derivation can return legacy paths when subsystem ID is absent.

Test signals: no local unit tests. Useful signals are successful ASoC component registration, playback/capture parameter negotiation over supported rates and formats, IRQ recovery logs for protection events, runtime suspend/resume through hibernate, ACPI/DT property parsing for each boost type, and DSP firmware preload/control behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41.h

Purpose: private header joining the CS35L41 bus wrappers with the ASoC core.

Important APIs and types: defines `CS35L41_RX_FORMATS` and `CS35L41_TX_FORMATS` as 16-bit and 24-bit little-endian PCM formats. Declares exported `cs35l41_pm_ops`, `cs35l41_probe()`, and `cs35l41_remove()`. `struct cs35l41_private` embeds `struct wm_adsp dsp` as the first member, keeps a legacy `snd_soc_codec *codec`, hardware config `struct cs35l41_hw_cfg`, `struct device *dev`, `struct regmap *regmap`, two regulator bulk entries, IRQ number, and optional reset GPIO.

Control flow and integration: the header itself has no runtime control flow. It defines the state contract used by `cs35l41.c`, `cs35l41-spi.c`, and any sibling bus bindings. Bus drivers allocate and fill `dev`, `regmap`, `irq`, and optional platform hardware config before calling the core probe.

State and persistence: all persistent driver state hangs from `struct cs35l41_private`. The first-member `wm_adsp` layout is important because WM_ADSP helpers may rely on container-style assumptions or established driver patterns.

Dependencies: includes GPIO consumer, regulator consumer, firmware, ALSA core, public `sound/cs35l41.h`, and local `wm_adsp.h`.

Risks: this header exposes only SPI-visible common APIs in this subset; I2C or HDA users must agree with the same struct layout and PM ops. The `snd_soc_codec *codec` field appears unused in the read files and may be legacy. Adding state here changes all bus allocations.

Test signals: compile coverage is the primary signal. Runtime validation comes from successful bus probe filling mandatory fields before the core touches them, plus PM callbacks resolving through `cs35l41_pm_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l41.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45-i2c.c

Purpose: I2C transport binding for the CS35L45 ASoC codec core.

Important APIs and data: `cs35l45_i2c_probe()` allocates `struct cs35l45_private`, stores it with `i2c_set_clientdata()`, initializes regmap from `cs35l45_i2c_regmap`, fills `dev`, `irq`, `bus_type = CONTROL_BUS_I2C`, and `i2c_addr`, then calls `cs35l45_probe()`. `cs35l45_i2c_remove()` delegates to `cs35l45_remove()`. OF matching uses `cirrus,cs35l45`; I2C ID table contains `cs35l45`; PM is wired through `cs35l45_pm_ops`.

Control flow: driver bind is a thin allocation/regmap/delegate sequence. All power sequencing, DSP setup, IRQ registration, and component registration are handled by the common core after the I2C-specific fields are populated. Removal recovers client data and calls common teardown.

State and persistence: the only transport-specific persistent state is the I2C address and bus type in the common private struct, used later for hibernate wake configuration. Device-managed allocation and regmap lifetime are tied to the I2C device.

Dependencies and integration: depends on Linux I2C, regmap I2C, module infrastructure, and `cs35l45.h`. It imports namespace `SND_SOC_CS35L45` for common symbols and table exports.

Risks: regmap failure is returned directly after logging with `dev_err()`, not `dev_err_probe()`, so deferred-probe context may be less clear. Wake-from-hibernate depends on `i2c_addr` being accurate. The wrapper does not validate `client->irq`; the core simply skips IRQ registration if no IRQ is provided.

Test signals: I2C device enumeration, regmap allocation failure injection, successful wake-source setup in runtime suspend, and probe/remove cycling with and without an IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45-spi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45-spi.c

Purpose: SPI transport binding for CS35L45.

Important APIs and data: `cs35l45_spi_probe()` allocates common private state, forces `spi->max_speed_hz` to `CS35L45_SPI_MAX_FREQ`, calls `spi_setup()`, initializes regmap from `cs35l45_spi_regmap`, fills `dev`, `irq`, and `bus_type = CONTROL_BUS_SPI`, then calls `cs35l45_probe()`. `cs35l45_spi_remove()` calls `cs35l45_remove()`. OF compatible and SPI ID are both `cs35l45`; PM uses `cs35l45_pm_ops`; exported common symbols are imported from `SND_SOC_CS35L45`.

Control flow: the probe path is transport setup followed by common probe delegation. Removal is a direct common remove. Unlike the I2C path, no wake address is set because SPI hibernate wake uses the bus-type flag rather than an address field.

State and persistence: persistent state is the private pointer in SPI drvdata and the common regmap. Device-managed allocation owns the memory and regmap. SPI max-speed is modified on the device before common initialization.

Dependencies and integration: depends on SPI, regmap SPI, OF matching, module registration, and `cs35l45.h`.

Risks: the return value of `spi_setup(spi)` is ignored, so a failed speed/mode setup may allow probe to continue to regmap and core initialization. As with the I2C wrapper, IRQ is optional and unchecked by the wrapper. Forcing max speed can mask board/device-tree configuration mistakes.

Test signals: SPI probe with a failing `spi_setup()` is a useful fault-injection case. Successful register reads through the SPI regmap and runtime hibernate wake behavior distinguish transport correctness from common-core behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45-tables.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45-tables.c

Purpose: CS35L45 register tables and exported utility functions shared by the I2C/SPI wrappers and ASoC core.

Important APIs and data: `cs35l45_patch` is an initialization patch with protected test-key unlock writes, boost/LDPM/clock/test register updates, and error-release defaults. `cs35l45_apply_patch()` registers that patch. `cs35l45_defaults` seeds the regcache with block enables, GPIO defaults, wake/source clock defaults, ASP controls, mixer defaults, DSP stream rates, IRQ masks, and amplifier controls. `cs35l45_i2c_regmap` and `cs35l45_spi_regmap` export 32-bit big-endian regmap configs; SPI adds 16 pad bits. `cs35l45_get_clk_freq_id()` maps supported PLL reference frequencies to hardware configuration IDs.

Control flow: the common core calls `cs35l45_apply_patch()` during device initialization after OTP boot and ID validation. DAI/sysclk logic calls `cs35l45_get_clk_freq_id()` before programming `CS35L45_REFCLK_INPUT`. Regmap callbacks gate cache and register access: readable covers device IDs, power, GPIO, ASP, mixer, IRQ, mailbox, DSP system, and DSP memory regions; volatile covers IDs, reset, status/IRQ/mailbox/DSP scratch and all DSP memory windows.

State and persistence: persistent data is static const table data and exported regmap configurations. Runtime hardware state is not stored here, but cache defaults influence resume and regcache sync behavior.

Dependencies and integration: depends on regmap and `cs35l45.h`; exports symbols in namespace `SND_SOC_CS35L45`. The table module is required by both transport drivers and by `cs35l45.c`.

Risks: register range declarations are broad and must match hardware documentation; an incorrect volatile/readable classification can break regcache resume or block legitimate firmware access. Patch sequencing includes protected magic registers and is sensitive to ordering. PLL frequency support is table-limited; unsupported BCLK/sysclk values fail later DAI setup.

Test signals: compile/link coverage for namespace exports, probe logs showing patch application, regmap cache sync after runtime resume, and DAI parameter tests across every frequency in `cs35l45_pll_refclk_freq`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45-tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45.c

Purpose: ALSA SoC component driver for CS35L45 smart amplifiers. It implements DSP mailbox control, DAPM graph, speaker/receiver mode switching, ASP DAI configuration, PLL setup, runtime hibernate, device-property GPIO configuration, regmap IRQ fanout, DSP initialization, and probe/remove.

Important APIs and data: mailbox helpers validate command/status pairs for PAUSE, RESUME, REINIT, HIBERNATE, and OUT_OF_HIBERNATE. DAPM widgets model DSP preload, DSP audio, global enable, ASP enable, monitor ADCs, ASP RX/TX, DSP RX muxes, DAC mux, AMP enable, and SPK output. Controls include amplifier mode, analog/digital volume, and WM_ADSP controls. DAI ops include format, hw_params, TDM slot, sysclk, and mute-stream HPF tuning. Exported functions are `cs35l45_probe()` and `cs35l45_remove()`; PM ops are exported as `cs35l45_pm_ops`.

Control flow: DSP preload sets `MEM_RDY` before starting WM_ADSP when needed. DSP audio events send RESUME/PAUSE mailbox commands. Global enable writes `CS35L45_GLOBAL_ENABLES` with required delays. Amplifier mode transitions disable AMP and DAPM SPK, reconfigure receiver/speaker bits, boost, HV/LV mode, DRE/gain, control writability, then restore AMP if it was active. ASP hw_params accepts 44.1/48/88.2/96 kHz, programs global FS and word lengths, and computes BCLK if sysclk was not provided. Runtime suspend hibernates WM_ADSP and firmware, masks mailbox IRQ, cache-only marks regmap dirty; resume exits hibernate, syncs regcache, exits DSP hibernate, and toggles global error release.

State and persistence: `struct cs35l45_private` stores DSP, regmap, regulators, reset GPIO, sysclk/TDM slot settings, amplifier mode, IRQ inversion, IRQ data, I2C address, and bus type. Probe enables `vdd-batt` before `vdd-a`, handles optional reset, waits for OTP, applies patch and properties, initializes DSP, enables runtime PM, registers regmap IRQ chips/handlers if IRQ exists, and registers the ASoC component.

Dependencies and integration: depends on ASoC, WM_ADSP/HALO, regmap IRQ, GPIO, regulators, runtime PM, firmware/property APIs, and the table module. I2C/SPI wrappers populate transport-specific fields before calling the common probe.

Risks: multiple sequencing points are hardware-sensitive: supply order, reset delays, OTP boot timeout, patch ordering, mailbox polling, and hibernate wake setup. `cs35l45_dsp_init()` writes FS errata after `wm_halo_init()` but does not check the errata write return. `cs35l45_apply_property_config()` uses `sprintf()` into a fixed 32-byte buffer but current names are bounded. Speaker/receiver mode mutates live DAPM and control permissions and can be fragile under concurrent mixer changes.

Test signals: successful playback/capture DAI negotiation, amplifier mode mixer tests while idle and active, runtime suspend/resume with DSP preloaded, IRQ event injection through regmap IRQs, DT GPIO child-node parsing, HPF tuning on unmute, and probe error unwinding across regulator/reset/DSP/IRQ failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45.h

Purpose: private CS35L45 header containing register addresses, bit definitions, formats/rates, mailbox and IRQ enums, common private state, and declarations shared by the core, table module, and I2C/SPI wrappers.

Important APIs and types: defines the CS35L45 register map from identity/reset through power, GPIO, ASP, mixer, amp, IRQ, mailbox, and DSP memory windows. Bitfield macros cover global/block enables, PLL refclk, sample rate IDs, ASP format/width/slots, GPIO config, IRQ masks, mixer sources, wake sources, and amplifier gain/HPF settings. Enums define CSPL mailbox states/commands, bus type, amplifier mode, regmap IRQ indices, and mailbox event IDs. `struct cs35l45_irq` describes a virtual IRQ handler; `struct cs35l45_private` is the common driver object. Extern declarations publish PM ops, I2C/SPI regmap configs, patch/frequency helpers, and probe/remove.

Control flow and integration: the header has no direct execution but defines the constants that drive every register update in `cs35l45.c` and `cs35l45-tables.c`. The `CS35L45_IRQ()` and `CS35L45_REG_IRQ()` macros generate both logical IRQ handler entries and regmap IRQ descriptors, keeping IRQ mapping compact.

State and persistence: `struct cs35l45_private` persists transport and runtime state: WM_ADSP as first member, device/regmap, reset GPIO, two regulators, initialization/sysclk flags, TDM slot settings, amplifier mode, IRQ polarity/data, I2C address, and bus type.

Dependencies: includes runtime PM, regmap, regulators, DT sound bindings, and local `wm_adsp.h`. Constants are tightly coupled to hardware documentation and the table module’s regcache defaults.

Risks: typos in macro names such as `CS35l45_ASP_FMT_DSP_A` and `CS35l45_HPF_DEFAULT` are internally consistent but easy to misuse in new code. Any register or mask change has wide blast radius across DAI setup, PM, IRQ, and DSP paths. The struct layout requires bus wrappers to set mandatory fields before core probe.

Test signals: compile-time use of all exported macros, regmap IRQ table construction, DAI format/HPF paths using the mixed-case macros, and probe through both I2C and SPI wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-i2c.c

Purpose: I2C binding for ASoC CS35L56 and CS35L63 variants using the shared CS35L56 core.

Important APIs and data: `cs35l56_i2c_probe()` reads match data from I2C/ACPI tables, allocates `struct cs35l56_private`, sets `base.dev` and `base.can_hibernate`, selects `cs35l56_regmap_i2c` for ID `0x3556` or `cs35l63_regmap_i2c` for ID `0x3563`, initializes the I2C regmap, calls `cs35l56_common_probe()`, then `cs35l56_init()`, then requests IRQ through `cs35l56_irq_request()`. `cs35l56_i2c_remove()` delegates to `cs35l56_remove()`. I2C IDs are `cs35l56` and `cs35l63`; ACPI IDs are `CSC355C` and `CSC356C`; PM uses `cs35l56_pm_ops_i2c_spi`.

Control flow: transport probe does identity selection before regmap creation so the core receives the right register layout and `base.type`. On any failure after common probe/init/IRQ, it calls `cs35l56_remove()` to unwind shared resources.

State and persistence: stores all state in the common private struct and its embedded `base`. `base.can_hibernate` enables hibernate-capable PM behavior for I2C/SPI style transports. I2C clientdata persists the private pointer.

Dependencies and integration: depends on I2C, ACPI, regmap, module parameter infrastructure, and local `cs35l56.h`. It imports `SND_SOC_CS35L56_CORE` and `SND_SOC_CS35L56_SHARED` namespaces.

Risks: unsupported match data returns `-ENODEV`. Correct operation depends on ACPI/I2C match data providing the intended part ID; wrong data selects the wrong regmap and type. IRQ request happens only after init; failures there remove the already-initialized core.

Test signals: enumeration for both CS35L56 and CS35L63 IDs, regmap selection checks, IRQ request failure unwind, runtime PM through `cs35l56_pm_ops_i2c_spi`, and hibernate-capable suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-sdw.c

Purpose: SoundWire binding for CS35L56/CS35L57/CS35L63 ASoC devices. It adapts SoundWire register access and lifecycle events to the shared CS35L56 core.

Important APIs and data: custom regmap bus `cs35l56_regmap_bus_sdw` implements read, write, and gather-write with address offset `0x8000`, endian conversion, SoundWire page splitting, and slow OTP-register reads through bridge status/data registers. `cs35l56_sdw_read_prop()` declares playback/capture ports, paging support, quirks, interrupt masks, and optional clock-stop-mode1 support. `cs35l56_sdw_ops` wires property, interrupt, status, and clock-stop callbacks. Probe selects `cs35l56_regmap_sdw` or `cs35l63_regmap_sdw`, starts regcache cache-only until enumeration, calls `cs35l56_common_probe()`, and defers full init until attach.

Control flow: SoundWire attach status triggers `cs35l56_sdw_init()` if not initialized or soft-resetting. That gets the unique ID, uses it as calibration index if none was set, runs `cs35l56_init()`, and enables SoundWire codec IRQs when init is complete. Interrupt callback masks and clears implementation-defined interrupts, holds runtime PM, and queues `cs35l56_sdw_irq_work()`, which calls the shared `cs35l56_irq()` and unmasks unless removal/suspend asked not to. Runtime resume handles clock-stop/unattach completion before shared resume and interrupt re-enable. System suspend disables and flushes SoundWire IRQ work before delegating shared suspend.

State and persistence: private state includes SoundWire peripheral pointer, link/unique IDs, attach flags, clock-stop-mode1 flag, IRQ work item, and unmask suppression flag. Regcache starts cache-only because registers are unavailable until SoundWire enumeration completes.

Dependencies and integration: depends on SoundWire core APIs, regmap, PM runtime, workqueues, endian helpers, and shared CS35L56 core/shared namespaces. It integrates with SoundWire manager lifecycle rather than a fixed platform IRQ.

Risks: endian and page-boundary handling are central; mistakes corrupt firmware controls or register values. Slow OTP reads poll bridge status and can timeout. PM reference balancing around queued IRQ work is delicate; canceling instead of flushing could leak a runtime PM get, which the code comments explicitly avoid in suspend. Register access is impossible during clock-stop/unattach, so resume must wait for `initialization_complete`.

Test signals: SoundWire enumeration attach/unattach, clock-stop-mode1 suspend/resume, OTP slow-read paths, multi-page regmap reads/writes, queued interrupt handling and PM balance, and device IDs for CS35L56/57/63.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-shared-test.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-shared-test.c

Purpose: KUnit coverage for CS35L56 shared speaker-ID and GPIO/pad helper logic across CS35L56 and CS35L63 variants and regmap transports.

Important APIs and data: test-private structures model a faux amplifier device, faux GPIO provider, mock register cache, shared `cs35l56_base`, and applied pad pull latch state. A mock GPIO chip implements input direction and `get()` from a bitmask. Custom regmap buses intercept reads/writes for GPIO/pad/update registers, synthesize `GPIO_STATUS1`, and fail unexpected register accesses. Tests exercise `cs35l56_configure_onchip_spkid_pads()`, `cs35l56_read_onchip_spkid()`, `cs35l56_check_and_save_onchip_spkid_gpios()`, and `cs35l56_get_speaker_id()`.

Control flow: suite init creates faux devices and regmaps for a specific part/revision/transport config. The mock `UPDATE_REGS` write simulates applying pad pull states into always-on latches. Parametrized cases verify GPIO status self-test behavior, speaker-ID bit assembly from on-chip GPIOs, pad input/pull configuration, property validation/rejection, absence behavior, vendor speaker ID stub override, direct `cirrus,speaker-id` property, and host GPIO `spk-id-gpios` software-node lookup. Seven KUnit suites reuse the same cases for L56 B0/B2 over SDW/SPI/I2C and L63 A1 over SDW.

State and persistence: all state is per-test and cleaned by KUnit actions: faux devices are destroyed, regmaps exited, and software nodes removed. Static stubbing hooks `cs_amp_get_vendor_spkid()` for the vendor-ID path.

Dependencies and integration: depends on KUnit, KUnit static stubs, faux devices, gpiolib, regmap, software nodes, seq_buf parameter descriptions, and public/shared CS35L56 and CS amp-library APIs. It imports `SND_SOC_CS35L56_SHARED` and `SND_SOC_CS_AMP_LIB`.

Risks: mock behavior intentionally allows only a narrow register set; new shared-helper register accesses will fail tests until the mock is updated. Host GPIO tests are skipped without reachable `CONFIG_GPIOLIB`. The suites validate logic but not real bus timing, IRQ, or PM behavior.

Test signals: this file is itself the test signal. Passing suites demonstrate stable speaker-ID handling across transport regmap configs, part variants, GPIO bit ordering, pull programming, invalid property rejection, vendor override precedence, software-node property path, and direct `cirrus,speaker-id` property path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l56-shared-test.c -->
