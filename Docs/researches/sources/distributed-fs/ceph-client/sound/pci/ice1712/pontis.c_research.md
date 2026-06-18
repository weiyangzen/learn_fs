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
