# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-null.c

Purpose: defines disabled null encryption and checksum descriptors used as sentinel or compatibility entries.

Important APIs/types/functions: `keytype_null` declares a zero-length key type. `NONE_checksum()` is a no-op checksum function. `_krb5_checksum_none` exports `CKSUMTYPE_NONE`. `NULL_encrypt()` is a no-op encryption function. `_krb5_enctype_null` exports `ETYPE_NULL` with `F_DISABLED`.

Control flow: generic lookup can find the null descriptors, but validation and crypto initialization reject the disabled enctype unless flags are changed. If invoked directly through descriptors, checksum and encryption return success without mutating data.

State and persistence behavior: no mutable state except the descriptor flags that can be changed by generic enable/disable functions.

Dependencies and integration points: participates in `_krb5_checksum_types[]` and `_krb5_etypes[]` as a marker. Used by APIs that default missing mappings to `ETYPE_NULL`.

Risks: accidentally enabling null encryption would remove confidentiality and integrity. The checksum size is zero, so callers must handle empty trailers correctly.

Test signals: validation should reject `ETYPE_NULL` by default, lookup should still resolve the descriptor, and null checksum size should remain zero.
