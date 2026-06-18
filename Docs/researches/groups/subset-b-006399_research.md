# Research: subset-b-006399

Grouped research for ALSA PCI and Envy24HT board-support sources under `sources/distributed-fs/ceph-client/sound/pci`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/revo.c -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/revo.c

## Purpose
`revo.c` is the Envy24HT low-level board driver for M-Audio Revolution 7.1, Revolution 5.1, and Audiophile 192 cards. It binds those subvendor IDs to `snd_ice1712_card_info` entries, initializes the attached AKM DAC/ADC converters, configures a PT2258 volume controller on Revolution 5.1, and exposes AK4114 S/PDIF receiver controls for Audiophile 192.

## Important APIs, Types, and Functions
- `struct revo51_spec` stores card-private side devices: the GPIO bit-banged I2C device, `snd_pt2258`, and `ak4114`.
- `revo_i2s_mclk_changed()` pulses converter reset through the AC97 command register when the master clock changes.
- `revo_set_rate_val()` maps sample rate to AKM DFS mode and resets/writes AKM codec registers through `snd_akm4xxx`.
- `revo51_i2c_init()` creates a software I2C bus over GPIO6/GPIO7 and binds a PT2258 at address `0x40`.
- `ap192_ak4114_read()` and `ap192_ak4114_write()` implement the AK4114 4-wire GPIO protocol.
- `revo_init()` is the board initialization hook; `revo_add_controls()` is the control-building hook.
- `snd_vt1724_revo_cards[]` is the exported entry table consumed by the generic ICE1724 driver.

## Control Flow
The generic ICE1724 probe selects an entry from `snd_vt1724_revo_cards[]`, calls `revo_init()`, then later calls `revo_add_controls()`. Initialization switches on `ice->eeprom.subvendor`, assigns DAC/ADC counts, allocates `ice->akm`, initializes one or two AKM codecs with board-specific serial GPIO masks, initializes PT2258 I2C for Revolution 5.1 or AK4114 for Audiophile 192, then sets `VT1724_REVO_MUTE` to unmute. Runtime sample-rate changes reach `revo_set_rate_val()` through AKM ops and, for Audiophile 192, `ap192_set_rate_val()` also adjusts ADC DFS GPIO pins and resets the ADC.

## State and Persistence
State is runtime-only. `ice->spec` owns allocated helper state, `ice->akm` owns AKM codec instances, and AKM/PT2258/AK4114 subsystems keep their own control caches. The file writes hardware registers and GPIO lines directly; no persistent configuration is stored outside ALSA control state and the live device registers.

## Dependencies and Integration Points
The file depends on the ALSA ICE1712/Envy24HT core, `snd_akm4xxx`, ALSA I2C bit ops, PT2258 support, and AK4114 support. It integrates through `struct snd_ice1712_card_info` callbacks and uses shared GPIO helpers such as `snd_ice1712_save_gpio_status()`, `snd_ice1712_gpio_write_bits()`, and `snd_ice1712_akm4xxx_build_controls()`.

## Risks and Test Signals
Risks include incorrect GPIO masks shared by AKM and AK4114, leaked `ice->spec` allocation on partial init failures, and silent S/PDIF-rate limitations because AK4114 check flags suppress rate validation. Test signals are successful card probe for all three subvendors, visible AKM/PT2258/AK4114 mixer controls, clean rate switching across 44.1/48/96/192 kHz, and no pops or stuck mute after `i2s_mclk_changed`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/revo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/revo.h -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/revo.h

## Purpose
`revo.h` declares the public board-support interface and GPIO layout for the M-Audio Revolution/Audiophile 192 Envy24HT driver.

## Important APIs, Types, and Functions
- `REVO_DEVICE_DESC` contributes user-visible card descriptions to the ICE1724 card table.
- `VT1724_SUBDEVICE_REVOLUTION71`, `VT1724_SUBDEVICE_REVOLUTION51`, and `VT1724_SUBDEVICE_AUDIOPHILE192` identify the supported PCI subsystem IDs.
- `extern struct snd_ice1712_card_info snd_vt1724_revo_cards[]` exports the board table implemented in `revo.c`.
- `VT1724_REVO_CCLK`, `CDIN`, `CDOUT`, `CS0..CS3`, `I2C_DATA`, `I2C_CLOCK`, and `MUTE` define board-specific GPIO bit assignments.

## Control Flow
This header has no executable flow. It is included by the generic ICE1724 card registry and by `revo.c`; constants steer subdevice matching and GPIO operations.

## State and Persistence
No state is stored. The constants describe hardware wiring and must remain synchronized with `revo.c` serial/I2C transactions.

## Dependencies and Integration Points
The declarations depend on `struct snd_ice1712_card_info` from the ICE1712 core. GPIO aliases intentionally overlap for different board models, so call sites must choose the correct interpretation by subvendor.

## Risks and Test Signals
Risks are mainly wrong bit definitions or subdevice IDs, which would cause missing detection, wrong chip-selects, or stuck mute. Test signals are successful matching of all three board models and verified GPIO traffic during codec initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/revo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/se.c -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/se.c

## Purpose
`se.c` provides Envy24HT board support for ONKYO WAVIO SE-90PCI and SE-200PCI cards. SE-90PCI is mostly static hardware setup, while SE-200PCI initializes WM8740, WM8766, and WM8776 devices and creates custom ALSA mixer controls for playback, capture, input selection, AGC, and AFL bypass.

## Important APIs, Types, and Functions
- `struct se_spec` caches per-control stereo values in `vol[8]`.
- `se200pci_WM8766_write()` bit-bangs a 16-bit control word over GPIO16/17/18 and wraps GPIO save/restore.
- `se200pci_WM8776_write()` sends WM8776 register/data words over the Envy24HT I2C helper to address `0x34`.
- `se200pci_set_pro_rate()` dispatches rate changes to the attached codecs; only WM8766 changes MCLK ratio.
- `struct se200pci_control` and `se200pci_cont[]` describe custom ALSA controls and their target hardware.
- `se200pci_cont_*_{info,get,put}` implement ALSA mixer callbacks and update hardware on changed values.
- `se_init()` and `se_add_controls()` are the exported board callbacks through `snd_vt1724_se_cards[]`.

## Control Flow
Probe calls `se_init()`, which allocates `se_spec`, distinguishes SE-90PCI from SE-200PCI, sets DAC/ADC counts, and initializes codecs. For SE-200PCI, WM8766 is reset and configured for I2S 24-bit, WM8776 receives a manual default-register load and initial selector/AGC/volume state, and `ice->gpio.set_pro_rate` is assigned. Control registration loops over `se200pci_cont[]`, creates `snd_kcontrol` descriptors, and wires each put callback to `se200pci_cont_update()`.

## State and Persistence
Mixer values are cached only in `ice->spec->vol`; hardware register state is programmed immediately on mixer updates. EEPROM images in `se200pci_eeprom` and `se90pci_eeprom` are static fallback configuration data used by the core. There is no nonvolatile persistence or resume cache in this file.

## Dependencies and Integration Points
The file depends on ICE1712/Envy24HT GPIO and I2C helpers, ALSA control/TLV APIs, and board IDs from `se.h`. It integrates by providing `snd_vt1724_se_cards[]` and by setting `ice->gpio.set_pro_rate` for the core rate-change path.

## Risks and Test Signals
Risks include hand-coded WM8766/WM8776 register values diverging from hardware expectations, missing rollback on partial initialization errors, and `change` reporting in some multi-channel puts reflecting only the last lane. Test signals include ALSA mixer control enumeration, valid TLV scales, correct default mute/volume behavior, audible output on all SE-200PCI channel groups, capture selector switching, and MCLK changes above 96 kHz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/se.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/se.h -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/se.h

## Purpose
`se.h` declares the ONKYO SE board descriptors, supported subdevice IDs, and the exported card-info table for `se.c`.

## Important APIs, Types, and Functions
- `SE_DEVICE_DESC` lists SE-90PCI and SE-200PCI names for the enclosing card registry.
- `VT1724_SUBDEVICE_SE90PCI` and `VT1724_SUBDEVICE_SE200PCI` are the subvendor match IDs.
- `extern struct snd_ice1712_card_info snd_vt1724_se_cards[]` exposes the table implemented by `se.c`.

## Control Flow
No executable control flow is present. The ICE1724 registry includes this header to discover the board table; `se.c` uses the IDs to branch during initialization.

## State and Persistence
The header stores no state. Its constants define the stable hardware identity contract for the ONKYO board driver.

## Dependencies and Integration Points
It depends on the ICE1712 card-info type being visible to consumers and integrates with the generic Envy24HT card registry.

## Risks and Test Signals
Incorrect IDs or descriptions would prevent automatic board matching or expose the wrong model string. Test signals are module alias matching and correct `card->shortname`/model after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/se.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/stac946x.h -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/stac946x.h

## Purpose
`stac946x.h` defines register addresses for STAC9460/STAC946x codecs used by the Waveterminal 192M board code.

## Important APIs, Types, and Functions
The header exports register constants for reset/status, master and per-channel DAC volumes, mic/ADC volumes, de-emphasis, general purpose, audio port control, master clocking, powerdown, revision, and address-control registers.

## Control Flow
No executable control flow is present. `wtm.c` uses these constants to read/write STAC9460 codecs over I2C.

## State and Persistence
No runtime state is stored. The constants encode the register map assumed by `wtm.c`.

## Dependencies and Integration Points
The header is standalone and consumed by the Envy24HT WTM board driver. It indirectly couples to `snd_vt1724_read_i2c()` and `snd_vt1724_write_i2c()` call sites through register numbering.

## Risks and Test Signals
Risks are wrong or incomplete register definitions causing mixer controls to touch the wrong STAC registers. Test signals are correct WTM mixer behavior for DAC mute/volume, ADC gain/mute, MIC/Line switching, and master clock changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/stac946x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/vt1720_mobo.c -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/vt1720_mobo.c

## Purpose
`vt1720_mobo.c` supplies minimal VT1720/Envy24PT motherboard support for Albatron, Chaintech, and Shuttle boards. It mainly provides EEPROM defaults and a shared initialization callback for VT1616 AC-link based onboard audio.

## Important APIs, Types, and Functions
- `k8x800_init()` marks the device as VT1720, sets six DACs and two ADCs, and leaves a WM8728 TODO.
- `k8x800_add_controls()` is a placeholder for future VT1616 quirks.
- `k8x800_eeprom[]` and `sn25p_eeprom[]` provide static EEPROM configuration images.
- `snd_vt1720_mobo_cards[]` maps five supported subdevices to names, models, callbacks, and EEPROM data.

## Control Flow
The generic ICE1724 probe selects a matching table entry, loads the EEPROM image, calls `k8x800_init()`, and later calls `k8x800_add_controls()`. All listed boards share the same initialization path; SN25P gets a variant EEPROM with S/PDIF bits.

## State and Persistence
The only state change is runtime initialization of `ice->vt1720`, `num_total_dacs`, and `num_total_adcs`. EEPROM arrays are static data consumed by the core; there is no dynamic board-private allocation.

## Dependencies and Integration Points
The file depends on ICE1712/Envy24HT core types and constants. It integrates by exporting `snd_vt1720_mobo_cards[]`.

## Risks and Test Signals
The main risk is incomplete hardware support: control quirks and WM8728 support are marked TODO, so board-specific mixer behavior may be missing. The SN25P table entry uses `sizeof(k8x800_eeprom)` with `sn25p_eeprom` data, which is currently the same size but is a maintenance trap. Test signals include successful probe, AC97/AC-link codec availability, channel count reporting, and no regression in EEPROM-derived GPIO setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/vt1720_mobo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/vt1720_mobo.h -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/vt1720_mobo.h

## Purpose
`vt1720_mobo.h` declares motherboard-specific VT1720 descriptions, subdevice IDs, and the exported card-info table.

## Important APIs, Types, and Functions
- `VT1720_MOBO_DEVICE_DESC` aggregates Albatron, Chaintech, and Shuttle model descriptions.
- `VT1720_SUBDEVICE_*` constants identify K8X800, ZNF3-150, ZNF3-250, 9CJS, and SN25P boards.
- `extern struct snd_ice1712_card_info snd_vt1720_mobo_cards[]` exposes the table implemented in `vt1720_mobo.c`.

## Control Flow
The header has no executable flow. It participates in compile-time registration and subvendor-based dispatch in `vt1720_mobo.c`.

## State and Persistence
No state is stored. Constants preserve the hardware matching contract.

## Dependencies and Integration Points
Consumers must include ICE1712 card-info declarations before using the extern table. The IDs integrate with PCI subsystem matching performed by the Envy24HT core.

## Risks and Test Signals
Incorrect IDs lead to unsupported board probes or wrong EEPROM defaults. Test signals are correct matching and model names for all five motherboards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/vt1720_mobo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/wm8766.c -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/wm8766.c

## Purpose
`wm8766.c` is a reusable ALSA helper for Wolfson WM8766 DACs on VT17xx cards. It initializes the codec, caches writable 9-bit registers, restores state on resume, exposes common mixer controls, and delegates physical writes to a board-supplied callback.

## Important APIs, Types, and Functions
- `snd_wm8766_write()` updates `wm->regs[]` for cacheable registers and calls `wm->ops.write()`.
- `snd_wm8766_default_ctl[]` describes default channel volume, mute, phase, de-emphasis, IZD, and zero-cross controls.
- `snd_wm8766_init()` copies default control descriptors, resets the chip, and writes default register values.
- `snd_wm8766_resume()` replays cached registers.
- `snd_wm8766_set_if()` updates interface-format bits while preserving unrelated `IFCTRL` bits.
- `snd_wm8766_volume_restore()` forces the volume update bit after MCLK stoppage.
- `snd_wm8766_build_controls()` registers active controls with ALSA.

## Control Flow
Board code fills `struct snd_wm8766` with card and write callback, then calls `snd_wm8766_init()` and `snd_wm8766_build_controls()`. ALSA control callbacks read values from `wm->regs[]`, apply stereo/invert/update-bit transformations, and write changed register fields back through `snd_wm8766_write()`.

## State and Persistence
State is kept in `wm->regs[]`, `wm->ctl[]`, and optional `wm->agc_mode` even though WM8766 does not use AGC controls here. The cache is runtime-only but is the authoritative source for mixer get callbacks and resume replay.

## Dependencies and Integration Points
The file depends on ALSA control/TLV APIs, `__ffs()`, and definitions in `wm8766.h`. It integrates with board drivers through `struct snd_wm8766_ops.write`, avoiding board-specific bus logic inside the helper.

## Risks and Test Signals
Risks include missing input-range validation in put callbacks, incorrect `__ffs()` use if a mask is zero, and always returning `0` from put callbacks rather than reporting whether a value changed. Test signals are successful control creation, correct stereo volume update-bit behavior, resume restoring all cached registers, and board-level verification of the write callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/wm8766.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/wm8766.h -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/wm8766.h

## Purpose
`wm8766.h` defines the WM8766 register map, bit fields, ALSA control descriptor structures, runtime codec state, and exported helper API.

## Important APIs, Types, and Functions
- Register and bit macros cover DAC volumes, interface format, phase inversion, mute/de-emphasis, power, master clock, and reset.
- `struct snd_wm8766_ops` provides the board-specific `write()` callback.
- `enum snd_wm8766_ctl_id` indexes the default control table.
- `struct snd_wm8766_ctl` describes one ALSA control and optional custom get/set functions.
- `struct snd_wm8766` stores the card pointer, controls, write ops, and cacheable registers.
- Exported helpers are `snd_wm8766_init()`, `snd_wm8766_resume()`, `snd_wm8766_set_if()`, `snd_wm8766_volume_restore()`, and `snd_wm8766_build_controls()`.

## Control Flow
This header has no executable flow, but its structures define the call contract: board drivers initialize a `snd_wm8766`, provide `ops.write`, and call the implementation helpers.

## State and Persistence
`struct snd_wm8766` stores runtime codec state. `regs[WM8766_REG_COUNT]` caches 9-bit registers, excluding the reset register by design.

## Dependencies and Integration Points
The header depends on ALSA card/control types and Linux integer types supplied by including C files. It integrates reusable codec logic with board-specific serial or I2C transports.

## Risks and Test Signals
Risks include structure/API drift between board users and `wm8766.c`, and masks that include update bits requiring careful get/put handling. Test signals are compile coverage, correct control count, and successful resume replay on boards using the helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/wm8766.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/wm8776.c -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/wm8776.c

## Purpose
`wm8776.c` is the reusable ALSA helper for Wolfson WM8776 codec chips. It manages cached register writes, playback/capture mixer controls, headphone and ADC paths, and dynamic activation of limiter/ALC controls based on AGC mode.

## Important APIs, Types, and Functions
- `snd_wm8776_write()` converts a 7-bit register plus 9-bit data into the two-byte WM8776 bus format and updates the cache.
- `snd_wm8776_activate_ctl()` toggles ALSA control inactive state and notifies userspace.
- `snd_wm8776_set_agc()`, `snd_wm8776_get_agc()`, and `snd_wm8776_update_agc_ctl()` manage limiter/ALC mode and related control visibility.
- `snd_wm8776_default_ctl[]` defines master DAC, headphone, AUX/bypass, ADC, input switches, AGC, limiter, ALC, and noise-gate controls.
- `snd_wm8776_init()`, `snd_wm8776_resume()`, `snd_wm8776_set_power()`, `snd_wm8776_volume_restore()`, and `snd_wm8776_build_controls()` are the exported helper API.

## Control Flow
Board drivers instantiate `struct snd_wm8776`, provide `ops.write`, call init, optionally customize control descriptors, and build controls. Mixer get callbacks read from the cache or custom getters. Put callbacks transform user values for inversion/stereo/update-bit semantics, call custom setters when present, or patch register fields directly. AGC selection writes ALC registers and updates ALSA control active/inactive flags.

## State and Persistence
Runtime state lives in `wm->regs[]`, `wm->ctl[]`, and `wm->agc_mode`. The register cache is used for mixer reads and resume; reset register writes are not cached. No nonvolatile persistence exists.

## Dependencies and Integration Points
The helper depends on ALSA control/TLV APIs and `wm8776.h`. Board integration is intentionally narrow: only `struct snd_wm8776_ops.write` knows how bytes reach the codec. Control activity updates integrate with ALSA mixer notification through `snd_ctl_notify()`.

## Risks and Test Signals
Risks include incorrect inactive-control state if AGC mode and control names diverge, no put-change reporting, incomplete bounds checking for enum/integer values, and cache/hardware divergence on failed bus writes. Test signals include limiter/ALC controls becoming active only in the right modes, correct TLV exposure, resume replay, powerdown control behavior, and verified two-byte bus payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/wm8776.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/wm8776.h -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/wm8776.h

## Purpose
`wm8776.h` defines the WM8776 register map, control IDs, AGC modes, runtime state structures, and exported helper functions used by `wm8776.c` and board drivers.

## Important APIs, Types, and Functions
- Register macros cover headphone, DAC, phase, mute, serial format, master clock, powerdown, ADC volume, ALC, noise gate, limiter, ADC mux, output mux, and reset.
- `struct snd_wm8776_ops` exposes the board-specific two-byte write callback.
- `enum snd_wm8776_ctl_id` indexes all default mixer controls.
- `struct snd_wm8776_ctl` describes ALSA control metadata and optional custom set/get callbacks.
- `enum snd_wm8776_agc_mode` tracks Off, Limiter, and ALC channel modes.
- `struct snd_wm8776` stores card, control table, AGC mode, ops, and cached registers.

## Control Flow
The header defines the data contract but has no executable flow. Board code uses it to allocate and initialize codec state before calling the implementation helpers.

## State and Persistence
Runtime state is represented by `struct snd_wm8776`; cached registers intentionally exclude the reset register with `WM8776_REG_COUNT`.

## Dependencies and Integration Points
The header depends on ALSA card/control and fixed-width integer types. It integrates generic WM8776 mixer logic with board-specific I2C or serial write paths.

## Risks and Test Signals
Risks are macro mistakes in densely packed bit fields, enum/control count drift, and mismatch between update-bit masks and control conversion logic. Test signals include compile-time users of every exported helper, complete control registration, and successful register replay after suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/wm8776.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/wtm.c -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/wtm.c

## Purpose
`wtm.c` supports the ESI/Ego Sys Waveterminal 192M Envy24HT card. It controls two STAC9460-family codecs over I2C, provides ALSA mixer controls for eight DAC outputs and four ADC inputs, and coordinates muting around sample-rate master-clock changes.

## Important APIs, Types, and Functions
- `struct wtm_spec` stores `mute_mutex`, used to serialize rate-change muting with user mixer mute operations.
- `stac9460_{put,get}()` and `stac9460_2_{put,get}()` access the two codec I2C addresses.
- `stac9460_dac_mute_all()` mutes/unmutes master and per-channel DACs with a change mask to restore only affected channels.
- `stac9460_*_{info,get,put}` functions implement DAC mute/volume, ADC mute/gain, and MIC/Line enum controls.
- `stac9460_set_rate_val()` selects STAC master clock mode for base, mid, and high sample-rate ranges while muting around the transition.
- `wtm_init()` initializes card counts, `force_rdma1`, codec defaults, and rate-change callback.
- `wtm_add_controls()` registers the `stac9640_controls[]` table.

## Control Flow
Probe calls `wtm_init()`, which allocates `wtm_spec`, initializes the mutex, writes reset/master clock defaults to both STAC codecs, and installs `ice->gpio.set_pro_rate`. Control registration iterates the static control array. Mixer put callbacks read the current register, compute inverted user-facing volume/mute values, and write the appropriate codec depending on control index.

## State and Persistence
Hardware state is mostly read back from STAC registers instead of mirrored in a full software cache. `wtm_spec` only persists the mutex for runtime synchronization. `wtm_eeprom[]` is static configuration data for the ICE1724 core. There is no nonvolatile state.

## Dependencies and Integration Points
The file depends on Envy24HT I2C helpers, STAC register constants from `stac946x.h`, ALSA mixer/TLV APIs, and card IDs from `wtm.h`. It integrates via `snd_vt1724_wtm_cards[]` and the `set_pro_rate` callback.

## Risks and Test Signals
Risks include subtle bugs in change-mask handling for the second codec, missing accumulation of `change` in some ADC loops, direct hardware reads in get paths failing if I2C access is unreliable, and concurrency around master mute vs. individual mute. Test signals are stable control reads/writes for all eight DACs and two ADC pairs, correct MIC/Line switching on both codecs, no audible artifacts during rate changes, and valid operation at 48/96/192 kHz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/wtm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/wtm.h -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/wtm.h

## Purpose
`wtm.h` declares the Waveterminal 192M board descriptor, subdevice ID, codec I2C addresses, and exported card-info table.

## Important APIs, Types, and Functions
- `WTM_DEVICE_DESC` contributes the user-visible Waveterminal description.
- `VT1724_SUBDEVICE_WTM` is the Waveterminal 192M subsystem ID.
- `AK4114_ADDR`, `STAC9460_I2C_ADDR`, and `STAC9460_2_I2C_ADDR` define external chip addresses.
- `extern struct snd_ice1712_card_info snd_vt1724_wtm_cards[]` exposes the table implemented by `wtm.c`.

## Control Flow
There is no executable flow. The constants are consumed by `wtm.c` and the generic ICE1724 registry.

## State and Persistence
No state is stored. The header is hardware-identity and bus-address metadata.

## Dependencies and Integration Points
It depends on the ICE1712 card-info type at the use site. The I2C addresses integrate directly with Envy24HT I2C helper calls in `wtm.c`.

## Risks and Test Signals
Wrong addresses or subdevice IDs would make codec access or card matching fail. Test signals are I2C ACKs from both STAC codec addresses and correct card registration as Waveterminal 192M.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/wtm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/intel8x0.c -->
# sources/distributed-fs/ceph-client/sound/pci/intel8x0.c

## Purpose
`intel8x0.c` is the ALSA PCI driver for Intel ICH-family AC'97 audio controllers plus compatible SiS7012, NVIDIA nForce, AMD, and ALi M5455 variants. It handles PCI probe, controller reset, AC'97 codec discovery, PCM stream creation, busmaster descriptor-ring DMA, interrupt handling, mixer quirks, S/PDIF routing, AC97 clock measurement, proc diagnostics, and suspend/resume.

## Important APIs, Types, and Functions
- `struct ichdev` represents one busmaster stream: register offset, BDL address, PCM substream, buffer geometry, ring indices, interrupt bit, AC97 PCM mapping, and suspend/prepared flags.
- `struct intel8x0` is the card-private state: PCI/card pointers, MMIO regions, stream array, AC97 bus/codecs, capability flags, IRQ, descriptor pages, lock, and register masks.
- Codec access is implemented by `snd_intel8x0_codec_{semaphore,read,write}()` for ICH/SIS/NVIDIA and `snd_intel8x0_ali_codec_{read,write}` for ALi.
- DMA setup and IRQ progression are handled by `snd_intel8x0_setup_periods()`, `snd_intel8x0_update()`, and `snd_intel8x0_interrupt()`.
- PCM operations include `hw_params`, `hw_free`, `prepare`, `trigger`, `pointer`, and device-specific open/close functions.
- `snd_intel8x0_mixer()` creates the AC97 bus, discovers codecs, applies quirks, assigns AC97 PCM slots, and detects multichannel/DRA/20-bit/S/PDIF features.
- `snd_intel8x0_chip_init()` and helper reset functions bring hardware to a known state.
- `intel8x0_suspend()` and `intel8x0_resume()` handle PM reinitialization and IRQ reacquisition.
- `__snd_intel8x0_probe()` wires ALSA card creation, init, mixer, PCM, proc, optional clock measurement, and registration.

## Control Flow
PCI probe creates a managed ALSA card, chooses names and quirks, initializes PCI regions and descriptor rings, resets the controller, requests IRQ, initializes AC97 mixer/codecs, creates PCM devices, registers proc info, optionally measures/tunes the AC97 clock, then registers the card. PCM open selects an `ichdev`, applies constraints, and stores it as runtime private data. `hw_params` opens the corresponding AC97 PCM slots. `prepare` fills a 32-entry buffer descriptor list and programs channel mode registers. `trigger` starts/stops DMA. Interrupts read global status, call `snd_intel8x0_update()` for active streams, advance BDL/LVI/CIV state, and notify ALSA periods. PM suspend frees IRQ and suspends codecs; resume resets hardware, reacquires IRQ, restores SDM/SPDIF settings, resumes codecs, and restores suspended stream registers.

## State and Persistence
All state is runtime kernel state. `intel8x0` persists for card lifetime and owns descriptor pages, stream state, AC97 codec objects, and capability flags. `ichdev` tracks prepared/running stream positions and ring indices. AC97 codec state is delegated to ALSA AC97 core. Hardware registers are reinitialized on resume; there is no persistent storage beyond module parameters and userspace mixer restore.

## Dependencies and Integration Points
The driver integrates with the Linux PCI driver model, ALSA core, ALSA PCM layer, AC97 core, proc info, PM ops, DMA allocation, and IRQ handling. It depends on chipset-specific PCI IDs, AC97 quirk tables, and busmaster register layouts for Intel, SiS, NVIDIA, and ALi variants.

## Risks and Test Signals
Risks include chipset-specific register differences, busy-wait loops on DMA stop, semaphore/read-timeout behavior on broken codecs, global module parameters such as `spdif_aclink` mutating per probe, descriptor-ring position races, and VM-specific pointer handling. Test signals include successful probe across supported PCI IDs, AC97 codec detection including multi-codec ICH4 SDIN routing, playback/capture/MIC/SPDIF PCM operation, period interrupts under stress, suspend/resume with active streams, AC97 clock measurement logs, and clean proc output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/intel8x0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/intel8x0m.c -->
# sources/distributed-fs/ceph-client/sound/pci/intel8x0m.c

## Purpose
`intel8x0m.c` is the ALSA modem-class PCI driver for Intel ICH-family AC'97 modem controllers and compatible SiS/NVIDIA/AMD variants. It is derived from the audio driver but narrows the implementation to modem in/out streams and modem AC97 codec handling.

## Important APIs, Types, and Functions
- `struct ichdev` stores one modem DMA stream's BDL, buffer geometry, indices, interrupt mask, and attached modem AC97 codec.
- `struct intel8x0m` stores PCI/card/MMIO/IRQ state, two modem streams, AC97 bus/codec, descriptor pages, lock, interrupt masks, and position shift.
- `snd_intel8x0m_codec_{semaphore,read,write}()` implement AC97 register access with ready and semaphore checks.
- `snd_intel8x0m_setup_periods()`, `snd_intel8x0m_update()`, and `snd_intel8x0m_interrupt()` manage BDL programming, period advancement, and IRQ dispatch.
- `snd_intel8x0m_pcm_prepare()` writes modem line rate/level AC97 registers and sets up DMA.
- `snd_intel8x0m_mixer()` creates an AC97 bus with `AC97_SCAP_SKIP_AUDIO`, selects primary or secondary codec, and binds modem codecs to both streams.
- `snd_intel8x0m_chip_init()`, PM callbacks, proc helpers, and `__snd_intel8x0m_probe()` implement lifecycle.

## Control Flow
Probe creates the ALSA card, names it as an ICH modem, maps PCI regions, initializes two BDL streams for modem input/output, resets AC-link and DMA registers, requests IRQ, creates the AC97 modem mixer, creates one modem PCM device, registers proc diagnostics, and registers the card. PCM open constrains rates to 8000/9600/12000/16000 Hz mono S16. Prepare programs AC97 line rate and line level, then fills the BDL. Trigger starts/stops DMA. IRQ handling advances the matching modem stream ring and calls `snd_pcm_period_elapsed()`.

## State and Persistence
Runtime state is held in `struct intel8x0m`, two `ichdev` entries, descriptor pages, and the AC97 codec object. The driver has no persistent storage; module parameters select card index/id and optional AC97 clock. Resume rebuilds controller state and resumes the AC97 codec.

## Dependencies and Integration Points
The driver integrates with Linux PCI, ALSA card/PCM, AC97 modem codec support, IRQ, DMA, PM, and proc info. Its PCM device is marked `SNDRV_PCM_CLASS_MODEM`, which helps userspace distinguish it from audio PCM devices.

## Risks and Test Signals
Risks include assumptions that modem is only primary or secondary, no ALi path despite dormant code, spinlock release/reacquire around `snd_pcm_period_elapsed()`, busy waits on stop, and limited rate constraints. Test signals include successful detection of modem AC97 codec, one modem PCM with capture/playback, valid low-rate mono operation, period interrupts, suspend/resume, and proc reporting of codec-ready bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/intel8x0m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/korg1212/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/korg1212/Makefile

## Purpose
This Makefile builds the ALSA Korg 1212 PCI driver object when `CONFIG_SND_KORG1212` is enabled.

## Important APIs, Types, and Functions
- `snd-korg1212-y := korg1212.o` declares the object list for the composite module.
- `obj-$(CONFIG_SND_KORG1212) += snd-korg1212.o` connects Kconfig selection to module/object build output.

## Control Flow
There is no runtime control flow. During Kbuild evaluation, the object is included only when the configuration symbol is enabled.

## State and Persistence
No runtime state is present. The file affects build graph state only.

## Dependencies and Integration Points
It depends on the Linux kernel Kbuild system and the presence of `korg1212.o` from `korg1212.c` in the same directory. It integrates the driver into the broader ALSA PCI build.

## Risks and Test Signals
Risks are minimal: stale object naming or missing source file would break module builds. Test signals are successful `CONFIG_SND_KORG1212=m/y` builds and expected `snd-korg1212` module generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/korg1212/Makefile -->
