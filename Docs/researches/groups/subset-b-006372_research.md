# subset-b-006372 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_i2c.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_i2c.c

## Purpose
This is the I2C bus binding for the Cirrus CS35L41 HD-audio side codec driver. It does not implement amplifier policy itself; it identifies supported ACPI-instantiated devices, builds an I2C regmap, and delegates all real initialization, runtime PM, component binding, firmware, and audio behavior to `cs35l41_hda_probe()` and `cs35l41_hda_remove()` from the shared CS35L41 HDA core.

## Important APIs, types, and functions
The key entry point is `cs35l41_hda_i2c_probe(struct i2c_client *clt)`. It derives a `device_name` by scanning `dev_name(&clt->dev)` for `CLSA0100`, `CLSA0101`, or `CSC3551`, then calls `cs35l41_hda_probe(&clt->dev, device_name, clt->addr, clt->irq, devm_regmap_init_i2c(...), I2C)`. `cs35l41_hda_i2c_remove()` forwards removal to the shared core. The `i2c_device_id`, `acpi_device_id`, and `i2c_driver` tables expose the module to I2C and ACPI matching. The driver imports the `SND_HDA_SCODEC_CS35L41` namespace and uses `cs35l41_hda_pm_ops` for PM callbacks supplied by the core.

## Control flow
Probe performs only HID/name validation and regmap construction. Unsupported names return `-ENODEV` before any regmap or core state is created. Supported devices pass the physical I2C address as the amplifier id and the I2C IRQ into the core. Remove is symmetric and intentionally thin.

## State and persistence
This file owns no persistent state beyond driver registration tables. Per-device state is allocated and attached by the common CS35L41 HDA core. The I2C regmap is device-managed, so its lifetime follows the client device. Firmware, calibration, GPIO, and playback state live outside this file.

## Dependencies and integration points
It depends on the Linux I2C, module, ACPI/mod_devicetable, and regmap infrastructure, plus `cs35l41_hda.h`. It integrates with ACPI names used both by direct ACPI enumeration and serial-multi-instantiate style devices, which is why it checks `dev_name()` rather than only table data.

## Risks and edge cases
The string matching is deliberately narrow. A supported ACPI id presented under an unexpected device name will be rejected. Because `devm_regmap_init_i2c()` is passed directly into the core call, error handling for an `ERR_PTR` regmap must be robust in `cs35l41_hda_probe()`. Device-name matching must remain aligned with ACPI tables and with serial-multi-instantiate naming conventions.

## Test signals
Useful signals are successful binding for `CLSA0100`, `CLSA0101`, and `CSC3551`; rejection of unknown names; a valid regmap visible to the common probe; interrupt handoff to the core; module autoload from ACPI; and clean remove with no device-managed resource leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_property.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_property.c

## Purpose
This file supplies board-specific property overrides for CS35L41 HDA amplifiers on systems whose ACPI `_DSD` data is missing, incomplete, or wrong. It maps ACPI HID and subsystem id combinations to amplifier count, channel placement, boost topology, reset GPIO, speaker-id GPIO, and SPI chip-select handling so the shared CS35L41 HDA core can run on affected laptops.

## Important APIs, types, and functions
`struct cs35l41_config` is the main static board table row: it records subsystem id, number of amps, boost type, channel assignments, GPIO resource indices, and internal boost component values. `cs35l41_config_table[]` contains the large list of known subsystem ids. `struct cs35l41_prop_model` maps HID/SSID pairs to an `add_prop` implementation. The exported API is `cs35l41_add_dsd_properties()`, which selects the first matching model row and calls one of the override helpers.

Key helpers are `cs35l41_add_gpios()`, `generic_dsd_config()`, `hp_i2c_int_2amp_dual_spkid()`, `lenovo_legion_no_acpi()`, and `missing_speaker_id_gpio2()`. `cs35l41_add_gpios()` builds ACPI GPIO mapping arrays for `reset-gpios`, `spk-id-gpios`, and, for limited two-amp SPI cases, `cs-gpios`.

## Control flow
The public call scans `cs35l41_prop_model_table[]` for matching HID and optional SSID. Generic systems then look up `cs35l41_config_table[]`, verify that the driver's ACPI companion matches the physical ACPI device, optionally install GPIO mappings when `_DSD` is absent, derive amp index from SPI chip select or I2C address, fetch reset and speaker-id GPIOs, set speaker position and channel index, and fill `cs35l41_hw_cfg`. Special HP and Lenovo helpers bypass the generic table where the hardware layout needs custom speaker-id or ACPI-less reset handling. `missing_speaker_id_gpio2()` injects a missing speaker-id mapping and then falls back to the normal ACPI parser.

## State and persistence
The file mutates the caller-owned `struct cs35l41_hda`: `index`, `channel_index`, `reset_gpio`, `speaker_id`, `cs_gpio`, and `hw_cfg`. It may also install device-managed ACPI GPIO mappings on the physical ACPI device. No state persists beyond device lifetime, but the static subsystem tables are effectively policy data baked into the driver.

## Dependencies and integration points
It depends on ACPI property APIs, GPIO consumer APIs, SPI chip-select APIs, and CS35L41 core structures. Integration points include `cs35l41_hda_parse_acpi()`, `cs35l41_get_speaker_id()`, `fwnode_gpiod_get_index()`, `devm_acpi_dev_add_driver_gpios()`, `gpiod_get_index()`, `spi_set_csgpiod()`, and `spi_setup()`. It is tightly coupled to real laptop subsystem ids from Dell, HP, Asus, Lenovo, and others.

## Risks and edge cases
The largest risk is table drift: wrong subsystem data can swap left/right channels, select the wrong boost mode, or request wrong GPIO indices. The generic SPI CS workaround only supports two-amp systems and refuses to extend chip selects without `_DSD`. If `_DSD` already exists, reset/speaker-id GPIO mappings cannot be safely added, so the driver warns and may rely on firmware data. Shared GPIO ownership and manual `gpiod_put()` paths must stay balanced.

## Test signals
Test by probing each modeled HID/SSID path, validating amp index and channel placement for two- and four-amp designs, checking internal boost values in `hw_cfg`, confirming speaker-id reads, verifying SPI dual-chip-select behavior, and ensuring unsupported systems return `-ENOENT` so the caller can use ordinary ACPI parsing or fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_property.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_property.h -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_property.h

## Purpose
This header exposes the CS35L41 HDA property-override entry point to the shared CS35L41 HDA driver. It is intentionally small: it gives the common code a way to ask the property table layer to synthesize or correct DSD-style hardware data.

## Important APIs, types, and functions
The only exported declaration is `cs35l41_add_dsd_properties(struct cs35l41_hda *cs35l41, struct device *physdev, int id, const char *hid)`. The header includes `linux/device.h` for `struct device` and `cs35l41_hda.h` for `struct cs35l41_hda`.

## Control flow
There is no executable flow here. Include guards prevent duplicate declarations. Callers include this file, then call the function during CS35L41 HDA ACPI/platform setup when normal firmware properties need augmentation.

## State and persistence
No state is declared or persisted. The function operates on caller-owned device state in the implementation file.

## Dependencies and integration points
It couples the property override module to the CS35L41 HDA core data structure. Any signature change in `struct cs35l41_hda` setup requirements must be reflected here and in callers.

## Risks and edge cases
The main risk is interface mismatch: callers must pass the physical ACPI device, bus id/address/chip-select, and HID consistently with the implementation's matching tables. Because the API returns Linux errno values, callers must distinguish unsupported systems (`-ENOENT`) from hard setup failures.

## Test signals
Build coverage should confirm the declaration matches the implementation. Runtime testing should verify that CS35L41 core code can call the property layer and preserve fallback behavior when no model row matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_property.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_spi.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_spi.c

## Purpose
This file is the SPI bus binding for the CS35L41 HDA side codec. It validates the expected ACPI/device name, creates a SPI regmap, and delegates common amplifier initialization and teardown to the shared CS35L41 HDA core.

## Important APIs, types, and functions
`cs35l41_hda_spi_probe(struct spi_device *spi)` is the probe entry point. It accepts only devices whose name contains `CSC3551`, then calls `cs35l41_hda_probe(&spi->dev, "CSC3551", spi_get_chipselect(spi, 0), spi->irq, devm_regmap_init_spi(...), SPI)`. `cs35l41_hda_spi_remove()` calls the common remove function. `cs35l41_hda_spi_id[]`, `cs35l41_acpi_hda_match[]`, and `cs35l41_spi_driver` provide module matching and registration.

## Control flow
Probe rejects non-`CSC3551` names with `-ENODEV`. Otherwise the SPI chip select becomes the id passed to common code, which lets the core/property layer map bus instance to amp index. Remove has no local cleanup because state is owned by the common core and devm resources.

## State and persistence
The binding owns no durable per-device state. The regmap is devm-managed and the common core owns driver data, GPIO, firmware, PM, and playback state.

## Dependencies and integration points
It depends on Linux SPI, module, ACPI matching, regmap config from the CS35L41 core, and `cs35l41_hda_pm_ops`. It imports `SND_HDA_SCODEC_CS35L41`, integrating this bus module with the shared HDA smart-amp driver.

## Risks and edge cases
Only `CSC3551` is accepted for SPI. If platform naming changes while the ACPI id remains the same, probe will fail early. SPI chip-select mapping is delegated to common code and property overrides, so bus registration must preserve the intended chip-select value. As with I2C, direct passing of a regmap creation result relies on the common probe handling errors.

## Test signals
Probe on a `CSC3551` SPI platform should create a regmap, call the common probe with `SPI`, and bind into the HDA component framework. Unknown SPI devices should return `-ENODEV`. Remove and PM callback paths should be exercised through module unload and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l56_hda.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l56_hda.c

## Purpose
This is the shared HD-audio side-codec implementation for Cirrus CS35L54/56/57 smart amplifiers. Bus-specific I2C and SPI files allocate a `struct cs35l56_hda` and call into this file. The shared code handles ACPI indexing, reset, hardware init, DSP firmware loading, calibration, HDA component binding, playback hooks, ALSA controls, debugfs, runtime PM, and system sleep.

## Important APIs, types, and functions
The exported entry points are `cs35l56_hda_common_probe()`, `cs35l56_hda_remove()`, and `cs35l56_hda_pm_ops`. Internal control is split across playback helpers (`cs35l56_hda_play()`, `cs35l56_hda_pause()`, `cs35l56_hda_playback_hook()`), ALSA control callbacks for posture, user volume, and ASP1 TX source, firmware helpers (`cs35l56_hda_request_firmware_file()`, `cs35l56_hda_request_firmware_files()`, `cs35l56_hda_fw_load()`), calibration (`cs35l56_hda_apply_calibration()` and debugfs wrappers), component callbacks (`cs35l56_hda_bind()` and `cs35l56_hda_unbind()`), and PM callbacks.

`cs35l56_hda_dai_config[]` programs ASP1 for HDA use: I2S, 24-bit samples in 32-cycle slots, Hi-Z DOUT in unused slots, RX/TX disabled initially, and predictable TX input sources.

## Control flow
Common probe initializes locks, stores drvdata, initializes DSP work, reads ACPI to determine amp index/system name/reset GPIO, sets the amp name, initializes the shared `cs35l56_base` and `cs_dsp`, optionally pulses reset, performs hardware init and firmware boot wait, applies the shared patch, disables firmware auto-hibernate, reads calibration, initializes the Halo DSP wrapper, writes DAI registers, enables runtime PM, and registers as a component.

When the HDA codec component master binds, `cs35l56_hda_bind()` stores the codec pointer, fills the component slot, installs the playback hook, queues DSP firmware work, adds ALSA controls, and creates debugfs. The async work requests firmware using a fallback search order from most-specific `base-system-amp` names to generic files, powers down previous DSP state if needed, may shut down ROM firmware, powers up `cs_dsp`, resets and waits for boot when full firmware was downloaded, prevents auto-hibernate, syncs regcache, runs DSP, applies calibration, sends AUDIO_REINIT, and logs tuning.

Playback prepare waits for firmware work, runtime-resumes the device, sends AUDIO_PLAY, waits for PS0, enables ASP RX and the amp-specific TX bit, and marks `playing`. Cleanup sends AUDIO_PAUSE, clears ASP enables, and autosuspends. System suspend pauses playback, marks `suspended`, temporarily disables shared IRQ before noirq, and uses forced runtime suspend; resume reverses reset/IRQ ordering, reloads DSP if needed, and restarts playback if it had been active.

## State and persistence
Persistent device state includes `index`, `num_amps`, `system_name`, `amp_name`, `playing`, `suspended`, `asp_tx_mask`, codec/control pointers, debugfs root, `cs_dsp`, and shared `cs35l56_base` state such as calibration, firmware patch status, reset GPIO, IRQ lock, regmap, and type/revision. Firmware filenames are transient allocations. Calibration data is read into the shared base and can be applied from firmware load or debugfs writes.

## Dependencies and integration points
This file integrates with the HDA component manager, Cirrus shared smart-amp code (`cs35l56_*` helpers), `cs_dsp`, `cs-amp-lib`, firmware loader, runtime PM, regmap, ACPI property APIs, GPIO, debugfs, and ALSA control APIs. It imports firmware and shared Cirrus namespaces and expects bus wrappers to provide a valid regmap and type HID.

## Risks and edge cases
Firmware selection is complex and depends on sanitized system and amp names, preloaded firmware version, security state, and whether BIOS already patched firmware. Missing `.bin` is fatal when firmware is missing from the device. Race control relies on `flush_work()`, `irq_lock`, runtime PM guards, and shared IRQ disable/enable sequencing during suspend. ACPI `cirrus,dev-index` must map the bus id correctly, with a platform fixup for Lenovo Yoga Book 9i pseudo/bad addresses. Control removal assumes controls were created; partial add failures should be watched. Calibration is skipped for secured devices or invalid data.

## Test signals
Strong signals include successful probe on CS35L54/56/57 over both buses, correct amp index from ACPI/fixups, firmware fallback name resolution, async DSP work completion before controls are used, playback prepare/cleanup mbox traffic, PS0 polling, runtime autosuspend, system suspend/resume with shared IRQs, debugfs calibration read/write, ALSA posture/volume/mixer controls, and clean component unbind/remove with DSP power-down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l56_hda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l56_hda.h -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l56_hda.h

## Purpose
This header defines the shared state and public interface for the CS35L56-family HDA smart-amp driver. It is included by the common implementation and by I2C/SPI bus bindings.

## Important APIs, types, and functions
`struct cs35l56_hda` embeds `struct cs35l56_base`, an HDA codec pointer, a DSP work item, amp index/count/name fields, `struct cs_dsp`, playback/suspend flags, ASP TX mask, ALSA control pointers, and optional debugfs root. `cs35l56_hda_from_base()` converts shared base pointers back to the HDA wrapper. The exported declarations are `cs35l56_hda_common_probe()`, `cs35l56_hda_remove()`, and `cs35l56_hda_pm_ops`.

## Control flow
The header has no executable flow, but it defines the object passed from bus probe to common probe. Bus wrappers allocate and initialize `base.dev` and `base.regmap`, then call `cs35l56_hda_common_probe()`. Removal and PM callbacks flow back through the declarations in this header.

## State and persistence
The struct fields represent the lifetime state of one amplifier instance. Some fields are stable identity (`index`, `system_name`, `amp_name`), some are runtime state (`playing`, `suspended`, `asp_tx_mask`), and some link to external framework resources (`codec`, controls, debugfs, `cs_dsp`, base regmap/GPIO/IRQ data).

## Dependencies and integration points
It depends on Linux device/GPIO/regulator/workqueue headers, Cirrus `cs_dsp`, WMFW, and `sound/cs35l56.h`. The `extern` PM ops allow I2C and SPI drivers to share the same suspend/resume implementation.

## Risks and edge cases
Because the bus wrappers and common code share this struct directly, initialization ordering matters: `base.dev` and `base.regmap` must be valid before common probe. Lifetime ownership of `system_name`, controls, debugfs, and DSP resources must remain consistent with remove/unbind paths.

## Test signals
Build tests should cover all configurations using I2C, SPI, debugfs, and PM. Runtime tests should verify `container_of` conversion through calibration/debugfs paths and that bus wrappers call remove/PM functions against a fully initialized object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l56_hda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l56_hda_i2c.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l56_hda_i2c.c

## Purpose
This file is the I2C transport binding for CS35L54/56/57 HDA smart amplifiers. It allocates the shared HDA object, creates the I2C regmap, passes the I2C address and chip HID to common probe, then requests the device IRQ.

## Important APIs, types, and functions
`cs35l56_hda_i2c_probe()` allocates `struct cs35l56_hda`, sets `base.dev`, optionally enables hibernate capability at compile time, initializes `base.regmap` with `cs35l56_regmap_i2c`, calls `cs35l56_hda_common_probe(cs35l56, id->driver_data, clt->addr)`, and then calls `cs35l56_irq_request()`. The id table maps `cs35l54-hda`, `cs35l56-hda`, and `cs35l57-hda` to chip ids `0x3554`, `0x3556`, and `0x3557`. The ACPI table matches `CSC3554`, `CSC3556`, and `CSC3557`.

## Control flow
Probe is linear: allocate, initialize regmap, common probe, IRQ request. If IRQ request fails after common probe succeeded, it calls `cs35l56_hda_remove()` to unwind common state. Remove forwards to common remove. The driver uses `cs35l56_hda_pm_ops` for PM.

## State and persistence
Local state is only the devm allocation and regmap setup. The common object persists as device drvdata after common probe. The I2C address is used as the id for ACPI amp-index matching.

## Dependencies and integration points
It depends on Linux I2C/regmap/module infrastructure and the shared CS35L56 HDA/common Cirrus namespaces. Integration with IRQ handling is via `cs35l56_irq_request()` from the shared CS35L56 support code.

## Risks and edge cases
Failure after common probe must unwind both component and runtime-PM state; this file explicitly does that for IRQ failures. `i2c_client_get_device_id()` must produce a valid id because driver data selects chip type. Address aliases that are not real amps are rejected later by common ACPI parsing.

## Test signals
Probe each supported ACPI id, validate regmap creation, verify I2C address to `cirrus,dev-index` mapping, test IRQ request success/failure unwind, suspend/resume through shared PM ops, and module remove with no leaked component registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l56_hda_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l56_hda_spi.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l56_hda_spi.c

## Purpose
This file is the SPI transport binding for CS35L54/56/57 HDA smart amplifiers. It performs SPI-specific configuration, creates a SPI regmap, and delegates common smart-amp behavior to the shared CS35L56 HDA core.

## Important APIs, types, and functions
`cs35l56_hda_spi_probe()` allocates `struct cs35l56_hda`, sets `base.dev`, calls `cs35l56_init_config_for_spi()`, optionally enables hibernate capability, initializes `base.regmap` with `cs35l56_regmap_spi`, calls `cs35l56_hda_common_probe(cs35l56, id->driver_data, spi_get_chipselect(spi, 0))`, and requests IRQ handling with `cs35l56_irq_request()`. The SPI id table covers `cs35l54-hda`, `cs35l56-hda`, and `cs35l57-hda`; ACPI matches `CSC3554`, `CSC3556`, and `CSC3557`.

## Control flow
The SPI-specific setup runs before common probe so the shared core sees a fully configured control port. If common probe fails, probe returns the error. If IRQ setup fails, common remove is called to unwind. Remove forwards to `cs35l56_hda_remove()`.

## State and persistence
No independent long-lived state exists outside the allocated shared object and devm SPI regmap. The SPI chip select is the amp id consumed by common ACPI parsing.

## Dependencies and integration points
Dependencies include Linux SPI, regmap, module infrastructure, CS35L56 shared SPI configuration helpers, common HDA PM ops, and shared IRQ handling. The module imports both `SND_HDA_SCODEC_CS35L56` and `SND_SOC_CS35L56_SHARED`.

## Risks and edge cases
`cs35l56_init_config_for_spi()` must run successfully before regmap use; misconfigured SPI mode/timing would break all later register traffic. Probe unwind after IRQ failure mirrors the I2C binding and is important because common probe already registered components and runtime PM. Chip-select values must match ACPI `cirrus,dev-index` or platform fixups.

## Test signals
Validate SPI mode/config setup, chip-select to amp-index mapping, regmap register access, IRQ request failure unwind, component binding, shared playback/firmware behavior, and system/runtime PM through the common ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l56_hda_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/hda_component.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/hda_component.c

## Purpose
This file implements the HD-audio side-codec component manager used by HDA codec drivers to bind external amplifier component devices. It centralizes component matching, bind/unbind orchestration, playback hook fanout, and optional ACPI notification fanout.

## Important APIs, types, and functions
Exported APIs are `hda_component_acpi_device_notify()`, `hda_component_manager_bind_acpi_notifications()`, `hda_component_manager_unbind_acpi_notifications()`, `hda_component_manager_playback_hook()`, `hda_component_manager_bind()`, `hda_component_manager_init()`, and `hda_component_manager_free()`. `struct hda_scodec_match` carries bus/HID/match format/index data for component matching. `hda_comp_match_dev_name()` performs relaxed device-name matching by bus prefix, optional bus number, and formatted HID/index suffix.

## Control flow
`hda_component_manager_init()` initializes the parent, creates one match object per expected component, registers match callbacks with the component framework, and adds a component master on the HDA codec device. `hda_component_manager_bind()` clears component slots and calls `component_bind_all()` under the parent mutex. Playback hooks are fanned out in three ordered passes: all pre hooks, then all main hooks, then all post hooks. ACPI notification setup checks whether any component requests notifications and, if so, installs one handler on the first component ACPI device; notification dispatch loops over components and calls their per-device callback.

## State and persistence
State lives in caller-owned `struct hda_component_parent`: a mutex, codec pointer, and fixed array of component slots. Component drivers fill slots during their component bind callbacks. The manager owns no heap state except devm-allocated match data tied to the HDA codec device. `hda_component_manager_free()` removes the component master and clears `parent->codec`.

## Dependencies and integration points
It depends on Linux component framework, ACPI, HDA codec APIs, mutex cleanup guards, and local `hda_component.h`/`hda_local.h`. Side-codec drivers such as CS35L56 and TAS2781 fill `struct hda_component` fields with device pointers, names, playback hooks, and ACPI notification handlers.

## Risks and edge cases
Device-name matching is intentionally relaxed but still string-format dependent; bus naming changes can prevent component bind. ACPI notification install failures are logged as warnings but return success, so callers must tolerate missing notifications. Playback fanout holds the mutex while invoking callbacks, so callbacks should avoid re-entering manager operations or blocking indefinitely. The fixed `HDA_MAX_COMPONENTS` limit requires callers to keep count within array size.

## Test signals
Test component master init/bind/free for 1-4 amps, correct relaxed matching for I2C/SPI names, ordered playback hook calls, ACPI notification install/remove and dispatch, duplicate bind rejection in component drivers, and clean unbind when side-codec devices disappear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/hda_component.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/hda_component.h -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/hda_component.h

## Purpose
This header defines the shared HDA side-codec component binding interface. It is the contract between HDA codec parents and side-codec component drivers.

## Important APIs, types, and functions
`HDA_MAX_COMPONENTS` is 4 and `HDA_MAX_NAME_SIZE` is 50. `struct hda_component` stores a bound side-codec device, printable name, ACPI device, notification support and callback, and three playback hook phases. `struct hda_component_parent` stores the parent mutex, HDA codec pointer, and component array. The header declares manager APIs for ACPI notification binding, playback hook fanout, component manager init/free/bind, and has helpers `hda_component_from_index()` and `hda_component_manager_unbind()`.

## Control flow
Parent drivers initialize a manager with expected component count and match strings, bind all components when ready, call playback hook fanout during HDA PCM actions, and free/unbind the manager during codec teardown. With `CONFIG_ACPI` disabled, ACPI helper functions become no-op inline stubs.

## State and persistence
The parent struct is caller-owned and persists for the HDA codec lifetime. Component slots are filled by side-codec bind callbacks and cleared on unbind. The inline index helper bounds-checks access to the fixed component array.

## Dependencies and integration points
Dependencies include Linux ACPI, component framework, mutexes, and HDA codec types. The header is included by manager implementation and by smart-amp drivers that need to fill component slots or call playback/notification manager APIs.

## Risks and edge cases
Callers must not request more than four components. `hda_component_manager_unbind()` assumes `parent` and `cdc` are valid and takes the mutex around `component_unbind_all()`. ACPI notification stubs mean code must not depend on notification side effects when ACPI is disabled.

## Test signals
Compile with and without `CONFIG_ACPI`, test bounds behavior of `hda_component_from_index()`, verify component slot lifecycle across bind/unbind, and run multi-amp playback hook fanout through a parent HDA codec driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/hda_component.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda.c

## Purpose
This file is the shared HDA support library for Texas Instruments TAS2781-family side-codec drivers. It provides EFI calibration import, common remove behavior, and ALSA control callbacks for profile/program/config selections used by both I2C and SPI transport drivers.

## Important APIs, types, and functions
It exports `tasdev_fct_efi_guid[]`, `tas2781_save_calibration()`, `tas2781_hda_remove()`, and the control callbacks `tasdevice_info_profile()`, `tasdevice_info_programs()`, `tasdevice_info_config()`, `tasdevice_get_profile_id()`, `tasdevice_set_profile_id()`, `tasdevice_program_get()`, `tasdevice_program_put()`, `tasdevice_config_get()`, and `tasdevice_config_put()`. Internal helpers `cali_cnv()` and `tas2781_apply_calib()` validate and convert EFI calibration blobs into the format expected by the TAS firmware library.

## Control flow
`tas2781_save_calibration()` checks EFI runtime support, selects a vendor GUID from the HDA category, probes two possible EFI variable names, allocates a buffer sized for the reported variable or minimum device count, reads calibration data, and calls `tas2781_apply_calib()`. Calibration apply supports older V1 and newer TAS2781 V2/V3 blob layouts, verifies CRC32, optionally extracts register addresses from a special node, converts per-device values to big-endian algorithm format, and sets total data size. Remove unregisters the component, disables runtime PM, and calls `tasdevice_remove()`. Control callbacks expose integer ranges and clamp/set current ids under `codec_lock` for mutable values.

## State and persistence
Calibration data is stored in `tasdevice_priv->cali_data` using device-managed allocation. Current profile/program/config state is stored in `tasdevice_priv` fields (`rcabin.profile_cfg_id`, `cur_prog`, `cur_conf`). EFI variables are persistent platform firmware state, but this driver only reads them.

## Dependencies and integration points
It depends on EFI runtime services, CRC32, Linux firmware/component/PM APIs, ALSA SoC control types, `sound/tas2781.h`, and the TAS2781 firmware library structures. I2C/SPI drivers call these exports when firmware parsing is complete and when HDA controls are created.

## Risks and edge cases
Malformed EFI calibration data disables calibration by setting `total_sz` to zero, allowing DSP defaults to continue. CRC layout assumptions are critical, especially for V2/V3 node counts and register-address nodes. `tas2781_hda_remove()` assumes drvdata and `tas_hda->priv` are valid and that component removal is safe for the supplied ops. Control info callbacks assume firmware/config data has already been parsed.

## Test signals
Test EFI missing/unsupported paths, both EFI variable names, V1 and V2/V3 CRC success/failure, multiple amp counts, category GUID selection for Dell/HP/Lenovo, control clamping/change return values, and remove after successful and partially failed probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda.h -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda.h

## Purpose
This header defines the common TAS2781 HDA wrapper state, custom ALSA control macros, vendor category ids, calibration constants, and shared function declarations used by the TAS2781 I2C and SPI HDA drivers.

## Important APIs, types, and functions
`ACARD_SINGLE_RANGE_EXT_TLV()` builds CARD-interface volume controls backed by `soc_mixer_control` data and TLV arrays. `ACARD_SINGLE_BOOL_EXT()` builds CARD-interface boolean controls. `enum device_catlog_id` selects EFI calibration GUID families. `struct tas2781_hda` links the Linux device, TAS firmware-library private state, three DSP/profile controls, device category, and transport-private HDA state. The header declares calibration, remove, profile/program/config info/get/put callbacks, and `tasdev_fct_efi_guid[]`.

## Control flow
There is no executable logic except macro expansion. Transport drivers allocate `struct tas2781_hda`, set `priv` and `hda_priv`, then use declared callbacks when constructing controls and when loading calibration.

## State and persistence
`struct tas2781_hda` persists for one component device lifetime. It connects framework resources (`struct device`, ALSA controls), firmware library state (`tasdevice_priv`), category selection for EFI variables, and transport-specific private memory.

## Dependencies and integration points
It depends on ALSA core definitions and on TAS firmware library types included indirectly by C files. The macros integrate ALSA CARD-interface controls with SoC helper callbacks despite these being HDA side-codec devices.

## Risks and edge cases
The control macros create compound-literal `soc_mixer_control` private data; users must keep the declarations static or otherwise ensure the private data remains valid as intended by the macro usage. Category ids must match the exported GUID array order. Transport drivers must initialize `hda_priv` to the correct private struct type before using it.

## Test signals
Build I2C and SPI drivers using the macros, inspect ALSA control names/access flags/TLV behavior, verify category-to-GUID selection in calibration, and test remove/control callbacks through both transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda_i2c.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda_i2c.c

## Purpose
This is the I2C HDA side-codec driver for TI TAS2563, TAS2770, TAS2781, and TAS5825 amplifier families. It discovers multi-amp I2C resources from ACPI, initializes the TAS firmware library, binds to the HDA component manager, loads RCA/DSP firmware, creates ALSA controls, handles EFI calibration, and manages runtime/system power.

## Important APIs, types, and functions
`struct tas2781_hda_i2c_priv` stores two generic sound controls, a calibration callback, and a chip id enum. ACPI discovery is handled by `tas2781_get_i2c_res()` and `tas2781_read_acpi()`. Playback and controls are handled by `tas2781_hda_playback_hook()`, amp volume callbacks, force-firmware-load callbacks, chip-specific control templates, and DSP/profile control templates. `tas2563_save_calibration()` handles TAS2563-specific EFI variables. Firmware callbacks are `tasdev_fw_ready()` and `tasdevice_dspfw_init()`. Component callbacks are `tas2781_hda_bind()` and `tas2781_hda_unbind()`. Probe/remove/PM are `tas2781_hda_i2c_probe()`, `tas2781_hda_i2c_remove()`, and the TAS2781 PM callbacks.

## Control flow
Probe allocates the HDA wrapper and private state, creates `tasdevice_priv` with `tasdevice_kzalloc()`, identifies the chip by device name, sets chip id/global address/calibration callback, reads ACPI resources into per-amp addresses, optionally reads ASUS speaker-id GPIO, initializes the TAS device library, enables runtime PM, resets devices, and registers a component. Component bind sets the vendor category from HDA subsystem vendor, runtime-resumes the device, fills the component slot, and calls `tascodec_init()` to request RCA firmware. When RCA firmware arrives, the driver parses it, adds the profile control and chip-specific volume/force controls, and for DSP-capable chips parses DSP firmware, adds program/config controls, loads program 0, applies initial profile blocks, and reads calibration.

Playback open runtime-resumes and switches tuning on under `codec_lock`; close switches tuning off and autosuspends. Runtime suspend powers down unused playback state; runtime resume reloads the current program. System resume resets cached per-device book/program/config state, resets hardware, reloads firmware program and initial profile block, and restores tuning if playback was active.

## State and persistence
State is spread across `tas2781_hda`, `tas2781_hda_i2c_priv`, and `tasdevice_priv`: chip id, global I2C address, discovered device addresses/count, speaker id, firmware names/states, current profile/program/config, playback flag, ALSA control pointers, and calibration data. EFI calibration variables are persistent firmware inputs; driver allocations are device-managed.

## Dependencies and integration points
The file depends on ACPI resources/GPIO, EFI, firmware loading, runtime PM, HDA component APIs, HDA codec subsystem ids, ALSA controls/TLVs, and TAS common I2C/firmware libraries. It integrates with `hda_component` via playback hooks and with shared `tas2781_hda.c` for common calibration/control callbacks.

## Risks and edge cases
Device identification relies on exact `dev_name()` patterns for serial-multi-instantiate variants. ACPI resource enumeration skips the global address and caps channel count. ASUS speaker-id GPIO mapping is conditional on subsystem vendor. Some chips lack DSP or calibration, so control creation paths differ by chip id. Firmware callback paths must tolerate parse failure and release firmware. `tas2781_hda_i2c_probe()` calls shared remove on errors after partial setup, so drvdata and component registration order are important.

## Test signals
Test each ACPI id (`INT8866`, `TIAS2781`, `TXNW2770`, `TXNW2781`, `TXNW5825`), multi-device resource enumeration, ASUS speaker-id firmware naming, RCA and DSP firmware load success/failure, chip-specific controls, TAS2563 and TAS2781 calibration paths, playback open/close tuning switches, runtime autosuspend, system resume reload, and component unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda_spi.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda_spi.c

## Purpose
This is the SPI HDA side-codec driver for HP-style TAS2781 smart amplifiers. It implements the TAS2781 SPI register-access quirks, ACPI amp-index discovery, component binding, RCA/DSP firmware loading, per-amp ALSA controls, EFI calibration, playback hooks, and runtime/system PM.

## Important APIs, types, and functions
SPI-specific regmap setup uses `tasdevice_ranges[]` and `tasdevice_regmap`. Access wrappers `tasdevice_spi_dev_read()`, `tasdevice_spi_dev_bulk_read()`, and `tasdevice_spi_dev_update_bits()` handle the dummy-byte requirement for non-book-zero or high-page reads. `tasdevice_spi_change_chn_book()` restricts operations to the current amp index. `tas2781_spi_reset()`, `tascodec_spi_init()`, and `tasdevice_spi_init()` prepare reset, firmware request, and TAS library callbacks. Volume/control helpers include analog and digital get/put callbacks, force-fwload callbacks, and per-amp control creation functions. Firmware/component flow is handled by `tasdev_fw_ready()`, `tas2781_hda_bind()`, and `tas2781_hda_unbind()`. Probe/remove/PM are `tas2781_hda_spi_probe()`, `tas2781_hda_spi_remove()`, and TAS2781 runtime/system PM callbacks.

## Control flow
Probe allocates the wrapper, SPI-private state, and `tasdevice_priv`, limits SPI speed, creates the SPI regmap, accepts only `TXNW2781`, reads ACPI `ti,dev-index` to map chip select to amp index and optional shared reset GPIO, initializes SPI-specific TAS callbacks, enables runtime PM, and registers as a component. Bind runtime-resumes, fills the component slot, starts asynchronous RCA firmware loading with a name based on device name and amp count, installs the playback hook on success, and marks category as HP. The firmware callback parses RCA, adds profile and volume controls, removes stale DSP data, builds a per-subsystem/per-index coefficient filename, parses DSP firmware, adds program/config controls, resets the amp, loads program 0, initializes current state, and imports calibration.

Playback open resumes and switches tuning on only when firmware state is `TASDEVICE_DSP_FW_ALL_OK`; close switches tuning off and autosuspends. Runtime suspend switches tuning off if active and invalidates cached book/config. System resume force-resumes, reads a reset-detection register, and if the device reset, invalidates cached state, reloads program 0, marks firmware OK, and restores tuning.

## State and persistence
State includes one SPI amp index, per-index cached book/program/config fields, reset GPIO for index 0/shared reset, firmware state, current profile/program/config, ALSA controls, playback flag, and calibration data in `tasdevice_priv`. Unlike I2C, this transport uses a single-device regmap window and explicit dummy-byte handling.

## Dependencies and integration points
Dependencies include Linux SPI/regmap/property/ACPI/runtime PM, HDA component and codec APIs, TAS2781 firmware library, TLV control data, EFI calibration from the shared TAS HDA library, and ALSA control APIs. It imports `SND_SOC_TAS2781_FMWLIB` and `SND_HDA_SCODEC_TAS2781`.

## Risks and edge cases
The dummy-byte read rule is central; missing it corrupts register reads outside early book/page ranges. `tasdevice_spi_dev_update_bits()` writes `TASDEVICE_PAGE_REG(reg)` after reading the full logical register, so register-window mapping assumptions must hold. `tasdevice_spi_change_chn_book()` returns `-EXDEV` for other channels and logs it as an ignored non-error. Control name "Froce Speaker-%d FW Load" contains a typo that may be user visible. Resume reloads firmware only when the clock-config reset value indicates a reset, so reset detection must be reliable.

## Test signals
Test SPI register reads for book 0/page 0-1 and for dummy-byte paths, ACPI `ti,dev-index` mapping for multiple chip selects, shared reset behavior, RCA/DSP firmware naming and load, per-index controls, playback open/close around firmware failure and success, runtime suspend/resume cache invalidation, system resume after hardware reset, and calibration import on HP category devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda_spi.c -->
