# sources/distributed-fs/ceph-client/fs/nls/nls_cp866.c

Purpose: Implements the Linux NLS module for DOS codepage 866, labeled Cyrillic/Russian. It converts single-byte CP866 filenames to Unicode and back using exact mapping tables.

Important APIs/types/functions: Defines `charset2uni[256]`, reverse pages `page00`, `page04`, `page21`, `page22`, and `page25`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp866"`. `init_nls_cp866()` registers the table and `exit_nls_cp866()` unregisters it.

Control flow: `uni2char()` checks for at least one output byte, selects the reverse table by Unicode high byte, and returns one byte for exact entries. Missing entries return `-EINVAL`. `char2uni()` maps one byte through `charset2uni` and fails on zero. Module lifecycle is standard NLS registration.

State and persistence behavior: The module has no mutable conversion state and persists nothing. Its only stateful effect is that the kernel can resolve `cp866` while the module is loaded.

Dependencies and integration points: Uses Linux module infrastructure and NLS APIs. Filesystem code uses the callbacks for CP866 names, with Cyrillic upper/lower folding in byte tables.

Risks: CP866 and CP855 are both Cyrillic but not interchangeable; byte positions and case folding differ. Exact mapping rejects unsupported Unicode and does not normalize Cyrillic variants. `char2uni()` relies on caller input buffer validity.

Test signals: Round-trip Russian Cyrillic uppercase and lowercase bytes, verify `charset2upper`/`charset2lower`, and confirm page 04 reverse mappings. Negative tests should cover unmapped Unicode pages, no output space, and byte zero.
