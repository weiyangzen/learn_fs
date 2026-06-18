<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/eadm.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/eadm.h

Purpose: Defines Extended Asynchronous Data Mover structures and SCM device driver hooks.

Important APIs/types/functions: `arqb`, `arsb`, `msb`, `aidaw`, `aob`, `scm_device`, `scm_driver`, `scm_driver_register()`, `eadm_start_aob()`, and `scm_irq_handler()`. Source-visible declarations include: #define _ASM_S390_EADM_H; struct arqb {; u64 data;; #define ARQB_CMD_MOVE 1; struct arsb {; u64 fail_msb;; u64 fail_aidaw;; u64 fail_ms;; u64 fail_scm;; #define EQC_WR_PROHIBIT 22.

Control flow: SCM drivers build asynchronous operation blocks with move specification blocks and AIDAWs, submit them through EADM, and receive completion/error callbacks from IRQ handling.

State and persistence behavior: Persistent state includes SCM device objects, operation blocks, block queues, request references, and hardware operation state.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <linux/device.h>, #include <linux/blk_types.h>, #include <asm/dma-types.h>. Integrated with Integrates storage class memory drivers, block layer completions, CIO interrupt handling, and DMA address wrappers..

Risks: Packed operation blocks and request lifetimes are hardware-facing; bad block counts or completion handling can corrupt SCM I/O.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 121 lines, 2116 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/eadm.h -->
