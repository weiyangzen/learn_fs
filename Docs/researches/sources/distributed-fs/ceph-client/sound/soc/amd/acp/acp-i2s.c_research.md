# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-i2s.c

## Purpose
`acp-i2s.c` implements generic ASoC CPU DAI operations for AMD ACP I2S/TDM controllers across Renoir, Rembrandt, ACP6.3, and ACP7.x style hardware. It sets format/TDM slots, programs sample resolution and master clock dividers, prepares ring/FIFO registers, and enables/disables stream interrupts.

## Important APIs, Types, And Functions
The exported object is `asoc_acp_cpu_dai_ops`. Important helpers include `acp_set_i2s_clk()`, `acp_i2s_set_fmt()`, `acp_i2s_set_tdm_slot()`, `acp_i2s_hwparams()`, `acp_i2s_prepare()`, `acp_i2s_startup()`, and `acp_i2s_trigger()`. It operates on `struct acp_chip_info`, `struct acp_resource`, and `struct acp_stream` from `amd.h`.

## Control Flow
Startup maps the DAI ID and stream direction to an IRQ bit, PTE offset, FIFO offset, and stream identity. `set_fmt()` switches between I2S and DSP_A/TDM mode. `set_tdm_slot()` validates slot width/count based on ACP generation and stores TX/RX format words for streams with matching DAI IDs. `hw_params()` translates sample format to hardware resolution, writes ITER/IRER sample length, writes TDM format if enabled, and computes LRCLK/BCLK dividers when SoC MCLK is present. Prepare configures DMA size, FIFO address/size, ring buffer address, and external interrupt mask. Trigger writes watermark/buffer size, optionally programs master clock, enables ITER/IRER and IER on start, and clears stream enable plus shared IERs on stop.

## State And Persistence
State persists in `acp_chip_info` arrays for TDM formats and transfer resolutions, `lrclk_div`, `bclk_div`, `tdm_mode`, and `acp_stream` fields such as `dai_id`, `irq_bit`, offsets, direction, and byte count. Hardware state persists in ACP I2STDM/BTTDM/HSTDM registers until stopped or reinitialized.

## Dependencies And Integration Points
The file depends on ASoC DAI callbacks, ACP register macros/resources from `amd.h`, stream allocation by the ACP PCM platform component, interrupt handling in `acp-legacy-common.c`, and platform drivers that register CPU DAIs using `asoc_acp_cpu_dai_ops`.

## Risks And Edge Cases
Generation-specific field layouts differ for ACP6.3/7.x versus older hardware. TDM slot settings are applied by scanning current streams, so order between stream startup and machine `set_tdm_slot()` matters. Some unsupported channel counts log errors but do not immediately return in one branch. Register address selection for ACP7.x uses different memory windows.

## Test Signals
Tests should cover I2S and DSP_A modes, slot widths 8/16/24/32, slot-count limits per generation, S16/S24/S32 rates and dividers, SP/BT/HS playback and capture prepare paths, trigger start/stop interrupt bits, and resume restoration of stored formats/resolutions.
