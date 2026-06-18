# sources/distributed-fs/ceph-client/sound/pci/ice1712/ews.c

## Purpose
Implements low-level support for TerraTec EWX24/96, EWS88MT, EWS88D, DMX 6Fire, Phase88, and terrasoniq TS88 ICE1712 cards. It provides GPIO-bitbanged I2C, CS8427 or CS8404 S/PDIF setup, PCF8574/PCF8575/PCF9554 expander access, AK4524 codec selection, and board-specific ALSA controls.

## Important APIs, Types, and Functions
The exported table is `snd_ice1712_ews_cards[]`. `struct ews_spec` stores up to three I2C expander/transmitter devices. `snd_ice1712_ews_init()` performs board initialization, and `snd_ice1712_ews_add_controls()` registers controls. The I2C bit ops are `ewx_i2c_start()`, `ewx_i2c_stop()`, `ewx_i2c_direction()`, `ewx_i2c_setlines()`, `ewx_i2c_getclock()`, and `ewx_i2c_getdata()`. AKM callbacks include `ews88mt_ak4524_lock()/unlock()`, `ewx2496_ak4524_lock()`, and `dmx6fire_ak4524_lock()`. S/PDIF callbacks encode/decode CS8404 state, while 6Fire helpers read/write PCF9554 registers and expose mux/switch controls.

## Control Flow
Initialization sets ADC/DAC counts by subvendor, allocates `ews_spec`, creates the GPIO-backed I2C bus, then creates board-specific I2C devices: PCF9554 for DMX6Fire, CS8404 plus PCF8574 expanders for EWS88MT-like boards, or PCF8575 for EWS88D. EWX2496 and DMX6Fire initialize CS8427 and set receiver error masks; EWS88MT/D use CS8404 S/PDIF ops and write default status bits. EWS88D returns before analog setup; the remaining boards allocate AKM codec state and initialize the matching AK4524 template. Control registration adds common S/PDIF controls when CS8427 did not provide them, AKM controls for analog boards, and card-specific sensitivity, ADAT, optical, phono, LED, and input-select controls.

## State and Persistence Behavior
`ice->spec` owns the I2C device pointers. PCF expander outputs hold sensitivity, ADAT, input-select, and chip-select state in external hardware. ALSA controls read-modify-write these expanders on demand. GPIO direction/mask is saved and restored around I2C and AKM operations. CS8404 status bytes live in `ice->spdif.cs8403_bits` and `cs8403_stream_bits`; CS8427 state is delegated to the ALSA CS8427 helper.

## Dependencies and Integration Points
The file depends on `ice1712.h`, `ews.h`, ALSA I2C bit-bang support, CS8427/CS8404 helpers, AK4xxx codec support, and ALSA controls. It is selected from the core `card_tables[]` and relies on core PCM/mixer/rate code to call S/PDIF and AKM callbacks.

## Risks
I2C and AKM serial access share GPIO pins and require strict save/restore sequencing. Front-module absence on EWS88MT is detected through PCF access and can fail probe. PCF expander bit polarity differs by control. A notable risk is `snd_ice1712_ews88d_control_put()`: it computes `ndata` but sends `data`, so changed EWS88D controls may report success without updating hardware. Error handling often returns `-EIO` only after bus operations fail, so hardware regressions are easiest to catch with real devices.

## Test Signals
Probe all supported subvendors, confirm I2C device creation and EWS88MT front-module detection, verify CS8427 controls on EWX2496/DMX6Fire and CS8404 controls on EWS88MT/D, exercise AKM mixer controls, test all sensitivity switches and 6Fire muxes, check EWS88D ADAT/optical controls actually change PCF8575 output, and validate suspend/reprobe behavior by checking GPIO and expander state.
