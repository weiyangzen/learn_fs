
# sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_skcipher_algs.c

Purpose: implements virtio crypto AES-CBC skcipher support for the Linux crypto API.

Important APIs, types, and functions: `struct virtio_crypto_skcipher_ctx` stores a selected device and separate encrypt/decrypt session ids. `virtio_crypto_alg_skcipher_init_session()` and close/session helpers manage host sessions through the control queue. `virtio_crypto_skcipher_setkey()` validates AES key sizes, selects a device, and creates both sessions. `__virtio_crypto_skcipher_do_req()` builds a virtio cipher data request with header, IV, src, dst, and status sg entries. `virtio_crypto_skcipher_encrypt()` / `decrypt()` validate block-aligned lengths and queue requests to crypto engine. `virtio_crypto_skcipher_finalize_req()` updates IV, frees allocations, and finalizes the request.

Control flow: setkey validates AES-128/192/256 and creates encrypt and decrypt sessions for `VIRTIO_CRYPTO_CIPHER_AES_CBC`. Encrypt/decrypt select data queue 0, attach callback state, reject zero or non-block-multiple input appropriately, and transfer to the queue's engine. The engine callback allocates request header and sg pointer array, copies the IV to DMA-safe memory, snapshots decrypt IV from the last source block, checks total request size against device `max_size`, submits to the virtqueue, and returns asynchronously. Completion maps virtio status, updates output IV from the last ciphertext block on encryption, frees IV/request allocations, and finalizes.

State and persistence: transform state is selected virtio device plus encrypt/decrypt session ids. Request state includes allocated virtio data header, sg array, DMA-safe IV buffer, status byte, and data-queue pointer. Algorithm registration state is an `active_devs` count in the static algorithm table.

Dependencies and integration points: depends on crypto skcipher/engine APIs, AES constants, scatterwalk, virtqueue locking, manager device selection, control queue helpers, and virtio crypto UAPI. Registers `cbc(aes)` as `virtio_crypto_aes_cbc` with priority 150.

Risks and test signals: only CBC is implemented despite broader Kconfig selections. The code uses `sg_nents(req->dst)` rather than `sg_nents_for_len()` for dst, so oversized dst lists affect sg count and request size. IV update rules are correctness-sensitive, especially in-place decrypt. `virtqueue_kick()` is called even if `virtqueue_add_sgs()` returns an error. Test signals include AES-CBC selftests, 128/192/256-bit keys, zero length, non-block length rejection, max_size rejection, rekey close/recreate, virtqueue add failure, status mapping, and unplug while sessions are live.
