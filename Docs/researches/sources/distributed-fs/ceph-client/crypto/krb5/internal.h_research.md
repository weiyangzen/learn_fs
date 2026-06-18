<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/internal.h -->
# sources/distributed-fs/ceph-client/crypto/krb5/internal.h

Purpose: Declares private Kerberos 5 crypto profiles, buffer sizing helpers, selftest vector structures, and cross-file entry points shared by the Kerberos module.

Important APIs/types/functions: `struct krb5_crypto_profile` is the method table for PRF, Kc/Ke/Ki derivation, key packaging/loading, encrypt/decrypt, and MIC get/verify operations. Alignment macros compute request, IV, descriptor, and digest buffer sizes. Test structs describe PRF, key, encryption, and MIC vectors. The header declares public-internal helpers from `krb5_api.c`, `krb5_kdf.c`, `rfc3961_simplified.c`, and profile externs for AES-SHA1, AES-SHA2, and Camellia enctypes.

Control flow: Public API functions select a `krb5_enctype`, then dispatch to the profile function pointers declared here. Enctype definition files bind concrete profiles to algorithm names and sizes. Selftest code uses the vector structs and extern arrays when configured.

State and persistence behavior: The header itself has no state. The profile/enctype objects it declares are static const runtime metadata. Temporary crypto buffers are sized using the macros so request layouts remain aligned for the crypto API.

Dependencies and integration points: Includes public `<crypto/krb5.h>`, scatterlist, shash, and skcipher APIs. It is the private contract among all Kerberos crypto compilation units and optional selftests.

Risks: Profile function signatures are security-sensitive; mismatch between enctype sizes and profile behavior can derive wrong keys, truncate checksums incorrectly, or misplace confounders. Alignment macro changes can break AEAD/shash request layout. Extern declarations must track Kconfig/Makefile composition.

Test signals: Build with selftests, run Kerberos vectors for every enctype, validate AEAD/shash buffer alignment under KASAN, and exercise public API calls for prepare/encrypt/decrypt/MIC across all profiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/internal.h -->
