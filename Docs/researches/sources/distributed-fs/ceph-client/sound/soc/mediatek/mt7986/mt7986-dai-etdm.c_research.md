# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-dai-etdm.c

## Purpose

This file implements the MT7986 ETDM DAI used as the external audio interface, with DAPM routing between memif endpoints and ETDM pins, format negotiation, stream parameter programming, trigger control, and sub-DAI registration.

## Important APIs, Types, and Functions

- `struct mtk_dai_etdm_priv` stores BCLK/LRCLK inversion, slave mode, and wire format.
- `mt7986_etdm_rate_transform()` maps rates to ETDM-specific FS values.
- `get_etdm_wlen()` and `get_etdm_ch_fixup()` convert ALSA width/channels to hardware fields.
- `mtk_dai_etdm_startup()` / `shutdown()` gate bulk clocks and ETDM in/out top clocks.
- `mtk_dai_etdm_config()` writes ETDM IN/OUT control, relatch, clock-source, FS, and divider fields.
- `mtk_dai_etdm_set_fmt()` parses I2S/DSP_A/DSP_B, inversion, and master/slave flags.
- `mt7986_dai_etdm_register()` adds the DAI, widgets, and routes.

## Control Flow

Platform probe registers the ETDM sub-DAI. Machine-driver `dai_fmt` calls `set_fmt()`, which allocates DAI-private format state. Startup enables clocks and clears ETDM top powerdown bits. `hw_params()` accepts 8/12/16/24/32/48/96/192 kHz and configures both playback and capture sides with matching format fields. Trigger start/resume enables both ETDM IN5 and OUT5; stop/suspend disables both. Shutdown powers down ETDM top gates and disables clocks.

## State and Persistence Behavior

Format state persists in `afe_priv->dai_priv[MT7986_DAI_ETDM]` after `set_fmt()`. Hardware format/rate state persists in ETDM registers until reconfigured or suspended. No explicit locking protects repeated `set_fmt()` allocations, but devm ownership handles lifetime.

## Dependencies and Integration Points

Depends on MT7986 register fields, bitfield helpers, common AFE state, ASoC DAI format negotiation, and machine drivers that set `.dai_fmt` on the ETDM BE.

## Risks and Edge Cases

`bck_inv`, `lrck_inv`, and `slave_mode` are parsed but not currently written to ETDM inversion/master fields, so non-default formats may be accepted without effect. `hw_params()` configures both directions even for one-way streams. `set_fmt()` must run before `hw_params()` or `etdm_data` is NULL.

## Test Signals

Validate I2S playback/capture through WM8960, rejected unsupported rates such as 44.1 kHz despite advertised macro including 44.1-family rates, ETDM trigger enable bits, and behavior for inversion/master flags.
