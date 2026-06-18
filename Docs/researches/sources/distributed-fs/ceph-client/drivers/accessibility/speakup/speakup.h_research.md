# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup.h

## Purpose
Main internal Speakup header for version constants, character classification bits, public cross-file prototypes, and shared extern state.

## Important APIs, Types, And Functions
Defines `SPEAKUP_VERSION`, `KEY_MAP_VER`, keymap/description sizes, chartab flags, and `IS_*` macros. Declares synth, sysfs, varhandler, buffer, selection, devsynth, UTF-8, fake-keyboard, and thread APIs plus many shared globals.

## Control Flow
No code runs here; it defines call contracts between core, sysfs, transport, synth, selection, and fake-keyboard components.

## State And Persistence Behavior
Extern declarations expose mutable in-memory state for current synth, consoles, keymaps, punctuation, chartab, character descriptions, and boot settings.

## Dependencies, Integration Points, Risks, And Test Signals
Includes `spk_types.h` and `i18n.h`. Risks are broad ABI-style coupling: changing chartab bits or `KEY_MAP_VER` affects keymap parsing and speech behavior. Test full module build, keymap compatibility, sysfs config, selection, and synth selection.
