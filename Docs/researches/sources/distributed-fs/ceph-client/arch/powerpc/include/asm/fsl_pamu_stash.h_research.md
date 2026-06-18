# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_pamu_stash.h

Purpose: Exposes Freescale PAMU cache-stash configuration for IOMMU domains.

Important APIs, types, and functions: `enum pamu_stash_target` names L1, L2, and L3 stash targets. `fsl_pamu_configure_l1_stash(struct iommu_domain *domain, u32 cpu)` programs L1 stashing for a domain relative to a CPU.

Control flow: IOMMU or device setup code selects a target CPU/domain and calls the helper before DMA traffic that should be stashed near that CPU.

State and persistence: The header stores no state. Configuration persists only in PAMU/IOMMU hardware tables until changed or reset.

Dependencies and integration points: Depends on the generic `iommu_domain` abstraction and Freescale PAMU backend code. It is a small interface between DMA isolation and cache-locality policy.

Risks: CPU-to-cache mapping must be valid for the SoC. Stashing on the wrong CPU can hurt performance or violate assumptions in driver affinity code. Builds without PAMU support need the implementation to be correctly gated elsewhere.

Test signals: Test domain setup on valid and invalid CPU IDs, DMA traffic locality/performance counters, multi-CPU affinity changes, and compile coverage with PAMU/IOMMU options enabled and disabled.
