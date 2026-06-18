<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/chsc.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/chsc.h

Purpose: Declares CHSC notification and network-address-information structures.

Important APIs/types/functions: PNSO operation codes, packed NAI/resume-token/area structures, notify types, and CHSC notifier registration. Source-visible declarations include: #define _ASM_S390_CHSC_H; struct notifier_block;; #define PNSO_OC_NET_BRIDGE_INFO 0; #define PNSO_OC_NET_ADDR_INFO 3; struct chsc_pnso_naid_l2 {; u64 nit;; struct { u8 mac[6]; u16 lnid; } addr_lnid;; struct chsc_pnso_resume_token {; u64 t1;; u64 t2;.

Control flow: Channel subsystem code fills request areas, receives CHSC response records, and notifies registered listeners on CSS or channel-path changes.

State and persistence behavior: State is hardware CHSC response data and notifier-chain registrations.

Dependencies and integration points: Direct includes are #include <uapi/asm/chsc.h>. Integrated with Integrates CCW device path information, network bridge/address queries, notifier blocks, and CSS reconfiguration..

Risks: Packed layouts and resume tokens are firmware ABI; incorrect parsing can lose path/network topology updates.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 84 lines, 1744 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/chsc.h -->
