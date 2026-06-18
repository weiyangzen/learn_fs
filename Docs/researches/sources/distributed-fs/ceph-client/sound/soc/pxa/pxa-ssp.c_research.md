# sources/distributed-fs/ceph-client/sound/soc/pxa/pxa-ssp.c

Purpose: implements the PXA2xx/PXA3xx SSP ASoC CPU DAI, including clock source/PLL control, I2S/DSP/TDM formatting, DMA parameters, runtime trigger, and suspend/resume register save/restore.

Important APIs/types/functions: private `struct ssp_priv` stores the requested `ssp_device`, optional external clock, sysclk, DAI format, and PM register snapshots. DAI ops include `pxa_ssp_set_dai_sysclk`, `pxa_ssp_set_dai_fmt`, `pxa_ssp_set_dai_tdm_slot`, `pxa_ssp_set_dai_tristate`, `pxa_ssp_hw_params`, `pxa_ssp_trigger`, probe/remove, startup/shutdown.

Control flow: DAI probe requests the SSP by DT phandle or legacy ID and optional extclk. Startup enables clocks, disables SSP when first active, allocates per-substream DMA data, and sets channel names. hw_params sets DMA width/burst, applies deferred DAI format if inactive, configures data size, PLL/dividers, I2S PSP timing, and validates TDM slots. Trigger toggles TX/RX service bits and SSP enable based on ALSA trigger commands.

State and persistence: SSP hardware registers hold active configuration; `ssp_priv` tracks desired and configured format to avoid redundant reprogramming. PM saves SSCR0/SSCR1/SSTO/SSPSP while inactive or active.

Dependencies and integration: uses PXA SSP core APIs (`pxa_ssp_request*`, read/write helpers), `sound/pxa2xx-lib` PCM component callbacks, DMAEngine PCM data, optional DT compatible `mrvl,pxa-ssp-dai`, and local `pxa-ssp.h`.

Risks: format changes are only safe while inactive; active hw_params returns without reconfiguration. Network/TDM mode requires slot masks or fails. Clocking differs by SSP type, and PXA3xx dithered clock paths need careful validation. Busy-waiting on SSSR can hang if hardware misbehaves.

Test signals: DT and legacy probe, I2S/DSP_A/DSP_B formats, master/slave combinations, TDM slot setup, 16/32-bit DMA widths, suspend/resume with active and inactive streams, and no DMA data leaks across startup failures.
