# subset-b-006398 research

Grouped research report for the ICE1724 ALSA driver subset. Each section is source-tree aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/ice1724.c -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/ice1724.c

### Purpose
`ice1724.c` is the core ALSA PCI driver for VIA/ICEnsemble VT1724/VT1720 Envy24HT/PT devices. It owns module parameters, PCI matching, device creation, EEPROM/model selection, GPIO/I2C/AC97 primitives, PCM DMA setup, S/PDIF controls, MIDI handling, proc diagnostics, and suspend/resume orchestration. Board-specific files plug into this core through `struct snd_ice1712_card_info` tables and callbacks.

### Important APIs, Types, And Functions
The central state object is `struct snd_ice1712`, allocated as ALSA card private data by `snd_devm_card_new`. Important callback surfaces include `ice->gpio.*`, `ice->get_rate`, `ice->set_rate`, `ice->set_mclk`, `ice->set_spdif_clock`, `ice->get_spdif_master_type`, `ice->gpio.set_pro_rate`, `ice->spdif.ops.*`, `ice->pro_open`, and board `chip_init/build_controls/chip_exit` hooks from `struct snd_ice1712_card_info`.

Key functions are `snd_vt1724_create`, `__snd_vt1724_probe`, `snd_vt1724_read_eeprom`, `snd_vt1724_chip_init`, `snd_vt1724_set_pro_rate`, `snd_vt1724_pcm_profi`, `snd_vt1724_pcm_spdif`, `snd_vt1724_pcm_indep`, `snd_vt1724_build_controls`, `snd_vt1724_spdif_build_controls`, `snd_vt1724_interrupt`, `snd_vt1724_read_i2c`, and `snd_vt1724_write_i2c`. The exported routing helpers `snd_ice1724_get_route_val` and `snd_ice1724_put_route_val` are used by card drivers with custom route controls.

### Control Flow
Probe allocates an ALSA card, initializes the generic `snd_ice1712` fields, enables PCI, requests BARs and IRQ, resets the chip, reads EEPROM data or synthetic board EEPROM data, and programs chip registers. It searches `card_tables[]` by model override or subvendor, then invokes the matched board `chip_init`. After board initialization, the core fills missing clock callbacks with standard implementations, derives hardware rate constraints, creates professional, S/PDIF, and independent surround PCMs, builds AC97 or I2S mixer state, creates generic controls, adds S/PDIF controls if present, invokes board `build_controls`, optionally creates MIDI rawmidi devices, and registers the ALSA card.

PCM open paths set runtime hardware capabilities, DMA register descriptors, sync-start behavior, rate constraints, buffer alignment, and current substream pointers. `hw_params` reserves multi-channel DMA lanes and calls `snd_vt1724_set_pro_rate`; `prepare` writes DMA address/size/count registers; `trigger` starts/stops/pauses grouped substreams by setting DMA control bits; `pointer` reads hardware counters. Interrupt handling services MIDI FIFO IRQs and multitrack PCM period events, acknowledges hardware status, and masks FIFO error IRQs to avoid interrupt storms.

### State And Persistence
The driver keeps runtime-only hardware state in `snd_ice1712`: EEPROM bytes, GPIO mask/direction/state, current rate, substream pointers, PCM reservation slots, rawmidi flags, saved PM register values, codec arrays, and card-specific `ice->spec`. `PRO_RATE_LOCKED`, `PRO_RATE_RESET`, and `PRO_RATE_DEFAULT` are module-wide controls exposed as ALSA mixer controls. EEPROM values are read from I2C or replaced by board tables; no permanent writes are made to device EEPROM. ALSA control state is mostly hardware-backed or cached in memory and restored through board/core resume hooks after suspend.

### Dependencies And Integration Points
This file integrates Linux PCI, IRQ, PM, ALSA card/PCM/control/rawmidi/proc APIs, AC97 support, AES/IEC958 definitions, and the local `ice1712.h`/`envy24ht.h` register definitions. It includes many board headers and aggregates their `snd_vt1724_*_cards` tables. Board files depend on the I2C helpers, GPIO helpers, route helpers, clock callbacks, PCM creation side effects, and `ice->spdif.ops`/`ice->gpio.set_pro_rate` callbacks supplied here.

### Risks
Most risk is hardware sequencing: clock changes are rejected while DMA is active, but board `set_pro_rate` callbacks still must tolerate codec timing constraints. Several busy-wait loops have fixed retry counts and only log on timeout. GPIO writes rely on correct EEPROM masks and board restore discipline. The interrupt handler has defensive timeout logic because TX MIDI IRQs can be sticky during PCM playback and FIFO errors can lock up machines. Global rate-lock/reset settings are shared across cards. Suspend is disabled unless board or fallback logic marks `pm_suspend_enabled`, so unsupported boards may not fully restore.

### Test Signals
Useful signals are successful module bind, correct `card->shortname/longname`, visible PCM devices, ALSA controls for clock/rate/routing/S/PDIF, `/proc/asound/card*/ice1724` EEPROM/register output, MIDI loopback behavior, PCM playback/capture at each advertised rate, rate-lock rejection while mismatched, S/PDIF default/status changes, and suspend/resume recovery on boards that enable PM. Error paths should be exercised with unknown subvendor, missing EEPROM, invalid EEPROM size, busy DMA during rate changes, and absent S/PDIF capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/ice1724.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/juli.c -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/juli.c

### Purpose
`juli.c` provides board-specific support for the ESI Juli@ VT1724 card. It supplies synthetic EEPROM data, custom clock/rate control through GPIO-connected Xilinx/PLL logic, AK4114 S/PDIF receiver integration, AK4358 DAC setup, monitor/mute mixer controls, virtual master volume, and PM callbacks.

### Important APIs, Types, And Functions
`struct juli_spec` stores the `ak4114` instance and analog-presence flag. The file defines Juli-specific rate lists and GPIO encodings, I2C accessors `juli_ak4114_read/write` and `juli_akm_write`, codec rate updater `juli_akm_set_rate_val`, controls `juli_mute_get/put`, `juli_add_controls`, PM callbacks `juli_suspend/resume`, clock callbacks `juli_is_spdif_master`, `juli_get_rate`, `juli_set_rate`, `juli_set_mclk`, `juli_set_spdif_clock`, and init entry `juli_init`.

### Control Flow
The core selects `snd_vt1724_juli_cards[]` and calls `juli_init`. Initialization allocates `juli_spec`, creates the AK4114 over VT1724 I2C, installs a change callback, forces analog I/O present, allocates and initializes one AK4358 codec descriptor, overrides `ice->hw_rates` and clock callbacks, wires `ice->spdif.ops.open` to rate-limit S/PDIF capture, and enables PM hooks. Control building first adds AKM controls, then GPIO-based master/monitor switches, a virtual master volume over the AKM follower controls, and AK4114 controls on the capture substream.

### State And Persistence
Persistent hardware identity comes from `juli_eeprom`; runtime state lives in GPIO bits, AKM register images, AK4114 state, and `ice->spec`. GPIO bits encode internal/external clock, base frequency, multiplier, AK5385 mode, monitor enables, and output mute. On rate changes, GPIO pins select PLL frequency and ADC mode, the AC97 cold-reset bit is pulsed to reset codecs, AK4358 DFS is rewritten, and AK4114 is reinitialized. PM suspend resets/soft-mutes AK4358 and suspends AK4114; resume unresets and resumes both.

### Dependencies And Integration Points
This file depends on core I2C helpers, GPIO callbacks, `snd_ak4114_*`, `snd_ice1712_akm4xxx_*`, ALSA controls/TLV, and core PCM open behavior. It integrates by overriding clock callbacks because the card does not use the standard ICE1724 clock scheme. `juli_spdif_in_open` and `juli_ak4114_change` cooperate with the core S/PDIF capture path to constrain runtime rates and reprogram codecs when external S/PDIF rate changes.

### Risks
Analog daughterboard detection is disabled and forced present because hardware detection was unreliable. Comments document unresolved monitor-routing behavior: some monitor controls may not match vendor documentation. `get_gpio_val` returns 0 for unsupported rates, so constraints must remain correct. Rate changes cold-reset codecs and reinitialize AK4114, making sequencing sensitive. GPIO mute semantics are inverted for master mute but normal for monitor switches, so control changes are easy to regress.

### Test Signals
Check model selection by subvendor/model, AK4114 creation, visible AKM and AK4114 controls, master volume follower behavior, monitor switches, S/PDIF capture rate constraint when externally clocked, sample-rate changes across all `juli_rates`, GPIO mute/unmute behavior, and suspend/resume restoring AK4358/AK4114 operation. Regression tests should include external S/PDIF rate changes and analog playback after clock switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/juli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/juli.h -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/juli.h

### Purpose
`juli.h` is the public board header that lets the ICE1724 core advertise and match ESI Juli@ cards.

### Important APIs, Types, And Functions
It defines `JULI_DEVICE_DESC`, `VT1724_SUBDEVICE_JULI`, and declares `extern struct snd_ice1712_card_info snd_vt1724_juli_cards[]`.

### Control Flow
The core includes this header, adds `snd_vt1724_juli_cards` to `card_tables[]`, and uses the subdevice ID or model name to call the `juli.c` initialization and control-building callbacks.

### State And Persistence
There is no runtime state in the header. The subdevice ID is a stable matching constant, while `snd_vt1724_juli_cards[]` points to synthetic EEPROM and callbacks in `juli.c`.

### Dependencies And Integration Points
The declaration depends on `struct snd_ice1712_card_info` being visible through the including C file. It integrates with module device descriptions and the board table scan in `ice1724.c`.

### Risks
Incorrect subdevice or description strings would make the board unreachable by automatic detection or model override. The header has no guards beyond the include guard and relies on `juli.c` to define the table exactly once.

### Test Signals
Build success, `modinfo`/device description inclusion, and successful probe of a card with subvendor `0x31305345` are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/juli.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/maya44.c -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/maya44.c

### Purpose
`maya44.c` implements ESI Maya44 board support. It manages two WM8776 codecs over I2C, custom mixer controls for volumes, switches, GPIO-backed phantom power/S/PDIF/capture source, card-specific playback routing, sample-rate notifications, forced secondary capture DMA, and synthetic EEPROM data.

### Important APIs, Types, And Functions
`struct snd_wm8776` caches WM8776 registers, volumes, and switch bits. `struct snd_maya44` stores the owning `snd_ice1712`, two codecs, and a mutex. Key functions are `wm8776_write`, `wm8776_write_bits`, `maya_vol_get/put`, `maya_sw_get/put`, `maya_gpio_sw_get/put`, `maya_rec_src_get/put`, `maya_pb_route_get/put`, `wm8776_init`, `set_rate`, `maya44_init`, and `maya44_add_controls`.

### Control Flow
On `maya44_init`, the driver allocates `snd_maya44`, initializes the mutex, sets four DAC and four ADC channels, initializes two WM8776 codecs at I2C addresses `0x34` and `0x36`, selects line input by default, overrides `ice->hw_rates`, installs `ice->gpio.set_pro_rate = set_rate`, forces RDMA1 for the second input channel, and marks `ice->own_routing` so generic route controls are skipped. `maya44_add_controls` registers all Maya controls using `ice->spec` as private data.

### State And Persistence
All WM8776 writes are cached in `wm->regs`; ALSA control values are cached in `wm->volumes` and `wm->switch_bits`. GPIO state controls phantom power, mic relay, and S/PDIF input inversion. Capture source selection changes both the mic relay and codec ADC mux. Playback route controls write the core `ROUTE_PLAYBACK` register through shared route helpers with Maya-specific bit shifts.

### Dependencies And Integration Points
This file depends on VT1724 I2C helpers, generic ICE1712 GPIO read/write helpers, ALSA control/TLV APIs, and the core route helper functions. It integrates with core rate changes through `ice->gpio.set_pro_rate`, with PCM topology through `num_total_dacs/adcs` and `force_rdma1`, and with generic control building by setting `own_routing`.

### Risks
The comment notes possible unknown meaning for route controls 5-9, so only four are exposed. Some GPIO names reflect known hardware behavior rather than a full schematic. `maya_sw_get` reads cached switch bits without taking the mutex, so external or resume-side mutations would need care. `set_rate` calls `snd_BUG()` for unexpected rates; constraints must stay aligned with `dac_rates`. The WM8776 ADC rate is limited to 256x/96 kHz even when DAC rates go higher.

### Test Signals
Check creation of two codec control instances, capture-source relay behavior, phantom and S/PDIF switches, playback route mapping, RDMA1 capture availability, supported rates from 32 kHz to 192 kHz, and correct WM8776 master-mode writes during rate changes. Useful runtime signals are I2C writes succeeding and ALSA controls preserving cached values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/maya44.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/maya44.h -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/maya44.h

### Purpose
`maya44.h` declares the ESI Maya44 board identity and card table for the ICE1724 core.

### Important APIs, Types, And Functions
It defines `MAYA44_DEVICE_DESC`, `VT1724_SUBDEVICE_MAYA44`, and declares `snd_vt1724_maya44_cards[]`.

### Control Flow
The core includes the header and scans `snd_vt1724_maya44_cards` during EEPROM/model matching. A match routes board initialization to `maya44_init` and control registration to `maya44_add_controls`.

### State And Persistence
The header has no mutable state. Its constants determine detection and user-facing device description aggregation.

### Dependencies And Integration Points
It integrates with `ice1724.c` card table discovery and relies on `maya44.c` for the table definition and synthetic EEPROM payload.

### Risks
Wrong constants would prevent the board-specific codec setup from running, leaving the core with generic behavior that cannot drive the Maya44 codecs properly.

### Test Signals
Build linkage of `snd_vt1724_maya44_cards`, model override `maya44`, and detection of subvendor `0x34315441` are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/maya44.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/phase.c -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/phase.c

### Purpose
`phase.c` supports Terratec PHASE 22, PHASE 28, and Terrasoniq TS22 PCI boards. PHASE22/TS22 use generic AK4524 support; PHASE28 has custom WM8770 SPI initialization, register caching, and many playback/capture controls.

### Important APIs, Types, And Functions
`struct phase28_spec` caches stereo master volume/mute and eight DAC channel volumes. Important functions include `phase22_init`, `phase22_add_controls`, `phase28_spi_write`, `wm_get`, `wm_put`, `wm_set_vol`, `phase28_init`, `phase28_add_controls`, `wm_*_get/put` mixer callbacks, `phase28_deemp_get/put`, and `phase28_oversampling_get/put`.

### Control Flow
For PHASE22/TS22, `phase22_init` marks VT1720 mode, sets two DAC/two ADC channels, allocates one AKM codec, and initializes `SND_AK4524` using GPIO private data. `phase22_add_controls` delegates to generic AKM control building. For PHASE28, `phase28_init` sets eight DAC/two ADC topology, allocates `phase28_spec` and an AKM image cache, configures GPIO direction, resets the WM codec, writes a long WM8770 initialization script over bit-banged SPI, initializes cached master/channel volume state as muted, and programs effective volumes. `phase28_add_controls` adds per-channel, master, digital PCM, deemphasis, and ADC oversampling controls.

### State And Persistence
PHASE28 register values are mirrored in `ice->akm[0].images`; user-facing volume/mute state is stored in `phase28_spec`. Effective analog volume is derived from per-channel volume and stereo master volume, with `WM_VOL_MUTE` flags folded into writes. No persistent hardware storage is updated; synthetic EEPROM arrays describe the supported boards.

### Dependencies And Integration Points
The file depends on ALSA controls/TLV, generic AKM support, ICE1712 GPIO save/restore helpers, and `phase.h` GPIO constants. It integrates with the core through `snd_vt1724_phase_cards[]` and by setting `num_total_dacs/adcs`, `vt1720`, `chip_init`, and `build_controls`.

### Risks
The top comments note uncertain CS8416 support for later PHASE22/TS22 revisions. PHASE28 SPI is manually bit-banged and changes GPIO masks/directions, so restore correctness is critical. The volume math uses lookup tables and cached mute flags; off-by-one or channel-index mistakes affect audio levels. Some control setters skip invalid values rather than returning errors. There are no PM callbacks, so register state may not recover after suspend unless handled by broader core behavior.

### Test Signals
Test board selection for all three subvendor IDs, AK4524 controls on PHASE22/TS22, WM8770 register programming on PHASE28, all PHASE28 playback channel controls, master mute/volume interactions, PCM digital attenuation, deemphasis, ADC oversampling, and route/clock operation at advertised rates. GPIO/SPI bus behavior can be inspected with hardware register readback where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/phase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/phase.h -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/phase.h

### Purpose
`phase.h` defines the Terratec/Terrasoniq PHASE board identities, declares their card table, and centralizes PHASE28 GPIO bit assignments.

### Important APIs, Types, And Functions
It defines `PHASE_DEVICE_DESC`, `VT1724_SUBDEVICE_PHASE22`, `VT1724_SUBDEVICE_PHASE28`, `VT1724_SUBDEVICE_TS22`, declares `snd_vt1724_phase_cards[]`, and defines PHASE28 SPI, reset, AC97, digital-select, headphone-select, and data-mask GPIO bits.

### Control Flow
`ice1724.c` includes the header and scans `snd_vt1724_phase_cards`; `phase.c` includes the header and uses the GPIO constants when resetting and programming the PHASE28 WM codec.

### State And Persistence
There is no mutable state. GPIO bit definitions are hardware contract constants used to avoid duplicated magic numbers in the implementation.

### Dependencies And Integration Points
It integrates with the core board table and with `phase28_spi_write`/`phase28_init` in `phase.c`.

### Risks
Wrong GPIO constants would corrupt codec programming or reset behavior. The header exposes constants only for PHASE28; PHASE22 GPIO wiring lives in `phase.c` AKM private data.

### Test Signals
Compile-time use of the constants, correct detection of the three subdevices, and successful PHASE28 codec initialization are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/phase.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/pontis.c -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/pontis.c

### Purpose
`pontis.c` implements Pontis MS300 support for a VT1720-style board with WM8776 analog codec and CS8416 S/PDIF receiver. It provides synthetic EEPROM data, codec initialization, custom mixer controls, writable proc diagnostics for WM registers, read-only proc diagnostics for CS registers, GPIO controls, and S/PDIF input source selection.

### Important APIs, Types, And Functions
The file uses `ice->akm[0].images` as a WM8776 register cache. Key functions include `wm_get`, `wm_put_nocache`, `wm_put`, `wm_dac_vol_get/put`, `wm_adc_vol_get/put`, `wm_adc_mux_get/put`, `wm_bypass_get/put`, `wm_chswap_get/put`, SPI helpers `spi_write/read`, `cs_source_get/put`, GPIO control callbacks, `wm_proc_init`, `cs_proc_init`, `pontis_init`, and `pontis_add_controls`.

### Control Flow
`pontis_init` marks `vt1720`, sets two DAC/two ADC channels, allocates an AKM cache, initializes `ice->gpio.saved[0]` as the selected CS8416 source, writes WM8776 init sequences over I2C, pulses the AC97 reset bit to reset CS8416, and writes CS8416 init registers through bit-banged GPIO SPI. `pontis_add_controls` registers codec, source, bypass, swap, and raw GPIO controls, then creates proc entries.

### State And Persistence
WM register state is cached in `ice->akm[0].images`. The selected CS8416 source is stored in `ice->gpio.saved[0]` rather than normal GPIO helpers, because generic GPIO get/put would overwrite it. GPIO mask/direction controls update `ice->gpio.write_mask` and `ice->gpio.direction`; data writes program hardware after applying those cached values. No state is persisted beyond runtime.

### Dependencies And Integration Points
Pontis uses the core VT1724 I2C helper for WM8776, generic ICE1712 GPIO helpers for bit-banged CS8416 SPI, ALSA control/proc APIs, and core board matching via `snd_vt1720_pontis_cards[]`. It sets `vt1720` so core GPIO width and PCM constraints match the hardware.

### Risks
The subdevice is a dummy ID, so model override may be important. GPIO controls expose low-level card pins while reserving bits 4-7 for CS8416; misuse can still disrupt hardware. SPI routines temporarily replace GPIO masks/directions and must restore them. There is no PM reinitialization path in this file. Some comments identify FIXME-level uncertainty about GPIO control interface placement.

### Test Signals
Check WM8776 and CS8416 proc outputs, S/PDIF source switching among Coax/Optical/CD, PCM and capture volume controls, ADC input switches, analog bypass, channel swap, raw GPIO controls, and stable playback/capture after repeated SPI/proc access. Model override `ms300` should select the card table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/pontis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/pontis.h -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/pontis.h

### Purpose
`pontis.h` declares Pontis MS300 board support for the ICE1724/VT1720 core.

### Important APIs, Types, And Functions
It defines `PONTIS_DEVICE_DESC`, dummy subdevice ID `VT1720_SUBDEVICE_PONTIS_MS300`, and declares `snd_vt1720_pontis_cards[]`.

### Control Flow
The core includes this header and scans the Pontis card table. A match or model override invokes `pontis_init` and `pontis_add_controls`.

### State And Persistence
The header is static metadata only; runtime state and synthetic EEPROM live in `pontis.c`.

### Dependencies And Integration Points
It integrates with `ice1724.c` `card_tables[]` and with device-description aggregation elsewhere in the driver family.

### Risks
Because the ID is explicitly dummy, automatic hardware matching may be less robust than boards with real subvendor IDs.

### Test Signals
Build linkage, model override `ms300`, and successful control/proc creation from `pontis.c` validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/pontis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy192.c -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy192.c

### Purpose
`prodigy192.c` supports the AudioTrak Prodigy 192 VE. It drives a STAC9460 codec over I2C, optionally detects and initializes an MI/ODI/O AK4114 S/PDIF input daughtercard over a GPIO 4-wire bus, and exposes DAC/ADC/mic/source controls plus proc diagnostics.

### Important APIs, Types, And Functions
`struct prodigy192_spec` stores optional `ak4114` and a `mute_mutex` used to serialize rate-change muting with user mute controls. Key functions are `stac9460_get/put`, `stac9460_dac_mute`, STAC DAC/ADC volume and mute callbacks, `stac9460_mic_sw_get/put`, `stac9460_set_rate_val`, 4-wire helpers `prodigy192_ak4114_read/write`, AK4114 input switch callbacks, `prodigy192_miodio_exists`, `prodigy192_ak4114_init`, `prodigy192_init`, and `prodigy192_add_controls`.

### Control Flow
Initialization sets six DAC/two ADC topology, allocates the spec and mutex, writes STAC reset/master-clocking defaults, installs `ice->gpio.set_pro_rate = stac9460_set_rate_val`, then probes the optional AK4114 by writing and reading a safe mask register. If present, it creates the AK4114 with custom 4-wire accessors. Control building adds STAC controls, adds AK4114 input/build controls only when the daughtercard exists, and registers a read-only proc dump for STAC registers.

### State And Persistence
STAC9460 state is primarily hardware-backed via I2C reads/writes. Rate changes temporarily mute master plus six DAC volume registers, update master clocking, then unmute only registers that were changed by the temporary mute operation. AK4114 state is held by the ALSA AK4114 helper. Synthetic EEPROM configures GPIO direction so the AK4114 data-in line is input and GPIO20 selects ICE1724 S/PDIF output.

### Dependencies And Integration Points
The file depends on core I2C helpers for STAC, ICE1712 GPIO save/restore for the bit-banged AK4114 bus, `stac946x.h`, ALSA controls/TLV, AK4114 helper APIs, and core rate notification through `ice->gpio.set_pro_rate`. It integrates with the core via `snd_vt1724_prodigy192_cards[]`.

### Risks
Several ADC setters have suspicious change accumulation patterns: `stac9460_adc_mute_put` and `stac9460_adc_vol_put` overwrite `change` each loop, so only the last channel can determine the return value. `stac9460_adc_vol_put` combines `ovol` into the new register value, which may preserve the wrong non-volume bits because `ovol` is derived from a transformed volume rather than the raw register. AK4114 presence probing mutates a real register and must restore it. The comments say AK4114 external rate detection is unreliable, so checks disable rate validation.

### Test Signals
Check STAC register proc output, six DAC volume/switch controls, ADC capture controls, analog line/mic input selection, rate changes at 48/96/192 kHz while preserving mute state, MI/ODI/O detection both present and absent, AK4114 Toslink/Coax input control, and S/PDIF capture without false rate-check failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy192.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy192.h -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy192.h

### Purpose
`prodigy192.h` declares AudioTrak Prodigy 192 board matching constants and GPIO pins used by the optional MI/ODI/O AK4114 interface.

### Important APIs, Types, And Functions
It defines `PRODIGY192_DEVICE_DESC`, STAC9460 I2C address `PRODIGY192_STAC9460_ADDR`, subdevice `VT1724_SUBDEVICE_PRODIGY192VE`, AK4114 GPIO masks `VT1724_PRODIGY192_CS/CCLK/CDOUT/CDIN`, and declares `snd_vt1724_prodigy192_cards[]`.

### Control Flow
The core uses the table declaration during board matching. `prodigy192.c` uses the address and GPIO masks to access STAC9460 and bit-bang AK4114 reads/writes.

### State And Persistence
No mutable state is defined. The constants encode hardware wiring and matching identity.

### Dependencies And Integration Points
It integrates with `ice1724.c` card tables and the low-level GPIO protocol in `prodigy192.c`.

### Risks
Incorrect GPIO masks would break optional S/PDIF daughtercard detection and access. Incorrect codec address would make all STAC controls nonfunctional.

### Test Signals
Successful Prodigy 192 probe, STAC I2C access at address `0x54`, and AK4114 access over GPIO8-11 validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy192.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy_hifi.c -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy_hifi.c

### Purpose
`prodigy_hifi.c` supports Audiotrak Prodigy 7.1 HiFi, Prodigy HD2, and Hercules Fortissimo IV boards. It handles WM8776 and WM8766 codecs for 7.1-style boards, AK4396 for HD2, custom volume/mux controls, proc diagnostics, SPI/I2C codec access, PM restore, and synthetic EEPROM data.

### Important APIs, Types, And Functions
`struct prodigy_hifi_spec` caches stereo master and eight channel volumes. Key functions are `wm_get/put`, `wm8766_spi_write`, `ak4396_write`, AK4396 volume callbacks, WM/WM8766 volume and master callbacks, ADC mux/volume/bypass/swap callbacks, `wm_proc_init`, `prodigy_hifi_add_controls`, `prodigy_hd2_add_controls`, `wm8766_init`, `wm8776_init`, `prodigy_hifi_resume`, `prodigy_hifi_init`, `ak4396_init`, `prodigy_hd2_resume`, and `prodigy_hd2_init`.

### Control Flow
For Prodigy 7.1 HiFi and Fortissimo IV, initialization sets eight DAC/one ADC topology, allocates AKM image cache and spec, initializes WM8776 over I2C, writes defaults, initializes WM8766 over bit-banged SPI, and installs a PM resume hook. Controls expose master, front, rear, center, LFE, side, capture, ADC mux, bypass, and channel swap. For HD2, initialization sets one DAC/one ADC topology, allocates the same cache/spec pattern, initializes AK4396 over GPIO serial, and registers only front playback volume plus WM proc support.

### State And Persistence
WM8776 register state is cached in `ice->akm[0].images`; volume state is cached in `prodigy_hifi_spec`. WM8766 and AK4396 are write-only from the driver’s perspective, so cached user values are required for resume and later master-volume recomputation. No device EEPROM is written; separate synthetic EEPROM arrays distinguish Prodigy 7.1, HD2, and Fortissimo IV.

### Dependencies And Integration Points
The file uses core I2C helpers, generic GPIO helpers for SPI/serial writes, ALSA controls/TLV/proc, and core PM callbacks. It integrates through `snd_vt1724_prodigy_hifi_cards[]`, setting per-board `driver`, `chip_init`, `build_controls`, and EEPROM fields.

### Risks
`wm_adc_mux_put` computes `change` but always returns 0, so ALSA clients will not be notified of a changed ADC mux bit. Some write-only codec paths depend entirely on cached values for resume correctness. The same spec type is reused for HD2 despite different codec topology, so controls must stay partitioned by board. Manual GPIO serial routines must restore masks/directions. PM resume restores selected WM8776 registers but intentionally excludes DAC attenuation until volumes are recomputed.

### Test Signals
For 7.1/Fortissimo, verify all playback channel volumes, master scaling across WM8776 and WM8766, capture mux/volume, bypass/swap, proc WM register access, and resume restoration. For HD2, verify AK4396 reset/init, front volume writes, resume volume restore, and absence of irrelevant 7.1 controls. The ADC mux control should be specifically checked for user-visible change notification because of the return-value issue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy_hifi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy_hifi.h -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy_hifi.h

### Purpose
`prodigy_hifi.h` declares board descriptions and subdevice IDs for the Prodigy HiFi family and Fortissimo IV.

### Important APIs, Types, And Functions
It defines `PRODIGY_HIFI_DEVICE_DESC`, `VT1724_SUBDEVICE_PRODIGY_HIFI`, `VT1724_SUBDEVICE_PRODIGY_HD2`, `VT1724_SUBDEVICE_FORTISSIMO4`, and declares `snd_vt1724_prodigy_hifi_cards[]`.

### Control Flow
The core scans `snd_vt1724_prodigy_hifi_cards` during probe. Matching entries call either `prodigy_hifi_init`/`prodigy_hifi_add_controls` or `prodigy_hd2_init`/`prodigy_hd2_add_controls`.

### State And Persistence
The header carries no mutable state. The IDs select different synthetic EEPROM arrays and codec paths in `prodigy_hifi.c`.

### Dependencies And Integration Points
It integrates with the core card table and device description string aggregation.

### Risks
The macro spans multiple product names; changing string formatting can affect module aliases/descriptions. Misassigned subdevice IDs would route boards to the wrong codec topology.

### Test Signals
Probe of all three subdevice IDs, correct ALSA `driver` names, and board-specific control sets validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/prodigy_hifi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/psc724.c -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/psc724.c

### Purpose
`psc724.c` supports the Philips PSC724 Ultimate Edge / VT1722-style board. It uses shared WM8766 and WM8776 helper drivers, adds board-specific codec write functions, headphone jack detection, master speaker muting, rate-change volume restore, PM resume, and synthetic EEPROM that corrects buggy hardware EEPROM contents.

### Important APIs, Types, And Functions
`struct psc724_spec` contains `snd_wm8766`, `snd_wm8776`, mute/jack booleans, `ice`, delayed work, and cached headphone state. Key functions are `psc724_wm8766_write`, `psc724_wm8776_write`, `psc724_set_master_switch`, `psc724_set_jack_state`, `psc724_update_hp_jack_state`, `psc724_set_jack_detection`, `psc724_ctl_get/put`, `psc724_add_controls`, `psc724_set_pro_rate`, `psc724_resume`, `psc724_init`, and `psc724_exit`.

### Control Flow
Initialization allocates spec, sets six DAC/two ADC topology, wires WM8776 I2C and WM8766 GPIO-SPI write callbacks, initializes both codecs, sets WM8766 I2S 24-bit interface, installs rate and PM callbacks, initializes delayed work, and enables jack detection. Control building renames WM helper controls to PSC724-specific front/surround/CLFE/capture names, builds WM8776/WM8766 controls, and adds two custom boolean controls for master speakers and headphone jack detection. Exit cancels delayed work.

### State And Persistence
Runtime state includes codec helper register caches, `mute_all`, `jack_detect`, `hp_connected`, and delayed work scheduling. Jack detection polls GPIO14 every second. When headphones are connected, speakers are muted through GPIO20/GPIO22 and WM8776 headphone power is adjusted; ALSA control notifications are emitted for affected controls. Rate changes restore codec volume settings because PMCLK stop can disturb codec volume state.

### Dependencies And Integration Points
The file depends on local `wm8766.h` and `wm8776.h` helper APIs, core GPIO save/restore and I2C helpers, delayed work, and ALSA control notification. It integrates through `snd_vt1724_psc724_cards[]`, `chip_exit`, `gpio.set_pro_rate`, and PM callbacks.

### Risks
`psc724_ctl_put` always returns 0 even when state changes, so mixer clients may not receive normal change feedback from the put return value. Jack detection is polling-based and can race with manual master speaker switch changes. The headphone state mutates both GPIO mute bits and WM8776 power, so notification and state synchronization are important. SPI writes are bit-banged and must preserve GPIO masks/directions. The EEPROM override is required because the real EEPROM is documented as buggy.

### Test Signals
Verify WM helper controls with PSC724 names, master speaker switch behavior, headphone jack polling and notifications, delayed work cancellation on removal, playback routing for front/rear/CLFE devices, volume restore after rate change, PM resume restoring both codecs, and no S/PDIF input exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/psc724.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/psc724.h -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/psc724.h

### Purpose
`psc724.h` declares Philips PSC724 Ultimate Edge board support for the ICE1724 family.

### Important APIs, Types, And Functions
It defines `PSC724_DEVICE_DESC`, subdevice ID `VT1724_SUBDEVICE_PSC724`, and declares `snd_vt1724_psc724_cards[]`.

### Control Flow
The core includes this header and uses the table in `card_tables[]`; a match invokes `psc724_init`, `psc724_add_controls`, and `psc724_exit` on teardown.

### State And Persistence
No mutable state is present. The ID selects the PSC724 EEPROM override and codec-helper path.

### Dependencies And Integration Points
It integrates with `ice1724.c` board matching and `psc724.c` table definition.

### Risks
Incorrect ID or missing declaration would leave the PSC724 using generic setup despite requiring EEPROM correction and helper codec initialization.

### Test Signals
Successful detection of subdevice `0xab170619`, creation of PSC724-specific controls, and invocation of chip exit on removal validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/psc724.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/quartet.c -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/quartet.c

### Purpose
`quartet.c` implements Infrasonic Quartet support. It controls AK4620 ADC/DAC codecs over GPIO SPI, AK4113 S/PDIF receiver over I2C, external CPLD/system/monitor registers through GPIO latch sequences, custom clocking with S/PDIF and word-clock options, monitor/input/mute/phantom controls, virtual master volume, proc diagnostics, and synthetic EEPROM.

### Important APIs, Types, And Functions
`struct qtet_spec` stores AK4113 and cached SCR/MCR/CPLD register images. `struct qtet_kcontrol_private` describes reusable controls. Key functions are `qtet_ak4113_read/write`, `qtet_akm_write`, `qtet_akm_set_regs`, `qtet_akm_set_rate_val`, `reg_write`, `set_scr/set_mcr/set_cpld`, `proc_regs_read`, `qtet_mute_get/put`, `qtet_ain12_sw_get/put`, `qtet_php_get/put`, generic `qtet_sw_get/put`, `qtet_add_controls`, clock callbacks `qtet_is_spdif_master/get_rate/set_rate/set_mclk/set_spdif_clock/get_spdif_master_type`, `qtet_ak4113_change`, `qtet_spdif_in_open`, and `qtet_init`.

### Control Flow
Initialization forces ICE1724 into external-clock mode supplied by Quartet circuitry, allocates spec, overrides all clock/rate callbacks, advertises three external clock names, and assigns `qtet_spdif_in_open` to both S/PDIF and pro-open hooks. It initializes SCR with phantom off then codec power-up, clears MCR and CPLD, sets two stereo DAC/two stereo ADC topology, initializes AK4620 through AKM helpers, creates AK4113, sets AK4113 change callback, creates proc diagnostics, and sets initial rate to 44.1 kHz. Control building creates AKM controls, custom SCR/MCR/CPLD controls, virtual master volume, and AK4113 capture controls.

### State And Persistence
SCR, MCR, and CPLD are write-only external registers, so the driver caches their values in `qtet_spec`. Clock source/rate, input selection, monitor routing, mute, phantom power, and coax source all live in these cached register images plus hardware latches. AK4620 rate mode is updated on internal rate changes and when AK4113 reports an external S/PDIF rate change. No persistent EEPROM writes occur.

### Dependencies And Integration Points
The file uses core I2C/GPIO helpers, ALSA AK4113 and AKM helpers, ALSA controls/TLV/proc, and core clock callback surfaces. It integrates via `snd_vt1724_qtet_cards[]`, overrides `ice->hw_rates`, `ice->ext_clock_names/count`, `ice->spdif.ops.open`, and `ice->pro_open`.

### Risks
The GPIO latch protocol changes direction/mask broadly and must restore outputs correctly. Cached write-only register images can diverge from hardware after reset unless init/resume paths replay them; no explicit PM callbacks are present. `qtet_get_spdif_master_type` returns `-1` for internal mode even though core callers expect external indices only when external is active. Phantom power sequencing deliberately toggles voltage and enable in order; regressions could affect hardware safety. AKM allocation uses space for two descriptors but configures one codec with two chips, so assumptions must remain consistent.

### Test Signals
Test all internal rates, S/PDIF and both word-clock external clock selections, S/PDIF capture rate constraint, AK4113 external rate callback, mute and AK4620 soft mute, phantom power sequencing, analog input selectors, monitor routing switches, virtual master followers, proc `quartet` SCR/MCR/CPLD output, and recovery after card reset or suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/quartet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/quartet.h -->
## sources/distributed-fs/ceph-client/sound/pci/ice1712/quartet.h

### Purpose
`quartet.h` declares the Infrasonic Quartet board identity and card table.

### Important APIs, Types, And Functions
It defines `QTET_DEVICE_DESC`, subdevice ID `VT1724_SUBDEVICE_QTET`, and declares `snd_vt1724_qtet_cards[]`.

### Control Flow
The core includes the header, scans the Quartet card table, and invokes `qtet_init` and `qtet_add_controls` when the subvendor or model matches.

### State And Persistence
The header is static metadata only. Runtime clock/register/cache state lives in `quartet.c`.

### Dependencies And Integration Points
It integrates with `ice1724.c` board aggregation and the table definition in `quartet.c`.

### Risks
Incorrect subdevice matching would prevent the custom CPLD/clock setup from running, which is essential for this board.

### Test Signals
Build linkage, model override `quartet`, detection of subdevice `0x30305349`, and presence of Quartet-specific clock/control surfaces validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/quartet.h -->
