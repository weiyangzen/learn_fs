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
