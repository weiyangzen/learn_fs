<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma1_core_ctx_axuser_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma1_core_ctx_axuser_regs.h

## Purpose
`pdma1_core_ctx_axuser_regs.h` defines the PDMA1 core-context AXUSER register addresses. It is an auto-generated address-only header with 20 macros in the `mmPDMA1_CORE_CTX_AXUSER_*` namespace, starting at `0x4C9B800`. These registers control or expose AXI user attributes for PDMA1 core context traffic.

## Important APIs, Types, And Functions
There are no functions or types. The exported macros cover HB attributes (`HB_ASID`, `HB_MMU_BP`, `HB_STRONG_ORDER`, `HB_NO_SNOOP`, `HB_WR_REDUCTION`, `HB_RD_ATOMIC`, `HB_QOS`, `HB_RSVD`, `HB_EMEM_CPAGE`, `HB_CORE`), end-to-end coordination, read/write override low/high registers, and LB coordination/lock/reserved/override registers.

## Control Flow
The header does not implement logic. In runtime code, PDMA1 AXUSER setup writes ASID and MMU-bypass attributes before PDMA traffic uses the core context. `gaudi2.c` writes `mmPDMA1_CORE_CTX_AXUSER_HB_ASID` and clears `mmPDMA1_CORE_CTX_AXUSER_HB_MMU_BP` as part of ASID/MMU preparation for PDMA1.

## State And Persistence
The registers hold hardware AXUSER configuration. Values persist in the device register block until reset or reprogramming. The header only names addresses; it has no software state.

## Dependencies
The file depends on register access helpers in consumers. It shares the generated `AXUSER` prototype layout with `pdma1_qm_axuser_nonsecured_regs.h`, so driver code can configure similar fields in both the queue-manager and core-context paths.

## Integration Points
The key integration point is Gaudi2 memory-management setup, where PDMA1 traffic must carry the correct ASID and must not accidentally bypass the MMU. It also integrates with security/isolation assumptions because AXUSER values participate in transaction identity and routing.

## Risks
Misprogramming ASID or MMU-bypass registers can route DMA through the wrong address space or bypass translation. Address-only headers provide no mask guidance, so callers must know register semantics and full-register write safety. The gap between the QM nonsecured AXUSER block and core-context AXUSER block can lead to configuring one path but not the other.

## Test Signals
Signals include PDMA1 DMA correctness under multiple address spaces, IOMMU/MMU isolation tests, ASID switch tests, reset reinitialization, and checks that PDMA1 setup writes both QM and core-context AXUSER blocks consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma1_core_ctx_axuser_regs.h -->
