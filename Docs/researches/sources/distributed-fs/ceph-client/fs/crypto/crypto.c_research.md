# sources/distributed-fs/ceph-client/fs/crypto/crypto.c

Purpose: implements fscrypt content encryption/decryption primitives, bounce page allocation, read decrypt workqueue setup, IV generation, framework initialization, and rate-limited fscrypt logging.

Important APIs/functions: `fscrypt_enqueue_decrypt_work()` queues bio/page decrypt work. `fscrypt_alloc_bounce_page()` and `fscrypt_free_bounce_page()` manage ciphertext pages from a mempool. `fscrypt_generate_iv()` implements policy-specific IV formats including inode+logical-block variants and direct-key nonce mode. `fscrypt_crypt_data_unit()` performs one skcipher encrypt/decrypt operation. `fscrypt_encrypt_pagecache_blocks()`, `fscrypt_decrypt_pagecache_blocks()`, `fscrypt_encrypt_block_inplace()`, and `fscrypt_decrypt_block_inplace()` are exported content helpers. `fscrypt_initialize()` lazily creates the bounce page pool for filesystems that need it. `fscrypt_init()` creates the high-priority unbound read workqueue, inode-info slab, and keyring support.

Control flow: filesystems ensure inode encryption info is set, then call page/block helpers during writeback, read completion, or compression paths. Helpers compute data unit indexes from folio index/offset or logical block number, generate IVs, and invoke the crypto API with scatterlists.

State and persistence: global workqueue, bounce page mempool, and `fscrypt_inode_info_cachep` persist for the framework lifetime. Per-inode crypto state lives in `fscrypt_inode_info` set up by keysetup code.

Dependencies/integration: crypto skcipher API, mempools, workqueues, page cache, fscrypt policy/keysetup internals, optional inline crypto, and filesystem `fscrypt_operations`.

Risks: all lengths/offsets must align to crypto data unit size and `FSCRYPT_CONTENTS_ALIGNMENT`. Large folios are rejected in encrypt-pagecache helper. Bounce-page pool must exist before use. IV generation must stay synchronized with inline-crypto I/O block limiting.

Test signals: encrypt/decrypt round trips for each policy flag, misalignment warnings/errors, bounce pool lazy init, workqueue parallel decrypt, direct-key IVs, inode+lblk IV variants, in-place helper rejection with subblock data units, and crypto API failure logging.
