# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/keyhelp.c Research

## Purpose
`keyhelp.c` implements Speakup's interactive help mode. It maps Speakup command functions to their assigned keys, speaks key names and command descriptions, and supports browsing help by initial letter or cursor keys.

## Important APIs And Control Flow
The external entry point is `spk_handle_help(struct vc_data *vc, u_char type, u_char ch, u_short key)`. Internal tables include `funcvals[]`, `key_offsets[MAXFUNCS]`, `key_data[MAXKEYS]`, `letter_offsets[26]`, `masks[]`, `state_tbl`, `cur_item`, and `nstates`. On first use, `help_init()` derives first-letter offsets from localized function names and locates the generated key state table in `spk_our_keys`. Entering help sets `spk_special_handler`, speaks instructions, and calls `build_key_data()`. Space exits, letters jump to command groups, cursor up/down moves through functions, and recognized keys or commands speak either the key name or command description.

## State And Persistence
State is static and volatile: cached letter offsets, built key offsets/data, current item, state table pointer, and state count. It is rebuilt on help entry to reflect remapped keys. `spk_special_handler` in broader Speakup state persists while help mode is active.

## Dependencies And Integration Points
The file depends on keyboard type constants, generated `spk_our_keys`, Speakup command constants, i18n messages from `spk_msg_get()`, and speech output through `synth_printf()`.

## Risks
`funcvals[]` must remain ordered with `MSG_FUNCNAMES_START` entries; drift gives wrong descriptions. `MAXFUNCS` and `MAXKEYS` are fixed limits, and `build_key_data()` can lose mappings if offsets exceed `MAXKEYS`. Localized function names affect first-letter navigation and can collide or not fit the `a` to `z` flow.

## Test Signals
Exercise entering/exiting help, letter jumps, up/down navigation, key lookup for assigned and unassigned commands, remapping followed by help rebuild, localized message sets, and boundary cases where generated keymaps approach static table limits.
