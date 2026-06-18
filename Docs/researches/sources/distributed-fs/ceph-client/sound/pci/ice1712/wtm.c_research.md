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
