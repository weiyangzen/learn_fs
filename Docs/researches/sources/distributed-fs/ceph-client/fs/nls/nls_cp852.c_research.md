# sources/distributed-fs/ceph-client/fs/nls/nls_cp852.c

Purpose: Provides the Linux NLS module for DOS codepage 852, covering Central and Eastern European Latin scripts. It is an exact single-byte conversion table for legacy filesystem filename encoding.

Important APIs/types/functions: Defines `charset2uni[256]`, reverse pages `page00`, `page01`, `page02`, and `page25`, `page_uni2charset[256]`, `charset2lower[256]`, `charset2upper[256]`, conversion callbacks `uni2char()` and `char2uni()`, and `struct nls_table table` with `.charset = "cp852"`. `init_nls_cp852()` and `exit_nls_cp852()` handle NLS registry lifecycle.

Control flow: `uni2char()` uses the Unicode high byte to choose a reverse page, then the low byte for a single output byte. It returns `-ENAMETOOLONG` if output capacity is zero and `-EINVAL` for missing mappings. `char2uni()` performs the forward lookup and rejects zero. Module load and unload call the standard register/unregister helpers.

State and persistence behavior: Static tables are immutable. The file keeps no dynamic state and persists nothing. The only externally visible state is whether the `cp852` table is currently registered.

Dependencies and integration points: Depends on Linux module and NLS APIs. It plugs into filesystem name conversion through `struct nls_table`, and the case folding arrays encode CP852-specific Central/Eastern European upper/lower byte pairs.

Risks: CP852 uses Latin Extended-A/B mappings, so stale or incorrectly generated `page01`/`page02` reverse tables can cause asymmetric conversion. Byte-level case folding is not a substitute for Unicode locale-sensitive behavior. Unmapped characters fail instead of being approximated.

Test signals: Exercise registration as `cp852`, round-trip Czech/Polish/Hungarian-style accented letters present in the high-bit table, and verify page coverage for Unicode pages 00, 01, 02, and 25. Negative tests should cover unmapped Cyrillic/Greek inputs, insufficient output length, and known case-fold pairs.
