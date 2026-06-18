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
