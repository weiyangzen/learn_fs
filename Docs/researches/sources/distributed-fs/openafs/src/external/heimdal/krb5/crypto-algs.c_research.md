# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-algs.c

Purpose: central registry for compiled-in Heimdal checksum and encryption algorithms.

Important APIs/types/functions: exports `_krb5_checksum_types[]`, `_krb5_num_checksums`, `_krb5_etypes[]`, and `_krb5_num_etypes`. The arrays reference descriptors defined in the AES, DES, DES3, RC4, null, and common crypto files. Conditional entries are controlled by `HEIM_WEAK_CRYPTO`, `HEIMDAL_SMALLER`, and `DES3_OLD_ENCTYPE`.

Control flow: lookup functions in `crypto.c` linearly scan these arrays for enctype or checksum identifiers. Preference-sensitive APIs such as deprecated keytype-to-enctype mapping iterate over `_krb5_etypes`; comments note the encryption list is in reverse preference order for non-pseudo enctypes.

State and persistence behavior: exposes global mutable descriptor pointers and counts. Enabling/disabling algorithms mutates flags inside descriptor records, not these arrays.

Dependencies and integration points: included by the krb5 crypto library build; it connects all algorithm-specific files to generic APIs such as `krb5_enctype_valid()`, `krb5_create_checksum()`, `krb5_crypto_init()`, and weak-crypto toggles.

Risks: compile-time macros materially change supported algorithms. Weak DES algorithms are absent unless `HEIM_WEAK_CRYPTO` is set, while some legacy DES3 entries are included unless smaller builds suppress them. Table order affects compatibility and negotiation behavior.

Test signals: enumerate supported enctypes/checksums under each build profile, validate string-to-enctype aliases, weak-crypto enable/disable behavior, and absence/presence of legacy entries.
