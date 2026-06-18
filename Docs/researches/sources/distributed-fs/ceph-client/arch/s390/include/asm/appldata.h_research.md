<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/appldata.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/appldata.h

Purpose: Defines the VM DIAG X'DC' application-data parameter block and call helper.

Important APIs/types/functions: `APPLDATA_*` function codes, `appldata_parameter_list`, `appldata_product_id`, and `appldata_asm()`. Source-visible declarations include: #define _ASM_S390_APPLDATA_H; #define APPLDATA_START_INTERVAL_REC 0x80; #define APPLDATA_STOP_REC 0x81; #define APPLDATA_GEN_EVENT_REC 0x82; #define APPLDATA_START_CONFIG_REC 0x83; struct appldata_parameter_list {; u64 product_id_addr;; u64 buffer_addr;; struct appldata_product_id {; static inline int appldata_asm(struct appldata_parameter_list *parm_list,.

Control flow: `appldata_asm()` refuses non-VM environments, fills physical addresses for the product ID and data buffer, increments DIAG statistics, and executes `diag 0xdc`.

State and persistence behavior: State is CP/VM application-data monitor state plus caller buffers visible through physical addresses.

Dependencies and integration points: Direct includes are #include <linux/io.h>, #include <asm/machine.h>, #include <asm/diag.h>. Integrated with Integrates with z/VM, machine detection, DIAG statistics, and monitoring record producers..

Risks: Buffer lengths and physical address translation must match the packed firmware contract; invoking outside VM correctly returns unsupported.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 69 lines, 1634 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/appldata.h -->
