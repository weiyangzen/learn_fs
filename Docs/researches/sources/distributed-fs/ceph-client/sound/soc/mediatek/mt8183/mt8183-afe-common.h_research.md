# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-afe-common.h

Purpose: provides shared MT8183 AFE IDs, IRQ IDs, MTKAIF protocol constants, MCLK IDs, private driver state, and cross-file function prototypes for the MT8183 ASoC platform.

Important APIs/types/functions: enumerates memifs `DL1`, `DL2`, `DL3`, `VUL12`, `VUL2`, `AWB`, `AWB2`, `MOD_DAI`, `HDMI`; DAIs `ADDA`, `PCM_1`, `PCM_2`, `I2S_0/1/2/3/5`, `TDM`, hostless loopback/speech; IRQs 0-8/11/12; MTKAIF protocol modes; MCLK IDs; `struct mt8183_afe_private` containing clock array, runtime PM bypass flag, per-DAI private pointers, MTKAIF calibration/DMIC fields, and MCK rates; prototypes for rate transforms, I2S sharing, and each DAI register callback.

Control flow: `mt8183-afe-pcm.c` allocates and owns `mt8183_afe_private`, uses enums to size memif/IRQ arrays, and invokes DAI register callbacks. DAI files store per-DAI state in `dai_priv`, use rate transform helpers, and read/write MTKAIF/DMIC state.

State and persistence: this header defines the long-lived private state layout. `dai_priv` entries are devm-allocated by DAI registration. MTKAIF calibration and DMIC flags persist for the device lifetime and affect ADDA capture configuration.

Dependencies and integration: includes ALSA SoC, Linux list/regmap, and MediaTek common AFE definitions. It is the coupling point between AFE core, clock control, and sub-DAI implementations.

Risks: enum ordering is ABI-like within the driver because arrays are indexed directly by IDs. `dai_priv` is a void pointer array, so type safety is manual. Adding/removing memifs or DAIs requires synchronized changes in memif tables, DAI drivers, register callbacks, and machine links.

Test signals: compile-time coverage across all MT8183 source files, probe-time memif/IRQ array sizing, DAI registration success for each callback, and audio route tests that exercise every DAI ID.
