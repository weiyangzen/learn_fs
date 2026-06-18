# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/cn10k_cpt.c Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/cn10k_cpt.c

### Purpose
`cn10k_cpt.c` adds CN10K-specific CPT command submission, LMTST setup, and hardware-context errata helpers while preserving fallback OcteonTX2 hardware operations.

### Important APIs, Types, And Functions
Important functions are CN10K `send_cmd`, `cn10k_cptpf_lmtst_init()`, `cn10k_cptvf_lmtst_init()`, `cn10k_cpt_lmtst_free()`, `cn10k_cpt_hw_ctx_init()`, `cn10k_cpt_hw_ctx_clear()`, `cn10k_cpt_hw_ctx_set()`, `cn10k_cpt_ctx_flush()`, and `cptvf_hw_ops_get()`. It defines hardware ops tables selecting either `otx2_cpt_send_cmd`/CN9K completion parsing or CN10K LMTST send/response parsing.

### Control Flow, State, And Persistence
PF/VF LMTST init checks capability flags; without CN10K LMTST the PF uses the OcteonTX2 ops table, while CN10K allocates force-contiguous LMTLINE DMA memory, aligns it to `LMTLINE_ALIGN`, registers it with firmware through `otx2_cpt_lmtst_tbl_setup_msg()`, and installs CN10K ops. Command submission copies instructions to the LF slot's LMTLINE after `dma_wmb()` and flushes through `cn10k_lmt_flush()`. Errata context init allocates and maps a 256-byte hardware context only for affected CN10KA revisions, sets the AOP-valid header, tags the DMA pointer with bit 60, and clear flushes/invalidate before unmapping.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on OcteonTX2 PF/VF/LF structs, AF mailbox setup, Marvell LMT assembly helpers, DMA attributes, hardware capability flags, and CN10K result formats from `cn10k_cpt.h`. Risks include pointer arithmetic on `void *` LMT bases, allocation alignment/unwind, using VF drvdata in `cn10k_cpt_ctx_flush()`, errata revision detection, and ensuring `dma_wmb()` precedes LMT flush. Test signals include CN10K and non-CN10K command submission, LMTST setup failure unwind, PF/VF LMT memory free, errata context init/clear on CN10KA A-step, context flush invalidation, and ops selection by capability bits.
