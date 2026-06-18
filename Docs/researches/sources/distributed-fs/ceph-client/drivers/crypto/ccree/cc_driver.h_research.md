<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_driver.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_driver.h

Purpose: defines the main CryptoCell driver interface, hardware revision constants, interrupt masks, algorithm wrapper types, per-device state, generic request metadata, and register/DMA helper functions shared across the driver.

Important APIs, types, and functions: defines `DRV_MODULE_VERSION`, `enum cc_hw_rev`, `enum cc_std_body`, DMA and interrupt masks, register macro `CC_REG()`, queue sizing constants, `struct cc_cpp_req`, `struct cc_crypto_req`, `struct cc_drvdata`, `struct cc_crypto_alg`, `struct cc_alg_template`, and `struct async_gen_req_ctx`. Helpers include `drvdata_to_dev()`, `dump_byte_array()`, `cc_iowrite()`, `cc_ioread()`, `cc_gfp_flags()`, and `set_queue_last_ind()`. Declared driver functions include reset wait, register init/fini, byte dumping, and default hash-length query.

Control flow: this header has no top-level runtime flow, but it shapes every request path. Algorithm registration wraps Linux crypto algorithms in `cc_crypto_alg`; request paths fill `cc_crypto_req` before calling the request manager; DMA code uses `cc_gfp_flags()` to match request sleepability; descriptor builders call `set_queue_last_ind()` conditionally for newer hardware.

State and persistence behavior: `cc_drvdata` is persistent from probe to remove and is the owner/locator for all subsystem handles. `cc_crypto_req` is transient per request and carries callback, callback argument, optional synchronous completion, and CPP metadata. `async_gen_req_ctx` is embedded in cipher/AEAD/hash request contexts to retain IV DMA and operation direction.

Dependencies and integration points: includes Linux interrupt/workqueue, DMA, platform device, clock, crypto API headers, register definitions, crypto constants, hardware queue descriptor definitions, and SRAM manager declarations. It is included by nearly every C file in the ccree driver.

Risks: constants in this header control hardware programming and queue limits. Changing `MAX_MLLI_BUFF_SIZE`, interrupt masks, or DMA mask can break multiple subsystems. `struct cc_drvdata` field lifetime assumptions are shared widely; adding fields requires careful probe/remove initialization. `set_queue_last_ind()` is revision-gated and descriptor completion behavior may change if used incorrectly.

Test signals: full driver build, probe/remove, algorithm registration, DMA mask validation, descriptor completion on 630/710/712/713 hardware, and request paths using sleepable and atomic crypto requests to check `cc_gfp_flags()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_driver.h -->
