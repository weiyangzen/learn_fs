<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/iommu.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/iommu.h

## Purpose
x86 IOMMU global declarations and DMA-remapping policy flags for Intel/AMD IOMMU, SWIOTLB, and overflow handling. The header is 40 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/acpi.h>`; `#include <asm/e820/api.h>`

Notable constants/macros: `#define _ASM_X86_IOMMU_H`; `#define x86_swiotlb_enable false`; `#define DMAR_OPERATION_TIMEOUT ((cycles_t) tsc_khz*10*1000)`

Notable declarations and inline helpers: `#define _ASM_X86_IOMMU_H`; `extern int force_iommu, no_iommu;`; `extern int iommu_detected;`; `extern int iommu_merge;`; `extern int panic_on_overflow;`; `extern bool amd_iommu_snp_en;`; `extern bool x86_swiotlb_enable;`; `#define x86_swiotlb_enable false`; `#define DMAR_OPERATION_TIMEOUT ((cycles_t) tsc_khz*10*1000)`; `static inline int __init`; `u64 start = rmrr->base_address;`; `u64 end = rmrr->end_address + 1;`; `int entry_type;`

## Control Flow
Boot code sets force/no-IOMMU/detected/merge flags, detects ACPI/DMAR/IOMMU hardware, and times out hardware operations using TSC-derived limits.

## State and Persistence
State is global IOMMU policy flags, detected hardware state, SNP/IOMMU flags, and SWIOTLB enablement.

## Dependencies and Integration Points
Depends on ACPI, e820, TSC calibration, DMA mapping subsystems, AMD/Intel IOMMU drivers, and kernel command-line policy.

## Risks
Risks include bad boot-parameter interaction, overflow panic policy surprises, timeout scaling errors before TSC init, and SNP/SWIOTLB mismatches.

## Test Signals
Tests should boot with iommu=on/off/force, AMD and Intel IOMMUs, SWIOTLB fallback, DMA stress, SNP guests, and timeout/error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/iommu.h -->
