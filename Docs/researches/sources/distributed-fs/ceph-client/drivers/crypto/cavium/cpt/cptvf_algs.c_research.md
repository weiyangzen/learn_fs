# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_algs.c

Purpose: registers Linux skcipher algorithms backed by the CPT VF SE engine and translates skcipher requests into CPT flexi-crypto requests.

Important APIs and control flow: `cvm_encrypt()` and `cvm_decrypt()` call `cvm_enc_dec()`, which initializes request context, builds input/output buffer lists, stores callback data, selects a VF handle by `smp_processor_id()`, and submits through `cptvf_do_request()`. Setkey handlers validate AES, XTS, and 3DES keys and populate `struct cvm_enc_ctx`. `cvm_crypto_init()` adds a VF to a global device array and registers algorithms when `dev_count == 3`; `cvm_crypto_exit()` unregisters when the last device exits. Algorithms include `xts(aes)`, `cbc(aes)`, `ecb(aes)`, `cbc(des3_ede)`, and `ecb(des3_ede)`.

State and persistence: per-transform state is key/cipher metadata in the crypto context; per-request state is DMA-capable request context; global state is `dev_handle`.

Dependencies and integration points: depends on crypto skcipher API, AES/XTS/DES helpers, scatterlists, `cptvf_algs.h`, and request manager submission.

Risks and test signals: risks include direct `sg_virt()` use, global device selection by CPU without bounds against `dev_count`, algorithm registration hard-coded to the fourth VF, and 3DES context type differing from AES while common setkey writes `cvm_enc_ctx`. Test signals include `cryptomgr` self-tests for all registered modes, request completion callback status handling, XTS key verification, and multi-VF hotplug/unload behavior.
