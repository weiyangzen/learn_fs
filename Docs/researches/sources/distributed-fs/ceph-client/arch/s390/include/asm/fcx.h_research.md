<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fcx.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/fcx.h

Purpose: Defines Fibre Channel Extensions/transport-command-word data structures and helper APIs.

Important APIs/types/functions: `tcw`, `tidaw`, TSA/TSB formats, `dcw`, `tccb`, flag constants, and helpers to initialize/finalize TCWs, TCCBs, TSBs, DCWs, and TIDAWs. Source-visible declarations include: #define _ASM_S390_FCX_H; #define TCW_FORMAT_DEFAULT 0; #define TCW_TIDAW_FORMAT_DEFAULT 0; #define TCW_FLAGS_INPUT_TIDA (1 << (23 - 5)); #define TCW_FLAGS_TCCB_TIDA (1 << (23 - 6)); #define TCW_FLAGS_OUTPUT_TIDA (1 << (23 - 7)); #define TCW_FLAGS_TIDAW_FORMAT(x) ((x) & 3) << (23 - 9); #define TCW_FLAGS_GET_TIDAW_FORMAT(x) (((x) >> (23 - 9)) & 3); struct tcw {; #define TIDAW_FLAGS_LAST (1 << (7 - 0)).

Control flow: CCW transport-mode users build TCWs referencing TCCB command blocks, TSB status blocks, optional TIDAL data lists, and interrogation TCWs, then submit them through CCW device TM start APIs.

State and persistence behavior: Persistent state is caller-allocated channel program memory, transport status, and DMA-visible data-address lists.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <asm/dma-types.h>. Integrated with Integrates CCW transport mode, FICON/DASD, CIO status handling, DMA pools, and `ccwdev.h` APIs..

Risks: Structure packing, data-address flags, and finalization counts are hardware ABI; errors can break channel programs or lose status.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 313 lines, 8150 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fcx.h -->
