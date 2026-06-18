# sources/distributed-fs/ceph-client/include/linux/kbd_diacr.h

## Purpose
Declares the keyboard accent/diacritic composition table used by virtual terminal keyboard handling.

## Important APIs, Types, And Functions
Exports `accent_table[]` of `struct kbdiacruc` and `accent_table_size`. The `kbdiacruc` type comes from `linux/kd.h`.

## Control Flow
The header has no logic. Keyboard translation code consults the table when composing dead-key accent sequences into Unicode characters.

## State And Persistence
The table is global kernel data. Its contents persist for the lifetime of the kernel and may be changed by keyboard map loading paths elsewhere.

## Dependencies And Integration Points
Depends on `linux/kd.h`. Integrates with VT keyboard translation, keymaps, and ioctls that configure accent mappings.

## Risks
Incorrect table size or contents can cause failed or wrong character composition. Consumers must bound iteration by `accent_table_size`.

## Test Signals
VT keyboard tests should cover dead-key composition, keymap loading, Unicode mode, invalid composition fallback, and table bounds.
