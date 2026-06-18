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
