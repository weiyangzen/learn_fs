# sources/distributed-fs/ceph-client/fs/nls/nls_cp861.c

Purpose: Provides the Linux NLS module for DOS codepage 861, labeled Icelandic. It translates legacy CP861 bytes to Unicode and back for filesystem filename processing.

Important APIs/types/functions: Contains `charset2uni[256]`, reverse pages `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp861"`. `init_nls_cp861()` registers the table; `exit_nls_cp861()` unregisters it.

Control flow: The callbacks perform fixed one-byte conversions. `uni2char()` checks `boundlen`, looks up the Unicode page and low byte, and returns one output byte or an error. `char2uni()` performs the forward byte lookup and treats a zero result as invalid. The module lifecycle is linear NLS registration.

State and persistence behavior: No mutable data is kept in the conversion path. Static tables are module-local; registration in the NLS subsystem is the only runtime state.

Dependencies and integration points: Depends on kernel module and NLS APIs. It integrates with any filesystem using the kernel NLS layer and provides CP861-specific case folding for Icelandic letters plus common graphical symbols.

Risks: Icelandic letters such as eth/thorn must match CP861 byte positions; replacing with nearby CP437/CP865 tables would change filenames. Reverse tables cannot encode zero-valued mappings, and no Unicode normalization or fallback conversion is performed.

Test signals: Confirm registration under `cp861`, round-trip Icelandic-specific high-bit bytes, and verify ASCII/accented case folding. Include negative tests for unmapped Unicode pages and no output buffer capacity.
