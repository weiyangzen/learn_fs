# sources/distributed-fs/ceph-client/fs/nls/nls_cp850.c

Purpose: Implements the Linux NLS module for DOS codepage 850, labeled Europe in the module description. It supports exact conversion between CP850 bytes and Unicode for legacy filesystem names.

Important APIs/types/functions: The file supplies `charset2uni[256]`, reverse pages `page00`, `page01`, `page20`, and `page25`, `page_uni2charset[256]`, byte case tables, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp850"`. `init_nls_cp850()` registers the table and `exit_nls_cp850()` unregisters it.

Control flow: The conversion callbacks are fixed-width single-byte lookups. `uni2char()` checks output room, chooses a Unicode page table, writes one byte for exact hits, and returns `-EINVAL` for holes. `char2uni()` maps `*rawstring` through `charset2uni` and treats zero as invalid. Module entry and exit only add/remove the table from the NLS registry.

State and persistence behavior: All mappings are static const data. No allocation or persistent writes occur; the only stateful effect is registration of the `cp850` NLS table during module lifetime.

Dependencies and integration points: Uses kernel module/NLS headers and error codes. Filesystems use this table when `cp850` is selected for on-disk names. `charset2lower` and `charset2upper` encode CP850-specific Latin accented case folding.

Risks: CP850 overlaps with CP437 in box-drawing regions but differs in extended Latin letters, so accidental table substitution can silently corrupt names. The implementation has no fallback for unmappable Unicode and no normalization. `char2uni()` relies on caller-provided input length validity.

Test signals: Verify `cp850` registration, round-trip all mapped high-bit European Latin bytes, and compare known CP850-specific letters against expected Unicode values. Confirm unmapped Unicode returns `-EINVAL`, zero output space returns `-ENAMETOOLONG`, and case tables preserve ASCII plus accented pairs.
