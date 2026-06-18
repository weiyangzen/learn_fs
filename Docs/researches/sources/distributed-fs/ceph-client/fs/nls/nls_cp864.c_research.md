# sources/distributed-fs/ceph-client/fs/nls/nls_cp864.c

Purpose: Implements the Linux NLS module for DOS codepage 864, an Arabic codepage. It performs exact conversion between CP864 single-byte values and Unicode Arabic, Arabic presentation forms, Latin, and symbol code points for filesystem names.

Important APIs/types/functions: Defines `charset2uni[256]`, reverse pages `page00`, `page03`, `page06`, `page22`, `page25`, and `pagefe`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp864"`. `init_nls_cp864()` registers and `exit_nls_cp864()` unregisters the table.

Control flow: `uni2char()` uses Unicode high-byte dispatch, notably including page 06 for Arabic and page FE for presentation forms, then writes a single byte for exact nonzero entries. `char2uni()` maps one raw byte to Unicode and rejects zero. Module init/exit simply update the NLS registry.

State and persistence behavior: The conversion tables are immutable module data. There is no dynamic allocation or persistent storage; the only runtime state is NLS registration.

Dependencies and integration points: Uses standard Linux module and NLS APIs. Filesystem NLS users selecting `cp864` receive these conversion callbacks and byte case tables. Arabic shaping, joining, and bidi processing are not integration responsibilities of this file.

Risks: CP864 includes Arabic presentation-form mappings, so replacing those with normalized base Arabic characters would break exact round-trip behavior. The source contains several unmapped bytes; tests must preserve intentional holes. The module does not perform shaping or bidirectional reordering, only codepoint conversion.

Test signals: Verify registration as `cp864`, round-trip Arabic base letters, presentation form entries from page FE, Latin symbols, and box-drawing bytes. Confirm unmapped bytes/Unicode return `-EINVAL` and no-output-space returns `-ENAMETOOLONG`.
