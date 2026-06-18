# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-encoders.h

## Purpose
Declares changelog record encoder APIs and low-level macros for storing the type marker plus GFID in ASCII or binary form.

## APIs, Types, and Functions
`CHANGELOG_STORE_ASCII()` writes mapped record type and textual GFID. `CHANGELOG_STORE_BINARY()` writes mapped type and raw `uuid_t`. The header declares optional-record converter/free helpers and the main `changelog_encode_binary()`, `changelog_encode_ascii()`, and `changelog_encode_change()` routines.

## Control Flow, State, and Persistence
The macros increment caller-owned offsets using `CHANGELOG_FILL_BUFFER()`. Persistent format decisions are delegated to the selected encoder mode in `changelog_priv_t`.

## Dependencies and Integration
Includes `changelog-helpers.h` for record structures, type maps, and buffer operations. Used by encoder implementation and snapshot logging helper code.

## Risks and Test Signals
Risks include macro argument naming inconsistency (`buf` parameter but `buffer` use), unchecked destination capacity, and ABI compatibility with libgfchangelog decoders. Test signals are compile coverage of macro expansions and decoder compatibility tests for both encoding modes.
