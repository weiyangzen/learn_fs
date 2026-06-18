# sources/distributed-fs/ceph-client/fs/nls/nls_cp855.c

Purpose: Implements the Linux NLS translation module for DOS codepage 855, a Cyrillic codepage. It maps CP855 bytes to Unicode Cyrillic characters and back for legacy filesystem name handling.

Important APIs/types/functions: Provides `charset2uni[256]`, reverse pages `page00`, `page04`, `page21`, and `page25`, `page_uni2charset[256]`, byte case tables, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp855"`. `init_nls_cp855()` registers with the NLS layer, and `exit_nls_cp855()` unregisters.

Control flow: `uni2char()` checks output capacity, selects a reverse table using the Unicode high byte, and writes a single byte for a nonzero exact entry. `char2uni()` consumes one byte and returns the corresponding `wchar_t` unless the mapping is zero. The module init/exit paths contain no additional branching.

State and persistence behavior: Conversion state is entirely static and read-only. Runtime mutation is limited to the kernel NLS registry entry during the loaded module lifetime.

Dependencies and integration points: Uses `<linux/nls.h>` and module infrastructure. Filesystem drivers can request `cp855`; once loaded, the callbacks and Cyrillic case tables are used by generic NLS-aware filename conversion paths.

Risks: CP855's Cyrillic upper/lower pairs are byte-specific and differ from CP866, so using the wrong Cyrillic module changes both conversion and case folding. Exact-only conversion rejects unsupported Unicode and cannot normalize composed characters. The reverse tables use zero as an unmapped sentinel.

Test signals: Verify lookup by `cp855`, round-trip Cyrillic bytes across Unicode page 04, and test the encoded Cyrillic case pairs. Include error tests for missing output space, unmapped Unicode, and byte zero behavior.
