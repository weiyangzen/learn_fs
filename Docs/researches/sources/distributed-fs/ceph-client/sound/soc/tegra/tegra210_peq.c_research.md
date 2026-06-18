# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra210_peq.c

## Purpose
Implements the Tegra210 parametric equalizer (PEQ) sub-block used by OPE. It provides child regmap initialization, default coefficient/shift RAM programming, ALSA controls for enable/stage count and per-channel biquad RAM, plus save/restore helpers for OPE runtime PM.

## Important APIs, Types, And Functions
Exported functions are `tegra210_peq_regmap_init()`, `tegra210_peq_component_init()`, `tegra210_peq_save()`, and `tegra210_peq_restore()`. Internal RAM helpers `tegra210_peq_read_ram()` and `tegra210_peq_write_ram()` sequence CFG RAM control/data registers. ALSA handlers `tegra210_peq_get/put()` cover scalar CFG bits, while `tegra210_peq_ram_get/put()` expose gain and shift RAM as signed integer arrays.

## Control Flow
`tegra210_peq_regmap_init()` finds the `equalizer` DT child, maps MMIO, initializes the `peq` regmap, and leaves it cache-only. `tegra210_peq_component_init()` powers the parent, disables PEQ by default, sets the default number of biquad stages, writes default gain and shift tables for all eight channels, drops PM, and adds controls. Save/restore loop over all channels and read/write gain plus shift RAM through the AHUB RAM access registers.

## State And Persistence
Default coefficients are static arrays. A file-scope `biquad_coeff_buffer` is reused by ALSA get/put handlers. OPE runtime PM calls `tegra210_peq_save()` before cache-only suspend and `tegra210_peq_restore()` after regcache resume. Regmap marks RAM data registers precious and volatile to avoid unsafe cache assumptions.

## Dependencies And Integration Points
Depends on OPE's `struct tegra210_ope`, the shared `TEGRA_SOC_BYTES_EXT()` macro, platform DT child resources, runtime PM, and regmap. PEQ controls are added to the OPE ASoC component rather than a standalone component.

## Risks
`biquad_coeff_buffer` is global, so concurrent control operations could race without explicit locking beyond ALSA/control serialization assumptions. `tegra210_peq_save()` and restore receive one gain and one shift buffer, then loop over all channels while overwriting/reusing the same buffers; this appears to preserve only the last channel's values across suspend unless all channels are expected to share identical coefficients. `tegra210_peq_ram_get()` reports integer arrays but uses `value.integer.value[]`; large arrays should be checked against ALSA control element limits.

## Test Signals
Verify DT child discovery, ALSA control counts for eight gain and eight shift parameter arrays, RAM reads/writes through controls, stage-count bounds, active/bypass behavior, and suspend/resume preservation of distinct per-channel coefficients.
