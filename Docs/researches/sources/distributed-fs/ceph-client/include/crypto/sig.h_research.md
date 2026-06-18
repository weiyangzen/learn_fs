# sources/distributed-fs/ceph-client/include/crypto/sig.h

Purpose: exposes the public crypto API for stateless-style public-key signature algorithms.

Important APIs, types, and flow: `struct sig_alg` provides key-size, digest-size, max-size, sign, verify, set-public-key, set-private-key, optional init/exit, and base metadata callbacks. `struct crypto_sig` wraps the transform and exit callback. Helpers allocate/free transforms, query algorithm sizes, sign digests/messages, verify signatures, and load public or private keys.

State and persistence: key material is stored in transform contexts after setkey. Sign/verify buffers are caller-owned. No persistence exists.

Dependencies and integration: builds on generic crypto transforms and is consumed by public-key infrastructure, RSA/ML-DSA providers, and signature templates.

Risks and test signals: risks include key/digest/signature size reporting drift, private-key operation exposure, and algorithms with message-vs-digest semantic differences. Signals include sign/verify known-answer tests, invalid key and signature sizes, public-only verify paths, private-key sign paths, and query integration with asymmetric keys.
