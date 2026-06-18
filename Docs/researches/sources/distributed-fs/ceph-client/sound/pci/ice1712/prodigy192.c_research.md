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
