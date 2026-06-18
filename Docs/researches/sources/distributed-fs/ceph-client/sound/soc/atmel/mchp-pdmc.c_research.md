# sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-pdmc.c

## Purpose
Microchip Pulse Density Microphone Controller capture-only DAI. It converts PDM microphone streams into PCM capture, configures PDM channel mapping from device tree, manages SINC/audio-filter parameters, exposes channel-map ALSA controls, and registers dmaengine PCM with a post-processing hook.

## Important APIs, Types, And Functions
- `struct mchp_pdmc` stores microphone mapping, regmap, pclk/gclk, DMA address data, enabled-channel mask, suspended IRQ mask, startup delay, mic count, SINC order, audio filter state, and `busy_stream`.
- ALSA controls: `"Audio Filter"`, `"SINC Filter Order"`, and `"Capture Channel Map"` through `mchp_pdmc_*_get/put` handlers.
- DAI ops: `mchp_pdmc_set_fmt`, `mchp_pdmc_startup`, `mchp_pdmc_hw_params`, `mchp_pdmc_trigger`, `mchp_pdmc_pcm_new`, and `mchp_pdmc_dai_probe`.
- `mchp_pdmc_dt_init()` parses `microchip,mic-pos` and optional `microchip,startup-delay-us`, rejecting invalid DS/edge combinations and duplicate microphones.
- `mchp_pdmc_process()` clears the channel index bits in DMA samples.
- Runtime PM handlers cache-only the regmap and enable/disable pclk/gclk.

## Control Flow
Probe parses microphone topology, maps registers, installs IRQ, initializes default audio filter and SINC order, enables runtime PM, registers dmaengine PCM and the capture DAI. Startup resets the IP and constrains channel count to the declared mic count. `hw_params` checks channel count, marks the stream busy, chooses the closest gclk OSR from the allowed set, programs MR/CFGR with filter, SINC order, DMA chunk, and mic edge/data selections, and sets DMA maxburst. Trigger start enables the selected PDM channels, waits the microphone startup delay, drains RHR and clears interrupts, then enables overrun/underrun interrupts. Stop/suspend disables interrupts and clears PDMCEN.

## State And Persistence
Control values are kept in `struct mchp_pdmc`; `busy_stream` prevents changing audio filter and SINC order while capture is configured. Channel-map state is stored in the `mchp_pdmc_std_chmaps` entries and reflected into CFGR. Regcache preserves register programming across runtime suspend/resume, but no state is persisted beyond the device lifetime.

## Dependencies And Integration Points
Uses `dt-bindings/sound/microchip,pdmc.h`, ASoC controls, dmaengine PCM, regmap, clk, runtime PM, and OF. The DAI accepts only PDM format and requires the CPU DAI to be bit-clock provider. DMA integration uses `snd_dmaengine_pcm_config.process` to scrub metadata bits.

## Risks
The control path writes CFGR in channel-map `get`, so status reads can change hardware. `busy_stream` is set in `hw_params` but is only cleared on remove in this file, so filter controls may remain busy after normal stream teardown unless higher-level component lifecycle resets them elsewhere. Gclk retuning temporarily disables the clock, making runtime-PM sequencing important. Startup delay defaults to 150 ms and directly affects capture latency. Incorrect `microchip,mic-pos` ordering will produce swapped channel maps even when capture works.

## Test Signals
Validate DT parsing failures for odd/duplicate/out-of-range `microchip,mic-pos`, capture at supported rates with 1 to 4 mics, channel-map ALSA control round trips, overrun/underrun IRQ warnings, suspend/resume with regcache sync, and DMA output with channel index byte cleared.
