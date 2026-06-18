<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/gart.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/gart.h

## Purpose
GART/IOMMU aperture declarations and helpers for older AMD64-style DMA remapping and AGP aperture handling. The header is 113 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/e820/api.h>`

Notable constants/macros: `#define _ASM_X86_GART_H`; `#define GPTE_VALID 1`; `#define GPTE_COHERENT 2`; `#define GARTEN (1<<0)`; `#define DISGARTCPU (1<<4)`; `#define DISGARTIO (1<<5)`; `#define DISTLBWALKPRB (1<<6)`; `#define INVGART (1<<0)`; `#define GARTPTEERR (1<<1)`; `#define AMD64_GARTAPERTURECTL 0x90`; `#define AMD64_GARTAPERTUREBASE 0x94`; `#define AMD64_GARTTABLEBASE 0x98`; `#define AMD64_GARTCACHECTL 0x9c`; `#define gart_iommu_aperture 0`; `#define gart_iommu_aperture_allowed 0`; `#define gart_iommu_aperture_disabled 1`

Notable declarations and inline helpers: `#define _ASM_X86_GART_H`; `extern void set_up_gart_resume(u32, u32);`; `extern int fallback_aper_order;`; `extern int fallback_aper_force;`; `extern int fix_aperture;`; `#define GPTE_VALID 1`; `#define GPTE_COHERENT 2`; `#define GARTEN (1<<0)`; `#define DISGARTCPU (1<<4)`; `#define DISGARTIO (1<<5)`; `#define DISTLBWALKPRB (1<<6)`; `#define INVGART (1<<0)`; `#define GARTPTEERR (1<<1)`; `#define AMD64_GARTAPERTURECTL 0x90`; `#define AMD64_GARTAPERTUREBASE 0x94`; `#define AMD64_GARTTABLEBASE 0x98`; `#define AMD64_GARTCACHECTL 0x9c`; `extern int gart_iommu_aperture;`; `extern int gart_iommu_aperture_allowed;`; `extern int gart_iommu_aperture_disabled;`; `extern void early_gart_iommu_check(void);`; `extern int gart_iommu_init(void);`; `extern void __init gart_parse_options(char *);`; `void gart_iommu_hole_init(void);`

## Control Flow
Callers query aperture_valid(), gart_iommu_aperture, fallback_aper_order, and AGP bridge apertures to decide whether a GART aperture can back DMA remapping.

## State and Persistence
State is global aperture configuration, fallback order, AGP bridge aperture list, and aperture_resource tracked at boot/runtime.

## Dependencies and Integration Points
Depends on PCI, resource management, e820/memory setup, SWIOTLB/IOMMU selection, and AMD64 GART implementation files.

## Risks
Risks include stale legacy hardware assumptions, aperture overlap with RAM/MMIO, and bad fallback sizing causing DMA failures.

## Test Signals
Tests should boot legacy GART-capable systems or emulation, validate aperture reservation, DMA mapping fallback, AGP aperture discovery, and no-IOMMU configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/gart.h -->
