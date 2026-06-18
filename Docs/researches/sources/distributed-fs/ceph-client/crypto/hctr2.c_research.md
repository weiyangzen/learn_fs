<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/hctr2.c -->
# sources/distributed-fs/ceph-client/crypto/hctr2.c

Purpose: Implements the `hctr2` and `hctr2_base` skcipher templates for length-preserving encryption using a 16-byte block cipher, XCTR stream mode, and POLYVAL hashing.

Important APIs/types/functions: `struct hctr2_tfm_ctx` owns the block cipher, XCTR skcipher, prepared POLYVAL key, prehashed tweak-length blocks, and `L = E_K(1)`. `hctr2_setkey()` keys both children, derives `H = E_K(0)`, `L`, and precomputed tweak hashes. `hctr2_crypt()` handles both encryption and decryption. `hctr2_hash_tweak()`, `hctr2_hash_message()`, and `hctr2_finish()` implement the HCTR2 hash/encrypt/hash construction. Template create functions validate `xctr(<cipher>)`, derive the underlying block cipher name, require 16-byte block size, and expose a 32-byte tweak as the IV.

Control flow: Create grabs the `xctr` child and matching raw block cipher, then registers a skcipher instance. Runtime requires `cryptlen >= 16`; it copies the first block, forwards scatterlists past the first block for the bulk part, hashes tweak plus bulk data, block-encrypts or decrypts the first-block mask, computes the XCTR IV, runs XCTR over the bulk portion, and after async completion hashes the transformed bulk to write the final first block.

State and persistence behavior: Per-transform state persists child handles and derived POLYVAL/blockcipher material until exit. Per-request state holds the copied first block, XCTR IV, forwarded scatterlists, saved hashed tweak, and a union reused as POLYVAL context or child skcipher request. No disk or global mutable state is maintained.

Dependencies and integration points: Uses internal cipher/skcipher template APIs, `polyval-lib` through `gf128hash.h`, scatterwalk helpers, and imports the `CRYPTO_INTERNAL` namespace. Fscrypt is a key expected consumer because the implementation chooses a 32-byte fixed tweak size to avoid per-file key derivation in some use cases.

Risks: Length-preserving modes are sensitive to exact byte ordering, padding marker handling for partial final blocks, and tweak hashing. The request context union is space-sensitive and protected by a `BUILD_BUG_ON`; layout changes can corrupt child requests. Async XCTR completion must run final hashing once. Inputs shorter than one block are rejected.

Test signals: HCTR2 known-answer vectors, encrypt/decrypt round trips for exact-block and partial-block lengths, 32-byte tweak behavior, in-place/out-of-place scatterlists, async child XCTR completion, template instantiation through `hctr2(aes)` and `hctr2_base(xctr(aes),polyval-lib)`, and fscrypt integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/hctr2.c -->
