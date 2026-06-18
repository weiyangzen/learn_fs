# sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_msp_dai.c

## Purpose
ASoC CPU DAI driver for Ux500 MSP I2S/PCM controllers. It translates ASoC DAI format, TDM, sysclk, hw_params, startup, prepare, trigger, and shutdown operations into low-level MSP configuration and generic DMAengine PCM registration.

## Important APIs, Types, and Functions
Important helpers include `setup_pcm_multichan()`, `setup_frameper()`, `setup_pcm_framing()`, `setup_clocking()`, `setup_pcm_protdesc()`, `setup_i2s_protdesc()`, `setup_msp_config()`, and DAI callbacks `ux500_msp_dai_startup()`, `ux500_msp_dai_shutdown()`, `ux500_msp_dai_prepare()`, `ux500_msp_dai_hw_params()`, `ux500_msp_dai_set_dai_fmt()`, `ux500_msp_dai_set_tdm_slot()`, `ux500_msp_dai_set_dai_sysclk()`, `ux500_msp_dai_trigger()`, and `ux500_msp_dai_of_probe()`. Platform callbacks are `ux500_msp_drv_probe()` and `ux500_msp_drv_remove()`.

## Control Flow, State, and Persistence
Probe allocates `ux500_msp_i2s_drvdata`, initializes default format/slots/masks/master clock, gets `v-ape`, PRCMU QoS, clocks, low-level MSP MMIO state, registers one CPU DAI, then registers the DMAengine PCM platform. Startup enables the regulator and clocks. `hw_params()` constrains channels according to I2S versus DSP/TDM slot masks. `prepare()` builds `ux500_msp_config`, opens/programs the MSP, and raises APE OPP if generated bit clock exceeds 19.2 MHz. Trigger delegates start/stop to low-level MSP enable/disable. Shutdown closes the direction, lowers QoS, disables clocks, and disables the regulator.

## Dependencies and Integration Points
Depends on ALSA SoC DAI and DMAengine helpers, Linux regulators/clocks/platform/OF, DB8500 PRCMU QoS, low-level `ux500_msp_i2s.c`, and `ux500_pcm.c`. MOP500 calls its DAI ops through standard ASoC runtime operations.

## Risks and Test Signals
Risks include `setup_msp_config()` return ignored in `prepare()`, format/inversion acceptance mismatches between set_fmt and setup_clocking, only 16-bit TDM slots supported, PRCMU QoS name inconsistency (`ux500_msp_i2s` vs `ux500-msp-i2s`), and global low-level state allowing only one TX and one RX direction. Test signals are regulator/clock balance, I2S and DSP_A/B format setup, 1/2/8/16-slot TDM masks, DMA address initialization, channel constraints from masks, high-bitclock OPP changes, and repeated prepare/trigger/shutdown cycles.
