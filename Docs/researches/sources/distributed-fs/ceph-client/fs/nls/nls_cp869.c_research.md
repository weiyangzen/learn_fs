# sources/distributed-fs/ceph-client/fs/nls/nls_cp869.c

Purpose: Provides the Linux NLS module for DOS codepage 869, a Greek codepage. It maps between CP869 bytes and Unicode for legacy filesystem filename conversion.

Important APIs/types/functions: Supplies `charset2uni[256]`, reverse pages `page00`, `page03`, `page20`, and `page25`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp869"`. Lifecycle hooks are `init_nls_cp869()` and `exit_nls_cp869()`.

Control flow: `uni2char()` performs capacity checking, high-byte reverse-page dispatch, nonzero entry validation, and one-byte output. `char2uni()` maps one byte to Unicode and rejects zero. Module entry/exit add and remove the NLS table.

State and persistence behavior: Static generated data is immutable. No heap state, per-mount context, or persistent data is maintained.

Dependencies and integration points: Integrates with the Linux NLS registry through `register_nls()` and `unregister_nls()`. Filesystems selecting `cp869` use these callbacks and Greek/ASCII byte case folding tables.

Risks: The table contains multiple unmapped high-bit byte positions, so exhaustive tests must allow intentional `0x0000` holes. CP869 differs from CP737 in Greek layout and symbols; using one for the other corrupts round-trip conversion. No context-sensitive final sigma or Unicode normalization is performed.

Test signals: Validate `cp869` registration, round-trip mapped Greek letters and punctuation, and assert `-EINVAL` for intentional byte holes or unsupported Unicode. Check ASCII and Greek case-fold table entries plus `boundlen <= 0` behavior.
