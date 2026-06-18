# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-interconnection.h

## Purpose

`mt8186-interconnection.h` defines MT8186 AFE input-port indices used by DAPM interconnection controls. The definitions map logical sources such as I2S channels, ADDA uplink channels, DL memory interfaces, gain outputs, SRC outputs, and TDM input channels to bit positions in `AFE_CONN*` registers. The complete 69-line header was read.

## Important APIs, Types, and Functions

There are no functions or types. Important macro families are low input indices `I_I2S0_CH*`, `I_ADDA_UL_CH*`, `I_DL*_CH*`, `I_PCM_*`, `I_GAIN*_OUT_CH*`, and high input indices represented as offsets from `I_32_OFFSET`, including `I_CONNSYS_I2S_CH*`, `I_SRC_*_OUT_CH*`, `I_DL4` through `I_DL8`, and `I_TDM_IN_CH1` through `I_TDM_IN_CH8`.

## Control Flow

The header has no runtime control flow. ASoC DAI files compile these macros into `SOC_DAPM_SINGLE_AUTODISABLE()` controls. At runtime, those controls set or clear the corresponding AFE connection bit when DAPM routes are activated.

## State and Persistence Behavior

No state is stored in this file. The macro values become register bit positions in DAPM controls; the resulting connection state is held by the AFE regmap and ALSA control/DAPM state.

## Dependencies and Integration Points

The header is included by MT8186 DAI files including hardware gain, I2S, PCM, SRC, and TDM paths. It depends only on its include guard. Its values must match `AFE_CONN*` and `AFE_CONN*_1` register layouts from `mt8186-reg.h` and the SoC hardware interconnect matrix.

## Risks and Edge Cases

Incorrect bit values silently route audio to the wrong source or no source. Some aliases intentionally overlap, such as `I_DL12_CH3` using the same bit as `I_DL1_CH1`, so consumers must understand the associated connection register context. High-port definitions subtract `I_32_OFFSET`; using them with a non-`*_1` register or using low-port values with a high register would address the wrong bit.

## Test Signals

Route-level tests should toggle each mixer switch and inspect the expected `AFE_CONN*` bit. Audio loopback tests can verify DL, ADDA, gain, SRC, CONNSYS, and TDM paths. Static review should compare this file with MT8186 hardware register documentation and with every `SOC_DAPM_SINGLE_AUTODISABLE()` use.
