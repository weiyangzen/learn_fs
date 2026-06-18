<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/clp.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/clp.h

Purpose: Defines command-list processor request/response headers and selected command structures.

Important APIs/types/functions: `CLP_BLK_SIZE`, command codes, `clp_req_hdr`, `clp_rsp_hdr`, return codes, and SLPC request/response blocks. Source-visible declarations include: #define _ASM_S390_CLP_H; #define CLP_BLK_SIZE PAGE_SIZE; #define CLP_SLPC 0x0001; #define CLP_LPS_BASE 0; #define CLP_LPS_PCI 2; struct clp_req_hdr {; u64 reserved2;; struct clp_rsp_hdr {; u64 reserved2;; #define CLP_RC_OK 0x0010 /* Command request successfully */.

Control flow: Callers build a page-sized CLP block with request headers, issue CLP firmware commands, and parse response headers/status codes.

State and persistence behavior: State is firmware command/response memory supplied by callers.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates s390 firmware/platform discovery, PCI logical partition services, and channel subsystem setup..

Risks: Return codes are firmware-specific and structures must remain packed/aligned to CLP block rules.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 59 lines, 1426 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/clp.h -->
