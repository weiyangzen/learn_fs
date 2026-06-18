# sources/distributed-fs/ceph-client/fs/nls/nls_cp775.c

Purpose: Provides the Linux NLS module for DOS codepage 775, used for Baltic Rim character data. It translates single-byte CP775 filesystem names to Unicode and back with exact generated tables.

Important APIs/types/functions: Defines `charset2uni[256]`, reverse lookup pages `page00`, `page01`, `page20`, `page22`, and `page25`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp775"`. `init_nls_cp775()` and `exit_nls_cp775()` register and unregister the table.

Control flow: `uni2char()` performs one-byte output conversion by checking `boundlen`, dispatching through `page_uni2charset` by Unicode high byte, and requiring a nonzero reverse entry. `char2uni()` reads one raw byte, translates through `charset2uni`, and fails on zero. Load/unload is linear registration logic.

State and persistence behavior: There is no mutable conversion state. The static mapping arrays and table live for the module lifetime; external state is only the NLS registry entry while loaded.

Dependencies and integration points: Integrates with kernel filesystems through `struct nls_table` and the NLS registry APIs in `<linux/nls.h>`. Its case tables support CP775-aware filename folding for Baltic Latin letters as well as ASCII.

Risks: Exact table semantics mean characters outside CP775 return `-EINVAL`, with no transliteration. The reverse mapping cannot encode byte `0x00` because zero marks missing entries. Case folding is byte-table based and should not be treated as full Unicode case mapping.

Test signals: Build and load the codepage module, confirm lookup by `cp775`, and run byte round-trips for Baltic accented letters, Latin-1 symbols, box-drawing characters, and ASCII. Include failure checks for unmapped Unicode, `boundlen == 0`, and case-fold expectations for Baltic-specific upper/lower byte pairs.
