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
