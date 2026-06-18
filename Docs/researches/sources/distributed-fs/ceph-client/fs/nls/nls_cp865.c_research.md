# sources/distributed-fs/ceph-client/fs/nls/nls_cp865.c

Purpose: Provides the Linux NLS module for DOS codepage 865, labeled Norwegian and Danish. It converts legacy CP865 filename bytes to Unicode and back.

Important APIs/types/functions: Contains `charset2uni[256]`, reverse pages `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp865"`. `init_nls_cp865()` and `exit_nls_cp865()` implement module registry lifecycle.

Control flow: The callbacks are single-byte exact lookups. `uni2char()` validates output room, finds a reverse page from the Unicode high byte, and writes one byte if the table entry is nonzero. `char2uni()` reads one byte and rejects zero-valued mappings. Load/unload only register and unregister `table`.

State and persistence behavior: No conversion state changes at runtime. Static tables live in module memory; external mutable state is limited to the NLS registry entry.

Dependencies and integration points: Integrates with Linux filesystems through `<linux/nls.h>` and `struct nls_table`. Case folding covers ASCII plus CP865 Nordic letters used in legacy DOS filenames.

Risks: CP865 is close to CP437 but differs in Nordic letters, making copy/paste table changes risky. No normalization, decomposition, or fallback is performed. Reverse lookup cannot encode byte zero because zero denotes missing entries.

Test signals: Confirm `cp865` lookup, round-trip Norwegian/Danish letters and DOS graphical symbols, and validate upper/lower byte folds. Include negative tests for unmapped Unicode and zero output capacity.
