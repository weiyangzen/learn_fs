<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2764-quirks.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2764-quirks.h

## Purpose

This private header contains TAS2764/SN012776 quirk sequences, primarily for Apple-derived behavior. It supplements `tas2764.c` with undocumented or board-specific register writes for noise gate, VBAT/PVDD conversion, DAC modulator reset, thermal threshold handling, hidden-page writes, and a special shutdown sequence.

## Important APIs, types, and functions

The header defines quirk bit flags such as `TAS2764_NOISE_GATE_DISABLE`, `TAS2764_CONV_VBAT_PVDD_MODE`, `TAS2764_DMOD_RST`, `TAS2764_UNK_SEQ0`, `TAS2764_APPLE_UNK_SEQ1`, `TAS2764_APPLE_UNK_SEQ2`, `TAS2764_THERMAL_TH1_DISABLE`, and `TAS2764_SHUTDOWN_DANCE`. Each maps to `struct reg_sequence` arrays consumed by `regmap_multi_reg_write()`. `tas2764_do_quirky_pwr_ctrl_change()` wraps transitions to shutdown with pre/post hidden-page writes. `tas2764_quirk_init_sequences[]` indexes initialization sequences by bit position.

## Control flow

At compile time `ENABLED_APPLE_QUIRKS` enables the lower six quirk bits, while the shutdown dance bit is defined but not included by that mask. `tas2764_apply_init_quirks()` in `tas2764.c` iterates the sequence table and applies entries whose bit is enabled. Power-control updates call `tas2764_do_quirky_pwr_ctrl_change()` only when `TAS2764_SHUTDOWN_DANCE` is enabled.

## State and persistence behavior

The header itself stores no runtime state, but its sequences write persistent hardware registers, including undocumented hidden pages. The power-control helper reads current power state from the component before deciding whether to perform the shutdown dance.

## Dependencies and integration points

It depends on `linux/regmap.h` and `tas2764.h`, and it is included inside `tas2764.c` after `struct tas2764_priv` is defined. The helper uses `tas2764->component` and `tas2764->regmap`, so it is tightly coupled to that implementation.

## Risks and test signals

Risks are high because several writes are explicitly undocumented or unknown, the enabled mask is compile-time rather than DT-configured, and bit/table ordering must remain consistent. Test signals include SN012776 probe success, no regmap errors while applying init sequences, clean power-down/up without pops or hangs, thermal/fault behavior matching target hardware, and regression checks with plain `ti,tas2764` devices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2764-quirks.h -->
