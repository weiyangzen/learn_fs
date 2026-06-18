# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-reg.h

## Purpose
Register-definition header for the MT8195 ASoC audio front end. It gives the MT8195 platform drivers symbolic offsets for the AFE, ASYS, IRQ, memif, DMIC, ADDA, ETDM, GASRC, SPDIF, DPTX, secure-mask, connection-matrix, and SRAM register spaces, plus field macros for common bit programming.

## APIs, Types, and Functions
This header exports preprocessor constants only. Important address groups include `AUDIO_TOP_CON*`, `ASYS_IRQ*`, `AFE_IRQ*`, `AFE_DAC_CON*`, `AFE_DL*`, `AFE_UL*`, `AFE_CONN*`, `AFE_SECURE_MASK_CONN*`, `AFE_DMIC*`, `ETDM_*`, `AFE_GASRC*`, `AFE_ADDA_*`, and `AFE_DPTX_CON`. `AFE_SRAM_BASE`, `AFE_SRAM_SIZE`, and `AFE_MAX_REGISTER` describe hardware range limits. Field helpers use `BIT()` and `GENMASK()` for top timing, PCM interface configuration, multi-channel microphone capture, MTKAIF, DMIC source configuration, ETDM formatting, DPTX channel enable, and ADDA downlink/uplink controls.

## Control Flow, State, and Persistence
There is no executable control flow or persistent C state in this file. Runtime behavior emerges when MT8195 AFE drivers include these constants and use regmap/MMIO operations to program hardware. The register names encode persistence domains: memif base/end/current registers persist DMA buffer addresses while streams run, connection-matrix and secure-mask registers persist routing/security policy until rewritten or reset, and IRQ/timing/control registers persist stream clocking and interrupt behavior across active runtime power windows.

## Dependencies and Integration
Consumers depend on Linux bitfield helpers made available by included kernel headers in the including compilation units. The file integrates with MT8195 machine/platform DAI, memif, clock, DMIC, ADDA, ETDM, SPDIF, and ASRC code by providing the single source of truth for offsets and masks used in `regmap_update_bits()`, `regmap_write()`, and register backup lists. `AFE_MAX_REGISTER` is suitable for regmap range validation.

## Risks and Test Signals
The main risk is silent hardware misprogramming from a wrong offset, mask, shift, typo, or SoC-revision mismatch; headers like this rarely fail at compile time when a bit definition is semantically wrong. Large repeated ranges such as `AFE_CONN*`, `AFE_SECURE_MASK_CONN*`, and `AFE_GASRC*` are especially sensitive to off-by-one address drift. Test signals are successful MT8195 probe with regmap range checks, working playback/capture on every memif, correct IRQ period accounting, DAPM route toggling through connection registers, suspend/resume register restore, DMIC/ADDA/ETDM/SPDIF/DPTX hardware validation, and register-dump comparison against the MT8195 datasheet or vendor reference.
