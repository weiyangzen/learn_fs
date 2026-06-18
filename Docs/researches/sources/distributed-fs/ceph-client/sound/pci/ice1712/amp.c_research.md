# sources/distributed-fs/ceph-client/sound/pci/ice1712/amp.c

## Purpose

This file provides VT1724 board support for Advanced Micro Peripherals AUDIO2000 and Chaintech AV-710 class cards. It supplies card descriptors and minimal chip/control initialization for the shared Envy24HT driver, including optional WM8728 programming on AV-710.

## Important APIs, Types, and Functions

`wm_put()` writes a WM8728 register over VT1724 I2C using `snd_vt1724_write_i2c()`. `snd_vt1724_amp_init()` sets total DAC/ADC counts and initializes AV-710's extra WM8728 codec when detected. `snd_vt1724_amp_add_controls()` adjusts a VT1616 AC97 register bit for output routing when AC97 exists. `snd_vt1724_amp_cards[]` exports Chaintech AV-710 and AMP Ltd AUDIO2000 `struct snd_ice1712_card_info` descriptors.

## Control Flow

The parent ICE1724 driver selects a descriptor by subvendor, then calls `chip_init` and `build_controls`. Initialization sets six DACs and two ADCs, and for AV-710 writes WM8728 attenuation and I2S format registers. Control-build adjustment clears bit `0x8000` in AC97 register `0x5a` through a cached AC97 write.

## State, Dependencies, Risks, and Tests

The file allocates no private state. It mutates `ice->num_total_dacs`, `ice->num_total_adcs`, the external WM8728, and an AC97 cache register. It depends on the Envy24HT parent, AC97 helpers, and VT1724 I2C. Risks include AV-710/AUDIO2000 shared IDs, unsupported AV-710 extra WM8728 mixer controls, and silent no-op behavior without AC97. Test descriptor matching, DAC/ADC counts, AV-710 I2C writes, AC97 `0x5a` update, and playback routing.
