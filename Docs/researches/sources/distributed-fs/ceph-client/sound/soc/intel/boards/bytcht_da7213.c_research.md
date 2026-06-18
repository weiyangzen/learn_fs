# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_da7213.c

## Purpose
This machine driver supports Baytrail/Cherrytrail boards with Dialog DA7212/DA7213 codecs. It provides the DPCM card layout, SSP2 I2S setup, DA7213 clock/PLL programming, and ACPI codec-name fixups.

## Important APIs, Types, and Functions
`codec_fixup()` forces 48 kHz stereo S24_LE and configures the CPU SSP2 port as two-slot 24-bit I2S. `aif1_startup()` limits FEs to 48 kHz. `aif1_hw_params()` sets DA7213 sysclk from 19.2 MHz MCLK and starts the codec PLL in SRM mode to `DA7213_PLL_FREQ_OUT_98304000`. `aif1_hw_free()` stops the PLL by switching to MCLK/zero configuration. DAPM controls expose headphone, headset mic, onboard mic, and aux input.

## Control Flow and Integration
The DAI layout is two dynamic FEs (`media-cpu-dai`, `deepbuffer-cpu-dai`) plus one no-PCM `SSP2-Codec` BE to `da7213-hifi`. Probe finds the ACPI codec instance from `mach->id`, rewrites the codec name, applies platform-name fixups, switches naming for SOF parent devices, sets SOF PM ops when needed, registers the card, and stores it as platform data.

## State, Persistence, and Dependencies
Static mutable state includes the codec name buffer and DAI link codec pointer. Runtime hardware state is the DA7213 sysclk/PLL state and SSP2 format. Dependencies include ACPI, `sst-mfld-platform`, Dialog DA7213 codec APIs, and Atom DPCM link indices.

## Risks and Test Signals
Risks include PLL start/stop imbalance if stream teardown paths change, hard failure when ACPI codec lookup fails, and global link mutation limiting multi-instance safety. Test signals include successful `devm_snd_soc_register_card()`, FE/deep-buffer playback at 48 kHz, DA7213 PLL programming messages only on real errors, audio capture/playback through SSP2, and clean PLL shutdown on stream free.
