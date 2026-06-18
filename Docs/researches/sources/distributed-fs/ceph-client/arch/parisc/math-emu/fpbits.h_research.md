# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fpbits.h

Purpose: provides portable bitfield extraction, signed extraction, masking, and deposit macros for the PA-RISC floating-point emulator. It abstracts the emulator's convention that bit 0 is the most significant bit of a 32-bit word.

Important APIs and types: `HOSTWDSZ` defaults to 32. `Bitfield_extract(start, length, object)` returns an unsigned field; `Bitfield_signed_extract` sign-extends; `Bitfield_mask` isolates a field in place; `Bitfield_deposit` clears and inserts a value into a field.

Control flow: this is macro-only code. All behavior expands inline at call sites in `float.h` and related format-specific headers. The macros compute shifts from `HOSTWDSZ`, `start`, and `length`, then combine masks and shifted values.

State and persistence: no runtime state is maintained. The only persistent contract is the source-level preprocessor API, which affects every floating-point field accessor compiled from the emulator headers.

Dependencies and integration: included indirectly by format helpers that name sign, exponent, mantissa, condition, and status fields. The file assumes unsigned arithmetic and a word size at least large enough for the requested fields.

Risks: macro arguments may be evaluated more than once in `Bitfield_deposit` via `object`, so callers must avoid side effects. Invalid `length` or `start` values can produce undefined shifts. The macros encode a PA-RISC bit numbering convention that differs from normal little-endian mental models.

Test signals: compile-time and unit-level checks should verify extraction and deposit for sign, exponent, mantissa, condition fields, all-zero and all-one masks, signed high-bit fields, and host builds that override `HOSTWDSZ`.
