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
