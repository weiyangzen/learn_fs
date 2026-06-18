# sources/distributed-fs/ceph-client/include/linux/qed/storage_common.h

Purpose: describes common QED firmware data structures and constants for storage offloads, especially SCSI-class iSCSI/FCoE queues, buffer descriptors, SGEs, and function initialization.

Important APIs and types: constants define SCSI command queue count, BDQ resources/IDs, SGL thresholds, BDQ ring limits, and selected SCSI opcodes. `struct iscsi_drv_opaque`, `union scsi_opaque`, `struct scsi_bd`, `struct scsi_sge`, `struct scsi_cached_sges`, `struct scsi_drv_cmdq`, and `struct scsi_tqe` describe firmware-visible descriptors. `struct scsi_init_func_params` and `struct scsi_init_func_queues` carry function and queue initialization parameters, including validity bits, status-block indexes, PBL bases, and flow-control thresholds. `enum scsi_sgl_mode`, `struct scsi_sgl_params`, and `struct scsi_terminate_extra_params` model SGL selection and termination accounting.

Control flow: storage drivers fill initialization structures during function setup, hand BDQ/CQ/CMDQ addresses to firmware, post descriptors for receive/immediate/task queues, and use SGL metadata to represent command payload buffers. Termination paths pass pending CQ/CMDQ counts to firmware.

State and persistence: state is firmware/device runtime state: queue indices, external producers, BDQ PBLs, SGL descriptors, and task IDs. It is not persistent across device reset except as reconstructed by driver initialization.

Dependencies and integration points: depends on QED common register-pair definitions, global queue constants, bitfield conventions, and Linux fixed-width endian types. It integrates storage upper layers with QED firmware ramrods and DMA queues.

Risks and test signals: risks include little-endian layout errors, bitfield mask/shift misuse, queue count mismatches, threshold misconfiguration causing deadlock, and SGL mode selection bugs around the cached-SGE threshold. Test iSCSI/FCoE login, large and small SGL I/O, BDQ exhaustion/replenishment, queue initialization on multi-queue devices, termination with outstanding commands, and firmware ABI compatibility.
