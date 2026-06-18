<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/krb5_kdf.c -->
# sources/distributed-fs/ceph-client/crypto/krb5/krb5_kdf.c

Purpose: Implements shared Kerberos key derivation helpers for PRF+ and the Kc, Ke, and Ki usage-specific keys.

Important APIs/types/functions: `crypto_krb5_calc_PRFplus()` implements RFC4402 PRF+ by concatenating `PRF(K, n || S)` blocks and truncating to the requested length. `krb5_derive_Kc()`, `krb5_derive_Ke()`, and `krb5_derive_Ki()` build the 5-byte usage constant from big-endian usage plus the checksum/encryption/integrity seed byte, set the expected output length, and call the profile-specific KDF.

Control flow: PRF+ allocates a combined temporary buffer for generated PRF blocks and `n || S`, loops counter values from 1 until enough material is produced, then copies exactly `L` bytes to the caller's preallocated result. Kc/Ke/Ki derivation is a thin dispatch layer over the selected `krb5_crypto_profile`.

State and persistence behavior: No persistent state. Temporary PRF+ material is freed with `kfree_sensitive()`. Caller-provided result buffers carry output.

Dependencies and integration points: Uses public export for PRF+, private profile methods, Kerberos usage seed constants from `<crypto/krb5.h>`, and allocation alignment helper `round16()`.

Risks: The PRF+ loop assumes the result buffer is already allocated and sized by the caller. Counter overflow is not a practical issue for normal Kerberos lengths but is not explicitly bounded. Usage constants must be exactly encoded or keys for checksum/encryption/integrity will not interoperate.

Test signals: RFC PRF+ vectors, Kc/Ke/Ki derivation vectors for all enctypes/usages, error propagation from profile PRF/KDF methods, sensitive-free checks, and boundary tests where output length is not a multiple of PRF length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/krb5_kdf.c -->
