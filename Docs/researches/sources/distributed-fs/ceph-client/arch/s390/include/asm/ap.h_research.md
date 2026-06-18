<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ap.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/ap.h

Purpose: Exposes inline instruction wrappers and data structures for s390 Adjunct Processor crypto queues.

Important APIs/types/functions: `ap_qid_t`, queue status unions, TAPQ/QCI/AQIC/QACT config structures, AP bind/associate helpers, `ap_nqap()`, and `ap_dqap()`. Source-visible declarations include: #define _ASM_S390_AP_H_; typedef unsigned int ap_qid_t;; #define AP_MKQID(_card, _queue) (((_card) & 0xff) << 8 | ((_queue) & 0xff)); #define AP_QID_CARD(_qid) (((_qid) >> 8) & 0xff); #define AP_QID_QUEUE(_qid) ((_qid) & 0xff); struct ap_queue_status {; union {; unsigned int value : 32;; struct {; unsigned int status_bits : 8;.

Control flow: Wrappers load AP queue IDs and control blocks into fixed general registers, issue PQAP/NQAP/DQAP instructions, loop on partial completion where required, and return hardware queue status words to AP bus and crypto drivers.

State and persistence behavior: State lives in AP hardware queues, configuration masks, interrupt indicators, message buffers, residual receive state, and caller-supplied control blocks.

Dependencies and integration points: Direct includes are #include <linux/io.h>, #include <asm/asm-extable.h>. Integrated with Integrates with s390 AP bus, zcrypt, vfio-ap, protected/secure execution queue handling, adapter interrupts, and exception-table recovery..

Risks: Register conventions and partial-completion handling are critical. `ap_dqap()` truncation uses response code `0xff` and residual GR0 handoff, so callers must preserve continuation state correctly.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 566 lines, 16432 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ap.h -->
