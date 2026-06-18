<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/ufshci.h -->
# sources/distributed-fs/ceph-client/include/ufs/ufshci.h

Purpose: defines UFS Host Controller Interface register offsets, bit masks, queue register layout, crypto capability/config formats, UIC command constants, UTRD/UTMRD/CQE/PRDT descriptor layouts, and helper macros.

Important APIs and types: register enums cover core UFSHCI, crypto, MCQ config, SQ/CQ runtime, and interrupt aggregation registers. Masks describe capabilities, interrupts, controller status, UIC layer errors, AHIT, MCQ bits, and crypto config. Wire/DMA structs include `ufs_crypto_capabilities`, `ufs_crypto_cap_entry`, `ufs_crypto_cfg_entry`, `ufshcd_sg_entry`, `utp_transfer_cmd_desc`, `request_desc_header`, `utp_transfer_req_desc`, `cq_entry`, and `utp_task_req_desc`.

Control flow: the driver reads capabilities/version, enables the controller, programs descriptor base registers, rings transfer/task doorbells or MCQ tail pointers, services interrupts/CQ entries, decodes OCS/UIC error state, configures auto-hibern8, and optionally configures inline crypto.

State and persistence: the header defines hardware register and DMA descriptor layouts. Live state exists in controller registers, DMA rings/descriptors, crypto key slots, interrupt status, and MCQ pointers.

Dependencies and integration points: depends on Linux types and `ufs.h` for UPIU structures. It integrates tightly with `ufshcd.h`, SCSI UFS core, MMIO accessors, DMA mapping, MCQ, MSI/ESI, and blk-crypto.

Risks and test signals: risks include endian/bitfield layout in descriptor headers and CQ entries, static size assertions, register-version differences, MCQ vs legacy capability interpretation, PRDT size granularity, and crypto key material layout. Test register programming on UFSHCI 1.x-5.x controllers, DMA descriptor size/alignment, MCQ completion parsing, UIC error injection, interrupt aggregation, and crypto enable/config paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/ufs/ufshci.h -->
