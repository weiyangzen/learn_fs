# sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_64.c

## Purpose
Provides the C post-copyback hook for 64-bit PowerPC hibernation resume.

## Important APIs, Types, and Functions
- `do_after_copyback()` restores IOMMU state, touches the softlockup watchdog, and issues a memory barrier.

## Control Flow and State
Called from `swsusp_asm64.S` after restored pages are copied and architectural registers are partly restored.

## State and Persistence Behavior
Restores global IOMMU programming and updates watchdog activity timestamp. The barrier orders copyback and IOMMU/watchdog side effects.

## Dependencies and Integration Points
Depends on `iommu_restore()`, watchdog infrastructure, and 64-bit hibernation assembly.

## Risks
If omitted or misordered, devices may DMA against stale IOMMU state after resume, or the watchdog may fire during long resume copyback.

## Test Signals
Hibernate/resume with active IOMMU/DMA devices and softlockup watchdog enabled.
