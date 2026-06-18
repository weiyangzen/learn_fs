# sources/distributed-fs/ceph-client/fs/nls/nls_cp863.c

Purpose: Provides the Linux NLS module for DOS codepage 863, labeled Canadian French. It maps CP863 bytes used in legacy filenames to Unicode and back with exact generated tables.

Important APIs/types/functions: Supplies `charset2uni[256]`, reverse pages `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25`, `page_uni2charset[256]`, case-fold arrays, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp863"`. Module lifecycle is `init_nls_cp863()` and `exit_nls_cp863()`.

Control flow: `uni2char()` dispatches by Unicode high byte, requires a nonzero exact reverse mapping, and writes one output byte. `char2uni()` consumes one byte through `charset2uni` and fails on zero. Registration and unregistration are direct calls to NLS helpers.

State and persistence behavior: Static const tables are the only conversion data. The module keeps no per-filesystem state and writes nothing to persistent storage.

Dependencies and integration points: Integrates with the Linux NLS registry and filesystem callers through `struct nls_table`. Its case tables handle CP863 Canadian French accented byte pairs and ASCII.

Risks: CP863 repositions several French accented characters compared with CP850/CP437, so using the wrong table causes reversible but semantically wrong names. Exact-only reverse lookup fails for decomposed accents and other Unicode equivalents. NUL and unmapped table holes are invalid.

Test signals: Confirm `cp863` registration, round-trip Canadian French accented bytes, and test box-drawing/symbol entries inherited from DOS layouts. Validate expected failures for decomposed accent sequences and unmapped Unicode.
