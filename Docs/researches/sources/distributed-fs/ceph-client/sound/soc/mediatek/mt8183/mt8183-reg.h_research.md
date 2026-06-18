# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-reg.h

## Purpose

`mt8183-reg.h` is the MT8183 audio front end register map and bitfield catalog. It has no executable control flow; its purpose is to give the MT8183 ASoC drivers stable symbolic names for MMIO offsets, register maximums, IRQ status masks, mux input/output bit indexes, and register-field shift/mask pairs.

## Important APIs, Types, and Data

The public surface is entirely preprocessor definitions. The first block defines register offsets for audio top gates, AFE core control, I2S, PCM, TDM, ADDA, MTKAIF, ASRC, gain, sidetone, sine generator, connection matrix, memif base/current/end pointers, MSB address extensions, IRQ counters/status/clear registers, and debug/monitor registers. `AFE_MAX_REGISTER` is set to `AFE_GENERAL2_ASRC_2CH_CON13`, and `AFE_IRQ_STATUS_BITS` covers the 13 MCU IRQ status bits used by the MT8183 driver.

The second block defines field triplets such as `*_SFT`, `*_MASK`, and `*_MASK_SFT`. These are consumed by `regmap_update_bits()` and table-driven structures in MT8183 code. High-use groups include `AFE_DAC_CON0/1/2` memif enable, mono, and mode fields; `AFE_MEMIF_HD_MODE`, `AFE_MEMIF_HDALIGN`, `AFE_MEMIF_MSB`, `AFE_MEMIF_MINLEN/MAXLEN/PBUF_SIZE`; `AFE_IRQ_MCU_CON0/1/2` and `AFE_IRQ_MCU_CLR`; ADDA and MTKAIF fields; and PCM/TDM/I2S format and enable fields.

## Control Flow and State

There are no functions, allocation, locks, or persistent variables. Runtime state lives in hardware registers addressed by these macros and in driver structures that include this header. The correctness contract is static: offset constants must match the SoC register layout, and field masks must match hardware bit positions.

## Dependencies and Integration Points

This header is included by MT8183 AFE, clock, ADDA, I2S, PCM, and TDM implementation files. It also indirectly defines the register vocabulary for regmap volatile checks, memif metadata tables, DAPM route controls, IRQ handling, runtime suspend/resume register programming, and ALSA hw_params paths.

## Risks

The file has no type safety. A wrong shift, mask, or offset compiles cleanly and can misprogram hardware, corrupt DMA pointers, break interrupt acknowledgement, or route audio through the wrong connection matrix endpoint. Some macro names are reused across I2S register groups, so including code must be careful to use the intended register-specific field. Because `AFE_MAX_REGISTER` bounds regmap access/cache coverage, extending the register map without updating it would hide later registers from regmap.

## Test Signals

Build coverage should catch missing macro names but not semantic offset mistakes. Runtime test signals are ASoC card probe, regmap initialization, successful playback/capture on DL/VUL/AWB paths, IRQ period callbacks, suspend/resume with regcache sync, I2S/PCM/TDM loopback, ADDA/MTKAIF capture/playback, and debugfs/regmap traces confirming writes hit expected offsets.
