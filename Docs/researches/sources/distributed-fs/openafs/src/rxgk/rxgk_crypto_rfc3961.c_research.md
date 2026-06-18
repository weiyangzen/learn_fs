## sources/distributed-fs/openafs/src/rxgk/rxgk_crypto_rfc3961.c

### Purpose
`rxgk_crypto_rfc3961.c` adapts the in-tree Kerberos RFC3961 crypto library to rxgk's opaque key API, packet/token crypto needs, transport-key derivation, nonce generation, and enctype ranking.

### Important APIs, Types, And Functions
It defines the concrete `rxgk_key_s` wrapper around a `krb5_keyblock` plus init context. Public functions implement key length lookup, make/copy/random/release key, MIC length/create/verify, encrypt/decrypt, `rxgk_derive_tk`, cipher expansion, nonce generation, and `rxgk_enctype_better`. Static helpers translate errors, map enctypes to checksum types, and implement RFC4402-style PRF+.

### Control Flow
Key creation accepts either full key bytes or random-to-key seed bytes. MIC and encryption operations create a fresh krb5 context/crypto handle per call, perform the RFC3961 operation, populate `RXGK_Data`, and destroy temporary crypto state. Transport-key derivation serializes epoch, cid, start time, and key number into a 20-byte seed, runs PRF+ to the enctype seed length, then calls random-to-key.

### State, Persistence, And Dependencies
Persistent state is the allocated rxgk key object. Other buffers and contexts are per-call. Dependencies are `afs/rfc3961.h`, Rx allocators, `rx_opaque`, `opr/time`, and generated rxgk key usage constants.

### Integration Points
Client/server packet code uses derived transport keys for per-packet MIC/encryption. Token code uses server keys to wrap tokens and random keys for printed tokens. `rxgk_util.c` queries MIC and cipher overhead.

### Risks
Most backend errors collapse to `RXGK_INCONSISTENCY`, reducing diagnostics. Checksum-type mapping is manual and must track supported enctypes. The key object stores a context for initialization/destruction only; crypto calls intentionally allocate separate contexts for thread safety. Negative local enctypes are ranked stronger by policy.

### Test Signals
Signals include known-vector RFC3961 encryption/MIC tests, key length validation for seed/full key inputs, unsupported enctype failures, PRF+ transport-key reproducibility, nonce length, cipher overhead, MIC verification failure mapping, and leak checks across all error paths.
