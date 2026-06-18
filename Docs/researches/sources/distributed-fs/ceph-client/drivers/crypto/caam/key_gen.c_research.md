<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/key_gen.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/key_gen.c

Purpose: generates MDHA split HMAC keys using CAAM hardware and a JR-backed descriptor, storing the resulting ipad/opad form back into caller-provided key storage.

Important APIs and control flow: `gen_split_key()` computes split key and padded lengths with helpers from `key_gen.h`, validates against `max_keylen`, allocates a descriptor, copies input key into output buffer, maps the output buffer bidirectionally, builds a descriptor that loads the key into class 2, starts MDHA HMAC init for the selected hash, triggers expansion with a zero-length FIFO load, and stores the split key with `FIFOST_TYPE_SPLIT_KEK`. It enqueues via `caam_jr_enqueue()` and waits for `split_key_done()`, which converts JR status through `caam_jr_strstatus()` and completes.

State and persistence behavior: all state is per-call: descriptor allocation, mapped key buffer, completion, and `alginfo` fields updated with split lengths. The generated split key persists only in `key_out` for the caller's transform context.

Dependencies and integration points: used by HMAC/authentication descriptor setup in CAAM crypto API modules. Depends on JR transport, descriptor helpers, MDHA operation constants, and error reporting.

Risks and test signals: risks include `split_key_len()` assuming valid MDHA hash selector index, key material copied and DMA-mapped in-place, no timeout, and descriptor buffer sizing tied to pointer width. Test signals include HMAC self-tests for MD5/SHA1/SHA2 variants, split key length/padding matching MDHA requirements, proper error on oversized keys, and no key corruption on DMA mapping failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/key_gen.c -->
