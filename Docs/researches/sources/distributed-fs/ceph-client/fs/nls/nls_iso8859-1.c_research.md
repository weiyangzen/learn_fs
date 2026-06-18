# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-1.c

## Purpose

This generated NLS module registers the ISO 8859-1 / Latin-1 single-byte charset. It maps each byte directly to the same Unicode code point in `U+0000..U+00FF` and provides exact reverse mappings for filesystems that need Western European filename conversion.

## Important APIs, Types, and Functions

`charset2uni[256]` is a one-entry-per-byte `wchar_t` decode table. `page00[256]` is the reverse Unicode page for `U+00xx`, and `page_uni2charset[256]` points only page 0 at `page00`. `charset2lower[256]` and `charset2upper[256]` fold ASCII and Latin-1 uppercase/lowercase pairs. `uni2char()` encodes one byte from the reverse page; `char2uni()` decodes one byte from `charset2uni`. The `struct nls_table` is registered as `iso8859-1`.

## Control Flow

`uni2char()` rejects zero output space with `-ENAMETOOLONG`, indexes the reverse page with the high and low bytes of `wchar_t`, writes a single output byte when the table entry is nonzero, and returns `-EINVAL` for unmapped code points. `char2uni()` indexes `charset2uni[*rawstring]`, rejects `0x0000`, and returns one consumed byte.

## State and Persistence Behavior

All tables are `static const` and read-only. The only module state is registration in the NLS registry between `init_nls_iso8859_1()` and `exit_nls_iso8859_1()`. Mapping changes affect persisted filenames on filesystems mounted with this charset.

## Dependencies and Integration Points

The file depends on `linux/nls.h`, errno definitions, and module infrastructure. Filesystems use it through the NLS registry and the callbacks in `struct nls_table`.

## Risks

The `char2uni()` zero check means byte `0x00` is treated as invalid in this NLS callback even though the decode table stores `U+0000`; callers must not expect embedded NUL filename characters. `uni2char()` also uses a zero reverse-table entry as "unmapped", so `U+0000` is not encodable through this path. Case-folding tables are byte-level and not full Unicode normalization.

## Test Signals

Build/load/unload the module, verify all nonzero `U+0001..U+00FF` values round-trip, verify `U+0100` returns `-EINVAL`, verify zero-length output returns `-ENAMETOOLONG`, and check ASCII plus accented Latin-1 case-folding entries.
