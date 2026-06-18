<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_buffer_mgr.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_buffer_mgr.h

Purpose: declares the buffer-manager interface used by the CryptoCell cipher, AEAD, and hash front ends. It provides common enum/type definitions for DLLI/MLLI selection and scatterlist copy direction.

Important APIs, types, and functions: `enum cc_req_dma_buf_type` distinguishes no buffer, direct-linked DMA (`CC_DMA_BUF_DLLI`), and MLLI table (`CC_DMA_BUF_MLLI`). `enum cc_sg_cpy_direct` controls copy direction for `cc_copy_sg_portion()`. `struct cc_mlli` stores SRAM address, mapped scatterlist counts, original SG entries, and MLLI entries. `struct mlli_params` stores the DMA pool, virtual address, DMA address, and byte length of an allocated MLLI table. Declared APIs cover initialization, cipher map/unmap, AEAD map/unmap, hash update/final map/unmap, and scatterlist portion copying.

Control flow: consumers call the map function before emitting hardware descriptors, inspect request-context fields populated by the implementation, submit descriptors, and then call the matching unmap from completion/error paths. The init function must run before algorithm registration can process requests because cipher/AEAD/hash mapping can allocate from `drvdata->mlli_buffs_pool`.

State and persistence behavior: the header describes transient per-request state rather than persistent storage. `mlli_params` values are valid only while a request mapping is live; `cc_mlli.sram_addr` points to driver SRAM assigned elsewhere and is meaningful after the MLLI table has been copied to SRAM.

Dependencies and integration points: includes Linux crypto alg APIs and `cc_driver.h`. It is used by `cc_cipher.c`, `cc_aead.c`, `cc_hash.c`, and any future request type that needs common DMA/MLLI handling.

Risks: the buffer-type enum is part of an implicit contract with descriptor builders; if a builder assumes DLLI while the mapper produced MLLI, hardware reads the wrong address form. `cc_mlli` has both mapped and logical counts, and mixing them can cause invalid DMA unmaps or descriptor lengths. API callers must pair every successful map with the exact matching unmap.

Test signals: compile coverage for all users, DMA API debug, request paths that exercise each enum value, and failure-injection around MLLI pool allocation and scatterlist mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_buffer_mgr.h -->
