<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/oid_registry.h -->
# sources/distributed-fs/ceph-client/include/linux/oid_registry.h

## Purpose
This header defines the kernel's ASN.1 object identifier registry enum and lookup/parse/format declarations used by certificate, crypto, key, Kerberos, Authenticode, TPM, and security parsers.

## Important APIs, types, and functions
`enum OID` lists recognized OIDs, with comments containing dotted numeric forms consumed by `build_OID_registry.pl`; `OID__NR` is the unknown/sentinel value. APIs are `look_up_OID()`, `parse_OID()`, and `sprint_oid()`.

## Control flow
ASN.1 parsers pass DER OID bytes to `look_up_OID()` or `parse_OID()` to map known encodings to enum values, then switch on the enum to select algorithms or semantic fields. `sprint_oid()` formats an OID for diagnostics.

## State and persistence
The registry is compile-time generated/static data. There is no runtime mutable state. The enum ordering and specially formatted comments are part of the build contract.

## Dependencies and integration points
It depends only on basic Linux types but integrates with generated OID registry data, X.509/PKCS parsers, public-key crypto, keyrings, CIFS/SPNEGO/Kerberos, module signing, IMA, and TPM key parsing.

## Risks and test signals
Risks include editing enum/comment format so the generator fails, enum value drift across generated tables, missing newer algorithm OIDs, DER length validation mistakes in consumers, and unknown OIDs falling through incorrectly. Test the OID generator, certificate parsing for RSA/ECDSA/GOST/SM2/SHA3/ML-DSA, unknown OID handling, formatted OID output, and build-time generated table consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/oid_registry.h -->
