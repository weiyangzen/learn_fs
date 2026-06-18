# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_algs.h

Purpose: defines CPT VF crypto algorithm constants, flexi-crypto control bitfields, key/context structures, and the VF request submission prototype.

Important APIs and types: `MAJOR_OP_FC`, `DMA_MODE_FLAG()`, `enum req_type`, `enum cipher_type`, and `enum aes_type` encode microcode request selections. `union encr_ctrl` is the hardware flexi-crypto encryption control word. `struct enc_context`, `fchmac_context`, and `fc_context` form the context passed to firmware. `struct cvm_enc_ctx`, `cvm_des3_ctx`, and `cvm_req_ctx` are Linux crypto transform/request-private contexts.

Control flow and state: the header has no executable flow but fixes the binary layout that `cptvf_algs.c` copies into input lists and `cptvf_reqmanager.c` DMA maps to hardware.

Dependencies and integration points: depends on `request_manager.h` and indirectly on CPT common hardware structures. Crypto algorithm callbacks and request manager share these structures.

Risks and test signals: risks include endian-sensitive bitfield layout, fixed key offsets such as `KEY2_OFFSET`, mismatch between DES3 and AES context structs, and not covering all declared cipher enum values. Test signals include correct control-word bytes in DMA input, AES key-length encoding, XTS key placement, and firmware accepting generated flexi-crypto contexts.
