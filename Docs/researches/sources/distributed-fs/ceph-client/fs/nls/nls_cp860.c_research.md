# sources/distributed-fs/ceph-client/fs/nls/nls_cp860.c

Purpose: Implements the Linux NLS module for DOS codepage 860, labeled Portuguese. It supports exact single-byte translation between CP860 bytes and Unicode for legacy filesystem filename conversion.

Important APIs/types/functions: The module defines `charset2uni[256]`, reverse pages `page00`, `page03`, `page20`, `page22`, `page23`, and `page25`, `page_uni2charset[256]`, byte case-fold arrays, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp860"`. Lifecycle hooks are `init_nls_cp860()` and `exit_nls_cp860()`.

Control flow: `uni2char()` validates output length, performs high-byte reverse-page dispatch, emits one byte for an exact nonzero mapping, or fails with `-EINVAL`. `char2uni()` maps one byte through `charset2uni` and rejects zero. Init and exit are direct calls into the NLS registry.

State and persistence behavior: All data is static and immutable. There is no allocation, no persisted filesystem state, and no per-caller context; only module registration state changes.

Dependencies and integration points: Uses Linux module/NLS headers and error codes. Filesystem NLS users select this table with `cp860`; case folding is supplied through the CP860 `charset2lower` and `charset2upper` arrays.

Risks: CP860 differs from CP437/CP850 in Portuguese accented letters while retaining many graphical symbols; confusing these codepages can produce visually plausible but incorrect filenames. Exact lookup rejects missing Unicode, and NUL cannot be represented because zero is the unmapped marker.

Test signals: Round-trip Portuguese accented entries, ASCII, and graphical symbols. Validate `cp860` lookup, `-ENAMETOOLONG` on no output space, `-EINVAL` for unmapped Unicode, and byte-level case folding for Portuguese-specific pairs.
