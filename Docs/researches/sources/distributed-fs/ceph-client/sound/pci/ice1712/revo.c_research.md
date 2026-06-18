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
