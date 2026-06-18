# sources/distributed-fs/ceph-client/fs/nls/nls_cp857.c

Purpose: Supplies the Linux NLS module for DOS codepage 857, the Turkish single-byte codepage. It converts between CP857 on-disk bytes and Unicode for filesystem names.

Important APIs/types/functions: Defines `charset2uni[256]`, reverse pages `page00`, `page01`, and `page25`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp857"`. Registry lifecycle is handled by `init_nls_cp857()` and `exit_nls_cp857()`.

Control flow: `uni2char()` returns one byte after a successful reverse-page lookup and returns `-ENAMETOOLONG` or `-EINVAL` for no capacity or no exact mapping. `char2uni()` directly indexes `charset2uni` and returns one byte consumed if nonzero. Module load/unload register and unregister the static table.

State and persistence behavior: The module has immutable generated tables and no persistent state. Its only mutable effect is registration in the global NLS table list while loaded.

Dependencies and integration points: Integrates with Linux filesystem NLS consumers through `struct nls_table`. Turkish-specific Latin mappings and byte-level upper/lower tables are supplied to callers that need case-insensitive comparisons in this legacy encoding.

Risks: Turkish dotted/dotless I behavior is represented only by static byte tables, not full locale-aware Unicode casing. The source has several unmapped `0x0000` entries in `charset2uni`, so tests must distinguish intentional holes from accidental omissions. No best-fit conversion exists for characters outside CP857.

Test signals: Confirm `cp857` registration, round-trip Turkish letters such as dotted/dotless I and related Latin Extended values, and verify `charset2lower`/`charset2upper` pairs. Negative tests should include unmapped byte holes, unmapped Unicode, and zero output length.
