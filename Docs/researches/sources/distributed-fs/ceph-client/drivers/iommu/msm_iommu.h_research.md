# sources/distributed-fs/ceph-client/drivers/iommu/msm_iommu.h

## Purpose
`msm_iommu.h` defines shared Qualcomm MSM IOMMU data structures and constants used by the MSM driver and any interrupt/fault integration. It describes hardware instances, context-bank masters, mapping attributes, and the exported fault handler.

## Important APIs, Types, and Functions
Constants include shareability attributes (`MSM_IOMMU_ATTR_NON_SH`, `MSM_IOMMU_ATTR_SH`), cacheability attributes (`MSM_IOMMU_ATTR_NONCACHED`, write-back/write-through variants, `MSM_IOMMU_CP_MASK`), and sizing limits (`MAX_NUM_MIDS`, `IOMMU_MAX_CBS`).

`struct msm_iommu_dev` represents one hardware block: MMIO base, number of context banks, device pointer, IRQ, clocks, global/domain list nodes, context list, context allocation bitmap, and embedded `iommu_device`. `struct msm_iommu_ctx_dev` represents a context-bank master: OF node, context number, array of machine IDs, count, and list node. The header declares `irqreturn_t msm_iommu_fault_handler(int irq, void *dev_id)`.

## Control Flow and State
The header has no runtime control flow, but its structures define the state owned by `msm_iommu.c`: global registration, domain attachment, context-bank allocation, and MID routing. The `mids` array is bounded and filled from `#iommu-cells` arguments during OF translation.

## Dependencies and Integration Points
The header includes interrupt, IOMMU, and clock definitions. It is tightly coupled to the MSM driver and the hardware macro header. The structures are not a stable external ABI; they are internal kernel driver state.

## Risks and Test Signals
Risks include fixed-size MID and context-bank arrays, implicit assumption that context mappings are design-time/static, and shared structures modified under the driver's global spinlock. Test signals include compile coverage for the MSM driver, OF parsing with maximum MIDs, context-bank counts near `IOMMU_MAX_CBS`, and fault handler declaration consistency.
