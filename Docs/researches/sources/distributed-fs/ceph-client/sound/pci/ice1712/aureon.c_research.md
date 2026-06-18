# sources/distributed-fs/ceph-client/sound/pci/ice1712/aureon.c

## Purpose

This file implements VT1724 Envy24HT board support for Terratec Aureon 5.1 Sky, Aureon 7.1 Space, Aureon 7.1 Universe, and Audiotrak Prodigy 7.1/LT/XT cards. It handles board-specific GPIO protocols, WM8770 setup and mixer controls, STAC9744 AC97 emulation/cache over a Xilinx GPIO bridge, CS8415A S/PDIF receiver controls, Aureon Universe PCA9554 input mux controls, headphone amplifier control, suspend/resume restoration, EEPROM override data, and card descriptor registration.

## Important APIs, Types, and Functions

`struct aureon_spec` stores cached STAC9744 AC97 registers, CS8415 mux selection, master and per-DAC WM volume/mute state, and PCA9554 output state. GPIO/I2C/SPI helpers include `aureon_pca9554_write()`, `aureon_ac97_write/read/init()`, `aureon_spi_write/read()`, `aureon_cs8415_get/read/put()`, `wm_get()`, `wm_put_nocache()`, and `wm_put()`. Mixer callbacks cover WM8770 master/DAC volume and mute, PCM digital volume/mute, ADC gain/mute/source, deemphasis, oversampling, AC97 monitor controls, CS8415 S/PDIF controls, and Universe aux muxing. Lifecycle functions are `aureon_add_controls()`, `aureon_reset()`, `aureon_resume()`, and `aureon_init()`.

## Control Flow

The parent ICE1724 driver calls `aureon_init()` from the selected card-info entry. Initialization allocates `aureon_spec`, sets DAC/ADC counts by model, allocates one `snd_akm4xxx` record as a WM8770 image cache, resets the board, initializes all master and per-DAC volumes as muted, writes those mutes, and installs PM resume hooks. `aureon_reset()` initializes the STAC9744 cache and AC97 bridge, configures GPIO, toggles WM8770 reset, writes Aureon or Prodigy WM initialization tables, optionally initializes CS8415A and headphone amp, restores GPIO state, and initializes PCA9554 direction/output. `aureon_add_controls()` adds controls conditionally by board type and probes CS8415 ID `0x41` before registering S/PDIF receiver controls.

## State and Persistence Behavior

The file maintains explicit software caches for hardware that is not normally readable: `spec->stac9744`, `ice->akm[0].images`, `spec->master`, `spec->vol`, `spec->cs8415_mux`, and `spec->pca9554_out`. EEPROM override arrays provide persistent board configuration to the parent. PM resume rebuilds hardware from reset tables and cached volumes. GPIO state is protected by save/restore helpers around bit-banged transactions.

## Dependencies and Integration Points

The file depends on ALSA control/TLV infrastructure, ICE1712/Envy24HT parent APIs, `aureon.h` IDs and GPIO masks, AC97 register constants, Linux allocation/delay/mutex support, and parent card-info discovery. It integrates with the parent PCM device when assigning IEC958 control device IDs.

## Risks and Test Signals

Risks include shared GPIO corruption without save/restore, write-only STAC9744 cache drift, variant-specific GPIO pins for Prodigy LT/XT, conditional CS8415 absence, headphone amp read behavior using the standard Aureon bit, allocation cleanup after partial init failures, and subtle WM volume latch behavior. Test every card descriptor path, Aureon 5.1 side-control omission, Universe PCA9554 mux and label mapping, Prodigy LT/XT SPI pins, CS8415 controls, all WM8770 controls, headphone amp, AC97 cache controls, suspend/resume replay, and `snd-ice1724` build/link.
