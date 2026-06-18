# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-interconnection.h

## Purpose

`mt8189-interconnection.h` defines the input-port bit positions used by MT8189 AFE connection registers. The DAI files use these macros in `SOC_DAPM_SINGLE_AUTODISABLE()` mixer controls to connect internal producers such as DL memifs, ADDA UL channels, DMICs, I2S inputs, PCM capture, gain blocks, and SRC outputs to consumer widgets.

## Important APIs, Types, And Data

The header exports only preprocessor constants. It has include guards and no functions, structs, or runtime state. Input ports below 32 are encoded directly, including CONNSYS I2S, gain outputs, STF, ADDA UL channels, proximity UL, and DMIC channels. For connection register banks representing input indexes at 32, 64, 128, and 192 or above, it defines bank offsets (`I_32_OFFSET`, `I_64_OFFSET`, `I_128_OFFSET`, `I_192_OFFSET`) and then subtracts those offsets to produce the bit position used in the corresponding `AFE_CONNxxx_n` register word. Examples include `I_DL0_CH1`, `I_DL_24CH_CH8`, `I_DL24_CH2`, `I_PCM_0_CAP_CH1`, `I_I2SIN1_CH2`, and `I_SRC_4_OUT_CH2`.

## Control Flow

There is no executable control flow. Its definitions are compiled into the static DAPM mixer tables in `mt8189-afe-pcm.c`, `mt8189-dai-adda.c`, `mt8189-dai-i2s.c`, and `mt8189-dai-pcm.c`. At runtime, ALSA control changes set or clear bits in AFE connection registers using these constants.

## State And Persistence

The header has no state and no persistence behavior. Persistence of the bits selected by these constants is handled by the regmap and DAPM controls in the C files that reference the macros.

## Dependencies And Integration Points

The constants must match the MT8189 hardware interconnect matrix and the register bank layout in `mt8189-afe-common.h`. They are an integration contract shared by every DAPM route that uses an `AFE_CONN*` register. Any mismatch affects audio routing even when clocks, DAIs, and memifs are otherwise configured correctly.

## Risks

Because many macros intentionally subtract a bank offset, the same numeric bit position can represent different absolute hardware input indexes depending on the connection register bank. Using a macro with the wrong `AFE_CONNxxx_n` bank can silently route the wrong source. The header contains no compile-time validation against hardware tables, so copy/paste mistakes in DAPM mixers are the main risk. Several C files have large route tables, increasing the chance of pairing a readable control label with an incorrect `I_*` bit macro.

## Test Signals

The primary tests are route-level audio loopback and DAPM control validation. For each mixer control, toggling the control should flip the intended bit in the intended `AFE_CONN*` register and produce audio from the named source. Static review should compare every `I_*` use against the MT8189 interconnect matrix and ensure the register bank suffix (`_0`, `_1`, `_2`, `_4`, `_6`) matches the macro offset group.
