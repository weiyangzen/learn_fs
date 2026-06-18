# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-dai-pcm.c

## Purpose

This file implements MT6797 modem PCM interface DAIs (`PCM 1` and `PCM 2`) with DAPM mixers/routes and hardware parameter programming for PCM interface registers.

## Important APIs, Types, and Functions

- Local enums encode PCM format, mode, sync, clock, AFIFO, BT mode, word length, and enable values.
- DAPM mixers route ADDA_UL and DL memif channels to PCM playback widgets.
- `mtk_dai_pcm_hw_params()` maps stream rate to a PCM mode and programs `PCM_INTF_CON1` or `PCM2_INTF_CON`.
- `mtk_dai_pcm_driver[]` defines symmetric playback/capture DAIs for 8/16/32/48 kHz.
- `mt6797_dai_pcm_register()` appends widgets/routes/drivers to `afe->sub_dais`.

## Control Flow

Registration occurs during platform probe. On `hw_params`, the function skips reprogramming if either playback or capture widget is already active, preserving symmetric active configuration. Otherwise it builds the PCM control word for the selected DAI and writes all fields except enable bit, which is controlled by DAPM supplies.

## State and Persistence Behavior

No private state. Hardware PCM interface configuration remains in registers while the DAI is active. Active DAPM widget flags are used as the guard against reconfiguration.

## Dependencies and Integration Points

Uses MT6797 interconnection/register macros, `mt6797_rate_transform()`, ASoC DAPM, and machine BE links named `PCM 1` and `PCM 2`.

## Risks and Edge Cases

The active-widget guard can preserve stale format if a second stream asks for a conflicting rate; symmetric flags should prevent this, but route-level behavior depends on ASoC ordering. PCM1 is configured as slave/internal modem and PCM2 has a different bit layout, so shared changes are risky.

## Test Signals

Run PCM1/PCM2 playback and capture at all four advertised rates, test simultaneous symmetric streams, and trace writes to `PCM_INTF_CON1`/`PCM2_INTF_CON`.
