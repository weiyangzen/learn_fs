<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_cipher.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_cipher.h

Purpose: declares skcipher request state, allocation APIs, and protected-key token layout for the CryptoCell cipher front end.

Important APIs, types, and functions: `struct cipher_req_ctx` stores per-request generic async context, selected DMA buffer type, input/output SG and MLLI counts, copied IV pointer, and MLLI allocation parameters. `struct cc_hkey_info` is the packed protected-key token passed through setkey, carrying real key length and two hardware key slots. `CC_HW_KEY_SIZE` exposes the token length for algorithm templates. Public functions are `cc_cipher_alloc()` and `cc_cipher_free()`.

Control flow: `cc_cipher.c` declares `sizeof(struct cipher_req_ctx)` as the base request size and appends fallback request space for ESSIV where needed. The buffer manager fills DMA and MLLI fields after mapping, descriptor builders consume them, and completion frees any live request resources.

State and persistence behavior: `cipher_req_ctx` is transient for one request. Its `iv` pointer references a DMAable copy of caller IV, not caller memory. `mlli_params` is live only between mapping and unmapping. `cc_hkey_info` is caller-provided key metadata and is copied into private context by protected-key setkey.

Dependencies and integration points: includes `cc_driver.h` and `cc_buffer_mgr.h`, binding cipher request state to common async context and buffer mapping types. Used by `cc_cipher.c` and `cc_buffer_mgr.c`.

Risks: packed key token layout is externally visible to users of protected-key algorithms; changing it would break setkey callers. Request-size accounting must include this structure or buffer-manager writes will corrupt memory. Input/output nent fields are easy to confuse with MLLI nents and mapped nents.

Test signals: compile-time structure use, protected-key setkey with valid/invalid token lengths, MLLI and DLLI skcipher requests, ESSIV fallback request-size tests, and DMA debug for map/unmap balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_cipher.h -->
