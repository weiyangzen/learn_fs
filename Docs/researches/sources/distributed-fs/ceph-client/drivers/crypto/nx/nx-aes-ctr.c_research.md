## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-ctr.c

Purpose: implements the RFC3686 variant of AES-CTR using NX hardware.

Important APIs: `ctr_aes_nx_set_key` prepares the AES CTR CPB, `ctr3686_aes_nx_set_key` extracts the trailing nonce from the key, `ctr_aes_nx_crypt` performs the shared encrypt/decrypt operation, `ctr3686_aes_nx_crypt` constructs the RFC3686 IV, and `nx_ctr3686_aes_alg` exports `rfc3686(ctr(aes))`.

Control flow: base setkey initializes the context for AES, selects the correct key property slot for 128/192/256-bit keys, sets `NX_MODE_AES_CTR`, and copies the key. RFC3686 setkey requires a key longer than the nonce, stores the 4-byte nonce in context, and delegates to base setkey. Crypt builds a 16-byte counter block from nonce, request IV, and initial counter 1, loops through scatterlist chunks with `nx_build_sg_lists`, calls `nx_hcall_sync`, copies the output counter for continuation, and updates AES stats.

State and persistence: the transform stores the RFC3686 nonce and key in CPB memory. A local IV/counter is used per request; the caller's request IV is not mutated by the RFC3686 wrapper.

Dependencies: AES and CTR crypto helpers, CPB constants, NX core scatterlist and hcall functions, and OF-provided algorithm properties.

Risks: CTR permits byte-granular blocksize but the NX chunk builder may trim to AES block boundaries when limited; short or non-multiple lengths need vector coverage. The code copies `aes_cbc.cv` while operating in CTR CPB union storage; this relies on union layout equivalence and should be watched during structure changes. Counter continuation must be correct across hardware chunks.

Test signals: RFC3686 test vectors for all AES key sizes, non-block-multiple lengths, multi-chunk large requests, scatterlist offsets, nonce extraction failure for too-short keys, and encrypt/decrypt equivalence.
