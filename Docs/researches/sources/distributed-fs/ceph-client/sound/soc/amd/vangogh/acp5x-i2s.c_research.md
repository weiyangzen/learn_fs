# sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x-i2s.c

## Purpose
This is the Vangogh ACP5x CPU DAI driver for SP and HS I2S/TDM streams. It configures DAI format, master/slave clock mode, TDM slot format, sample resolution, master clock dividers, and stream start/stop registers.

## Important APIs, Types, And Functions
DAI callbacks are `acp5x_i2s_set_fmt()`, `acp5x_i2s_set_tdm_slot()`, `acp5x_i2s_hwparams()`, and `acp5x_i2s_trigger()`. Probe is `acp5x_dai_probe()`, and the DAI driver is `acp5x_i2s_dai`.

## Control Flow
The PCI parent creates `acp5x_i2s_playcap` platform devices for SP and HS register windows. `set_fmt` records I2S versus DSP_A/TDM and bit/frame clock provider mode. `hw_params` selects stream instance from card driver data, maps PCM format to sample length, optionally writes TDM format, and when in master mode computes BCLK/LRCLK dividers for supported sample rates and 16/32-bit formats. Trigger start writes period watermark, ring-buffer size, optional master clock generator, enables TX/RX register bit 0, and enables the instance IER. Trigger stop clears bit 0 and disables IER when both directions are idle.

## State And Persistence Behavior
Device state holds `tdm_mode`, `master_mode`, `tdm_fmt`, and MMIO base. Stream private data owned by the DMA component carries instance, resolution, byte count, and computed clock dividers. The probe defaults `master_mode` to enabled.

## Dependencies And Integration Points
It depends on `acp5x.h` for register definitions, helpers, data structures, and `acp5x_set_i2s_clk()`. It works with `acp5x-pcm-dma.c` for DMA setup and with `acp5x-mach.c` for card-level instance selection and codec constraints.

## Risks And Edge Cases
Master-mode divider tables only support S16_LE and S32_LE; S8/U8 formats are listed in the DAI but return `-EINVAL` in master clock setup when master mode is active. Supported DAI rates list 8..96 kHz, while divider code includes 192 kHz cases not advertised. The DAI assumes DMA private data exists before `hw_params` and trigger.

## Test Signals
Test SP and HS playback/capture, I2S and DSP_A modes, clock provider modes, 16- and 32-bit formats at each supported rate, invalid rates/formats, and trigger stop IER gating. Machine-driver tests should confirm correct instance selection for headset codec versus speaker amplifier paths.
