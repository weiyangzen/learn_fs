<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/key_gen.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/key_gen.h

Purpose: declares split-key generation interfaces and inline helpers for MDHA HMAC split key sizing.

Important APIs and control flow: `split_key_len()` maps MDHA hash selector submasks to doubled pad sizes for MD5, SHA1, SHA224, SHA256, SHA384, and SHA512. `split_key_pad_len()` aligns the split key length to 16 bytes. `struct split_key_result` carries a completion and errno for asynchronous JR completion. Prototypes expose `split_key_done()` and `gen_split_key()`.

State and persistence behavior: no header-owned state; `split_key_result` is per-call state used by `key_gen.c`.

Dependencies and integration points: relies on `OP_ALG_ALGSEL_SHIFT/SUBMASK` constants from descriptor headers included before use. Consumed by CAAM hash/authentication setup code that needs hardware-expanded HMAC keys.

Risks and test signals: risks include no bounds check on the computed `mdpadlen` index for invalid alg selectors and implicit dependence on exactly six supported MDHA hashes. Test signals are correct split/padded lengths for every supported hash, rejected or unreachable invalid alg selectors, and generated split keys passing HMAC known-answer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/key_gen.h -->
