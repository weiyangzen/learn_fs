# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/cn10k_cpt.h Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/cn10k_cpt.h

### Purpose
`cn10k_cpt.h` declares CN10K-specific CPT hardware context structures, completion-code accessors, LMTST lifecycle helpers, errata context helpers, context flush, and VF hardware-op selection.

### Important APIs, Types, And Functions
Important definitions are `CN10K_CPT_HW_CTX_SIZE`, `union cn10k_cpt_hw_ctx`, and `struct cn10k_cpt_errata_ctx`. Inline helpers read CN10K or CN9K completion and microcode completion codes from shared `union otx2_cpt_res_s`. Function declarations mirror the CN10K implementation in `cn10k_cpt.c`.

### Control Flow, State, And Persistence
The hardware context union stores the CN10K context header fields persisted in DMA memory for affected devices. The errata context stores both the CPU pointer and tagged DMA CPTR. Completion-code helpers are selected through hardware ops tables and allow common request-manager code to parse different result layouts.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on common, PF, and VF OcteonTX2 structures plus CN9K/CN10K result structs from hardware-type headers. Risks include casting a shared result union to the wrong generation-specific layout, context-size bitfield limits, and the stale closing comment name. Test signals include compile coverage for common/PF/VF objects, CN9K versus CN10K completion-code parsing, errata context setup, and namespace-export consumers.
