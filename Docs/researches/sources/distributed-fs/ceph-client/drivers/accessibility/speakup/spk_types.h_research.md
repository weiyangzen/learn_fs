# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_types.h

## Purpose
Central Speakup data model for variables, per-console state, synth I/O callbacks, synth descriptors, highlight tracking, and global info.

## Important APIs, Types, And Functions
Defines `var_type_t`, variable operation modes, and `var_id_t`. Key structs include `spk_highlight_color_track`, `st_spk_t`, `st_var_header`, `num_var_t`, `punc_var_t`, `string_var_t`, `var_t`, `st_bits_data`, `synth_indexing`, `spk_io_ops`, `spk_synth`, and `speakup_info_t`. Macros map `spk_x`, `win_top`, and related names to current console state.

## Control Flow
No executable flow. Function pointers in `spk_io_ops` and `spk_synth` define driver callbacks for output, input, flush, probe, release, immediate output, catch-up, liveness, adjustment, receive bytes, and indexing.

## State And Persistence Behavior
Structs define the in-memory state held by core and drivers. `spk_synth.attributes` maps drivers into sysfs, and `spk_synth.dev` stores transport-specific state.

## Dependencies, Integration Points, Risks, And Test Signals
Included across Speakup and depends on kernel type, VT, lock, wait, I/O, and device headers. `var_id_t` ordering is ABI-like because keymaps depend on it. Test full build, sysfs variables, synth modules, per-console cursor/window state, and read-all indexing after changes.
