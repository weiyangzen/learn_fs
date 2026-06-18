# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_sai.c

## Purpose
`fsl_sai.c` is the Freescale/NXP SAI CPU DAI driver for Linux ASoC. It binds SAI MMIO registers, clocks, IRQs, DMA parameters, pinctrl states, SoC variants, and ALSA DAI callbacks into playback and capture interfaces. It supports I2S, left-justified, DSP A/B, PDM-style DSD, TDM slot configuration, multi-dataline and multi-FIFO DMA, timestamp/bit-counter controls, runtime PM, and multiple i.MX/VF610 SAI revisions.

## Important APIs, Types, And Functions
The public integration surface is the platform driver `fsl_sai_driver`, matched by `fsl_sai_ids`, and the ASoC component `fsl_component`. The DAI templates expose a combined `sai-tx-rx` DAI plus split `sai-tx` and `sai-rx` DAIs, each backed by `fsl_sai_pcm_dai_ops`, `fsl_sai_pcm_dai_tx_ops`, or `fsl_sai_pcm_dai_rx_ops`.

Key callback functions are `fsl_sai_probe`, `fsl_sai_remove`, `fsl_sai_dai_probe`, `fsl_sai_startup`, `fsl_sai_set_dai_fmt*`, `fsl_sai_set_dai_sysclk`, `fsl_sai_set_dai_bclk_ratio`, `fsl_sai_set_dai_tdm_slot*`, `fsl_sai_hw_params`, `fsl_sai_hw_free`, and `fsl_sai_trigger`. Interrupt and PM logic is in `fsl_sai_isr`, `fsl_sai_runtime_suspend`, and `fsl_sai_runtime_resume`.

Important helpers include `fsl_sai_set_bclk` for MCLK/divider selection, `fsl_sai_read_dlcfg` for parsing `fsl,dataline`, `fsl_sai_check_version` for VERID/PARAM discovery, `fsl_sai_get_pins_state` for high-rate PCM/DSD pinctrl selection, and `fsl_sai_dir_is_synced` for determining which direction provides clocks in synchronous mode.

## Control Flow
Probe allocates `struct fsl_sai`, maps MMIO, configures the regmap defaults for either offset-0 or offset-8 register layouts, acquires the bus and MCLK clocks, gets optional PLL clocks, constrains rates from available clocks, detects multi-FIFO SDMA from `dmas`, parses dataline masks, requests the shared IRQ, copies the DAI templates, parses synchronous/asynchronous and MCLK-direction properties, initializes DMA addresses, enables runtime PM, reads hardware version data, optionally enables MCLK output, configures i.MX95 audio-mix mode through SCMI, registers the PCM DMA platform, and registers the component.

At DAI probe, both Tx and Rx paths are software-reset, FIFO watermarks are initialized from FIFO depth and maxburst, and ALSA DMA data is attached. `startup` applies EDMA period-size constraints and either the full SAI rate list in clock-consumer mode or clock-derived constrained rates in provider mode.

Format setup writes CR2/CR4 bit clock, frame clock, polarity, master/consumer, DSP, PDM, and bit-order fields. `hw_params` derives slot width, slots, pins/dataline type, BCLK, pinctrl state, MCLK divider, DMA FIFO address, multi-FIFO peripheral config, FIFO watermark, TRCE enabled dataline mask, CR4/CR5 frame and word layout, and channel mask registers. `trigger` enables FRDE, TERE, interrupt bits, and synchronized opposite direction when starting, and disables DMA request/interrupts, synchronized partners, TERE/BCE, FIFO reset, and software reset on stop.

## State And Persistence
Persistent driver state is in `struct fsl_sai`: regmap, bus and master clocks, PLL handles, selected MCLK IDs, `mclk_streams`, stream slots and widths, BCLK ratio, sync mode, consumer/provider mode, PDM/DSP flags, dataline config, pinctrl state, DMA params, SDMA peripheral config, version/parameter data, PM QoS request, and constrained-rate storage. Hardware register state is cached through regmap and restored across runtime PM. Runtime suspend disables active MCLKs and the bus clock, removes PM QoS when needed, and switches regmap cache-only on. Resume reenables clocks, resets Tx/Rx, syncs cached registers, and reasserts TERE for SoCs where MCLK generation depends on TERE.

## Dependencies And Integration Points
The file integrates with ALSA ASoC, DMAEngine PCM, `imx-pcm`, regmap, runtime PM, pinctrl, Linux clocks, optional system controller GPRs for i.MX6UL MCLK direction, SCMI i.MX misc controls for i.MX952 audio-mix routing, and SDMA peripheral configuration for multi-FIFO transfers. It includes `fsl_utils.h` for PLL rate constraints and runtime-PM-safe mixer controls used by timestamp kcontrols.

## Risks And Edge Cases
Clock selection is sensitive: provider mode must find a valid MCLK divisor, skip unsupported 1:1 ratios on older hardware, and handle synchronized directions that require programming the opposite CR2 register. Dataline masks from DT can reject channel layouts or enable non-successive FIFOs, and multi-FIFO DMA changes addresses, maxburst, and watermarks. PDM and high-rate PCM require matching pinctrl states. The `mclk_with_tere` path intentionally toggles frame-master bits around word-width programming to avoid frame-clock glitches. Runtime suspend/resume must keep `mclk_streams` and selected `mclk_id` coherent or clocks can be disabled/enabled on the wrong source. Shared IRQ handling only clears write-one-to-clear status bits masked by enabled IRQs.

## Test Signals
Useful test signals are probe success across each compatible string, successful regmap version reads on offset-8 parts, `aplay` and `arecord` for I2S provider and consumer modes, simultaneous Tx/Rx in synchronous and asynchronous modes, TDM slot masks, PDM/DSD rates, multi-FIFO DMA with multi-dataline channel counts, suspend/resume while a stream is configured, timestamp kcontrol reads under runtime PM, and absence of underrun/overflow debug messages from `fsl_sai_isr`.
