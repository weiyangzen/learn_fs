# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/varhandlers.c

## Purpose
`varhandlers.c` maps Speakup variable IDs to names, storage, and setter behavior. It supports proc/sysfs-style variable registration, numeric and string updates, punctuation mask updates, character-table keyword decoding, and simple parser helpers used by Speakup configuration paths.

## Important APIs, Types, And Functions
The central tables are `var_headers[]`, `var_ptrs[MAXVARS]`, and `punc_vars[]`. Public or shared functions include `spk_chartab_get_value()`, `speakup_register_var()`, `speakup_unregister_var()`, `spk_get_var_header()`, `spk_var_header_by_name()`, `spk_get_var()`, `spk_get_punc_var()`, `spk_set_num_var()`, `spk_set_string_var()`, `spk_set_mask_bits()`, `spk_strlwr()`, and `spk_s2uchar()`.

## Control Flow
The first `speakup_register_var()` call initializes `var_ptrs` from `var_headers`, clears header data pointers, attaches the passed `struct var_t`, and applies default numeric/time/string values. Numeric updates in `spk_set_num_var()` interpret `how` as default, set, increment, decrement, or new-default operation, range-check the value, update an optional backing integer, adjust `spk_punc_mask` for punctuation level, apply multiplier/offset, optionally let the active synth consume the adjustment, and finally emit a synth command for synth-specific variables. String updates copy defaults or user data into the registered backing buffer. `spk_set_mask_bits()` validates punctuation/delimiter input against `spk_chartab` and sets or clears class bits.

## State And Persistence
State is stored in the registered `struct var_t` objects, header `data` pointers, global Speakup settings such as `spk_punc_mask`, `spk_chartab`, and synth command side effects. It is in-memory kernel state; user-visible persistence depends on the surrounding Speakup variable interfaces.

## Dependencies And Integration Points
The file depends on `spk_types.h`, `spk_priv.h`, `speakup.h`, kernel ctype helpers, timing conversion through `msecs_to_jiffies()`, active synth output via `synth_printf()`, and shared punctuation data such as `spk_punc_info`, `spk_punc_masks`, and `spk_chartab`.

## Risks
`spk_var_header_by_name()` assumes `var_ptrs` has been initialized before use; calling it too early can dereference NULL table entries. `spk_set_num_var()` formats into 32-byte buffers or `spk_pitch_buff`, so synth format strings and value strings must remain bounded. `spk_set_string_var()` uses `strcpy()` after only checking `len <= MAXVARLEN`, so backing buffers must match that contract. Mask updates rely on the correctness of global character classification data.

## Test Signals
Test signals include registration/unregistration ordering, all numeric update modes and range failures, time variable jiffy conversion, synth command emission for rate/pitch/volume-style variables, string default restore behavior, punctuation mask validation, and early lookup behavior before registration.
