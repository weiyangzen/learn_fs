# sources/distributed-fs/ceph-client/fs/nls/nls_cp874.c

Purpose: Implements the Linux NLS module for Thai CP874/TIS-620. It provides exact single-byte conversion between Thai legacy bytes and Unicode for filesystem names and exposes `tis-620` as an alias.

Important APIs/types/functions: Defines `charset2uni[256]`, reverse pages `page00`, `page0e`, and `page20`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp874"` and `.alias = "tis-620"`. Lifecycle hooks are `init_nls_cp874()` and `exit_nls_cp874()`. Metadata includes `MODULE_DESCRIPTION("NLS Thai charset (CP874, TIS-620)")`, `MODULE_LICENSE("Dual BSD/GPL")`, and `MODULE_ALIAS_NLS(tis-620)`.

Control flow: `uni2char()` checks output capacity, selects reverse page 00, 0E, or 20 by Unicode high byte, and writes one byte for exact nonzero mappings. `char2uni()` maps one input byte and rejects zero. Loading registers the table under the main charset and alias; unloading unregisters it.

State and persistence behavior: The code uses immutable static mapping arrays and no dynamic state. Persistence is limited to the transient NLS registry entry while the module is loaded.

Dependencies and integration points: Uses Linux module, NLS, and errno APIs. Filesystems can request either `cp874` or `tis-620` and receive the same callbacks. Thai has no uppercase/lowercase distinction, so the case tables primarily preserve bytes and ASCII behavior rather than language-specific folding.

Risks: CP874 has many intentionally unmapped bytes in the 0x80-0x9f and trailing ranges; treating those as valid would change error behavior. The `tis-620` alias is part of the integration contract and should not be dropped. Thai normalization, combining-mark ordering, and rendering are outside this byte conversion module.

Test signals: Verify both `cp874` and `tis-620` lookup/module alias behavior, round-trip Thai characters in Unicode page 0E, and check special page 20 punctuation such as the ellipsis entry. Negative tests should cover unmapped byte holes, unsupported Unicode, and zero output length.
