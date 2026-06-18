# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_aud2htx.c

## Purpose
`fsl_aud2htx.c` is the NXP AUD2HTX ASoC CPU DAI driver for routing audio data into HDMI transmit hardware. It provides a playback-only DAI, configures FIFO watermarks and DMA parameters, controls enable/DMA-enable bits on trigger, manages regmap cache and bus clock runtime PM, and registers a DMAengine PCM platform.

## Important APIs, Types, and Functions
- `fsl_aud2htx_trigger()` enables/disables the AUD2HTX block and DMA request generation on PCM trigger commands.
- `fsl_aud2htx_dai_probe()` configures DMA request threshold, masks interrupts, sets low/high watermarks, and attaches TX/RX DMA data to the DAI.
- `fsl_aud2htx_dai` exposes playback stream `CPU-Playback`, 1-8 channels, common HDMI audio rates from 32 kHz through 192 kHz, and formats from `FSL_AUD2HTX_FORMATS`.
- Regmap callbacks define readable, writable, volatile registers and defaults.
- `fsl_aud2htx_probe()` maps registers, initializes regmap, requests IRQ, obtains `bus` clock, sets TX DMA address/name/maxburst, enables runtime PM, registers DMAengine PCM, and registers the component/DAI.
- Runtime suspend/resume toggles regcache cache-only and the bus clock.

## Control Flow
Probe allocates private state, maps MMIO, initializes a MAPLE regmap, registers a placeholder IRQ handler, obtains the bus clock, initializes TX DMA parameters pointing at `AUD2HTX_WR`, sets drvdata, enables runtime PM, puts regmap into cache-only mode, and registers the platform and DAI. DAI probe then writes hardware defaults through regmap when the DAI is instantiated. Trigger start sets `AUD2HTX_CTRL_EN` and `AUD2HTX_CTRE_DE`; stop clears DMA enable then block enable.

Runtime resume enables the bus clock and syncs regmap cache to hardware; runtime suspend switches regmap cache-only and disables the clock. System sleep delegates to runtime PM force helpers.

## State and Persistence
Driver state is `struct fsl_aud2htx` with platform device, regmap, bus clock, and DMAengine DAI metadata. Register values persist logically through regmap cache across runtime suspend. There is no on-disk persistence.

## Dependencies and Integration Points
The driver depends on ASoC DAI/component APIs, DMAengine PCM registration, runtime PM, regmap MMIO, a DT compatible `fsl,imx8mp-aud2htx`, a `bus` clock, an IRQ resource, and a DMA channel named `tx`. Machine cards or graph cards connect its `CPU-Playback` stream to downstream HDMI/audio paths.

## Risks and Edge Cases
- The IRQ handler always returns handled and does not inspect or clear interrupt status; interrupts are masked by default, so enabling them later requires real handling.
- `dma_params_rx` is initialized into the DAI despite the DAI being playback-only and RX fields not being populated.
- Register writes in DAI probe depend on runtime PM/regcache behavior; if the device is not resumed by ASoC around probe, writes may remain cached until resume.
- Error paths disable runtime PM but do not need explicit regmap cleanup due to devm resources.

## Test Signals
- Probe and runtime resume should show no clock/regmap errors.
- Playback through HDMI should trigger enable bits, generate DMA requests below the low watermark, and stop cleanly.
- Runtime suspend/resume followed by playback validates regcache restore of watermark and mask configuration.
