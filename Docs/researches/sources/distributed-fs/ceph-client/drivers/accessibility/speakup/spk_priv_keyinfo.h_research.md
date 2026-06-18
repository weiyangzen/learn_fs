# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_priv_keyinfo.h

## Purpose
Defines private numeric IDs for Speakup key actions used by keymaps, keyboard dispatch, and keymap generation.

## Important APIs, Types, And Functions
Contains constants for `SPK_KEY`, review commands, cut/paste, speech kill, windows, help/lock/cursor/read-all, edit-bit commands, `SPKUP_MAX_FUNC`, and variable inc/dec command ranges such as `VAR_START` and `FIRST_SET_VAR`.

## Control Flow
No code runs. `main.c` uses these values to index `spkup_handler[]` and decide whether a mapped key invokes a function or variable adjustment. `makemapdata.c` parses the defines.

## State And Persistence Behavior
No state, but numeric stability is persistent ABI for generated/default keymap data.

## Dependencies, Integration Points, Risks, And Test Signals
Included by `spk_priv.h` and consumed by keymap tooling. Risks are renumbering or reordering constants without updating handler arrays and generated maps. Test regenerated maps, default keymap load, every command binding, and variable inc/dec mapping.
