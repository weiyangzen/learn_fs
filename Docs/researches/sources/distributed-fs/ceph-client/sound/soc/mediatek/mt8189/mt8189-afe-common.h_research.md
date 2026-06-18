# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-afe-common.h

## Purpose

`mt8189-afe-common.h` is the shared MT8189 AFE platform contract. It defines sample-rate encodings, MTKAIF protocol IDs, memory-interface and DAI IDs, interrupt IDs, audio clock-gate IDs, MCLK IDs, channel-merge IDs, the private per-device state structure, and DAI registration prototypes. MT8189 PCM, clock, and DAI implementation files include this header to share IDs and state layout.

## Important APIs, Types, and Data

The rate enums map ALSA rates to hardware encodings. `MTK_AFE_RATE_*` covers the common internal rate table including high-rate and 260 kHz variants. `MTK_AFE_IPM2P0_RATE_*` maps the newer IPM 2.0 hardware encodings with explicit hex values. Smaller `MTK_AFE_DAI_MEMIF_RATE_*` and `MTK_AFE_PCM_RATE_*` enums cover reduced-rate domains.

The MTKAIF protocol enum defines protocol 1, protocol 2, and protocol 2 clock phase 2. The large memif/DAI enum assigns IDs for download memifs, uplink memifs, ETDM input, HDMI, and non-memif DAIs such as ADDA, ADDA channel groups, AP DMIC, I2S in/out, PCM, TDM, and DPTX. `MT8189_DAI_NUM` sizes DAI-private arrays.

IRQ enums define normal MCU IRQ IDs `MT8189_IRQ_0` through selected IRQ 31 and a custom TDM IRQ namespace. Clock-gate enums define IDs consumed by clock helpers for `AUDIO_ENGEN_CON0` and `AUDIO_TOP_CON4` bits. MCLK IDs enumerate I2S, FMI2S, TDM MCLK, and TDM BCK clocks. `CM0`, `CM1`, and `CM_NUM` describe channel-merge state slots.

`struct mt8189_afe_private` is the central state object. It contains the clock-handle array, PMIC regmap, per-DAI private pointers, MTKAIF protocol/calibration/DMIC fields, ADDA vote/status booleans, MCLK rate cache, and channel-merge rate/channel fields. The file declares DAI registration entry points: `mt8189_dai_adda_register`, `mt8189_dai_i2s_register`, `mt8189_dai_pcm_register`, and `mt8189_dai_tdm_register`.

## Control Flow

The header itself has no executable control flow, but it defines the call graph glue. Platform probe allocates and attaches `struct mt8189_afe_private`, initializes clocks and regmaps, then invokes the DAI registration functions declared here. DAI and PCM code use the shared enum IDs to index memif data, IRQ data, DAI private storage, clock gates, and MCLK rates. Clock code uses the clock-gate and MCLK enums to map abstract driver requests to register masks and clock framework handles.

## State and Persistence

Runtime state persists for the life of the probed AFE device in `struct mt8189_afe_private`. `clk` is devm-owned and remains valid until device teardown. `pmic_regmap` points at PMIC register access. `dai_priv[]` stores per-DAI submodule state. MTKAIF calibration fields store chosen phases and cycles, while booleans track ADDA downlink/uplink/vote/max-volume status. `mck_rate[]` can cache requested MCLK rates across DAI operations. Channel-merge fields keep active rates and merged channel count.

No file-backed persistence exists. Any hardware state represented by these fields must be reinitialized after probe, reset, or resume according to platform PM behavior.

## Dependencies and Integration Points

The header includes Linux regmap, ALSA SoC, `mt8189-reg.h`, and the common MediaTek `mtk-base-afe.h`. It integrates every MT8189 source file in the directory: the Makefile compiles implementations that agree on these IDs; `mt8189-afe-clk.c` uses clock and private-state definitions; DAI files use memif/DAI/IRQ/rate IDs; machine drivers indirectly depend on the platform exposing the correct DAI names and capabilities.

The enum values also form internal ABI with static arrays in implementation files. For example, memif arrays are expected to be indexed by `MT8189_MEMIF_*`, DAI-private arrays by IDs below `MT8189_DAI_NUM`, and clock arrays by values from `mt8189-afe-clk.h`.

## Risks

The largest risk is enum drift. Adding, removing, or reordering IDs can corrupt indexing into arrays throughout the driver. Because many arrays are sized by terminal enum values, out-of-tree users or partially updated files can compile but misaddress state. `dai_priv` uses `void *`, so type safety is deferred to callers. Calibration arrays have fixed size 4 rather than an explicit MTKAIF channel enum, so related code must agree on channel count.

Shared booleans such as `is_adda_dl_on`, `is_adda_ul_on`, and `is_mt6363_vote` may need locking if manipulated from concurrent DAI paths. The header does not define synchronization rules. Rate enums must be mapped carefully; the standard, IPM2.0, memif, and PCM rate namespaces are not interchangeable even when names look similar.

## Test Signals

Compile tests should cover all MT8189 objects after any enum or struct change. Runtime signals include successful registration of every DAI ID, correct ALSA PCM exposure for all memifs, IRQ delivery for all configured IRQ IDs, successful clock/MCLK setup using private `clk` state, MTKAIF calibration persistence, ADDA vote transitions, and channel-merge operation. Static checks should verify array sizes and switch statements cover `MT8189_DAI_NUM`, `MT8189_MEMIF_NUM`, `MT8189_IRQ_NUM`, `MT8189_AUDIO_CG_NUM`, and `MT8189_MCK_NUM` where appropriate.
