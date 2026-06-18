<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/hash.h -->
# sources/distributed-fs/ceph-client/crypto/hash.h

Purpose: Local internal header connecting hash frontend code to the core crypto internals.

Important APIs/types/functions: Declares `extern const struct crypto_type crypto_shash_type` and `int hash_prepare_alg(struct hash_alg_common *alg)`. Includes `<crypto/internal/hash.h>` and local `internal.h`.

Control flow: This header has no executable flow. Compilation units include it when they need shared hash registration/type preparation declarations.

State and persistence behavior: No state is stored. The declarations refer to crypto type metadata and algorithm preparation implemented elsewhere.

Dependencies and integration points: Bridges hash code to `struct hash_alg_common`, the shash frontend, and the internal crypto algorithm registry helpers in `internal.h`.

Risks: Because it exposes internal symbols, declaration drift with the implementation can break shash registration or module linkage. It intentionally is not a public UAPI header.

Test signals: Build coverage of hash/shash modules, successful shash algorithm registration, and no unresolved symbol or type mismatch warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/hash.h -->
