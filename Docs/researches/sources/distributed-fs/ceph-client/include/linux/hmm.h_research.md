# sources/distributed-fs/ceph-client/include/linux/hmm.h

## Purpose
`hmm.h` defines the Heterogeneous Memory Management range-fault interface used by devices to mirror CPU virtual address ranges into device page tables. It describes PFN flag encoding, conversion helpers, `struct hmm_range`, and `hmm_range_fault()`.

## Important APIs, Types, And Functions
`enum hmm_pfn_flags` defines output flags such as `HMM_PFN_VALID`, `HMM_PFN_WRITE`, `HMM_PFN_ERROR`, `HMM_PFN_DMA_MAPPED`, `HMM_PFN_P2PDMA`, and `HMM_PFN_P2PDMA_BUS`, plus input request flags `HMM_PFN_REQ_FAULT` and `HMM_PFN_REQ_WRITE`. Helpers `hmm_pfn_to_page()`, `hmm_pfn_to_phys()`, and `hmm_pfn_to_map_order()` extract page, physical address, and mapping order. `struct hmm_range` stores notifier, sequence, virtual range, PFN array, default flags, mask, and device-private owner. `hmm_range_fault()` populates the range.

## Control Flow And State
Drivers register/use an `mmu_interval_notifier`, begin an interval read, fill an `hmm_range`, call `hmm_range_fault()`, consume PFN results under the caller lock, and retry if notifier sequence invalidates. Input flags request faulting and write access. Output flags report current validity/access/error/P2P state. Persistent state is in the caller's PFN array and the MMU notifier sequence.

## Dependencies And Integration Points
It depends on `linux/mm.h` and MMU interval notifiers. It integrates with GPU/accelerator drivers, device-private memory migration, P2PDMA, DMA mapping helpers, and process address-space invalidation.

## Risks
Risks include consuming PFNs outside the notifier-read critical section, missing invalidation retry, confusing input request bits with output validity bits, ignoring `HMM_PFN_ERROR`, using `hmm_pfn_to_page()` before checking valid, and mishandling high-order mapping edge cases whose aligned extent may exceed the requested range.

## Test Signals
Use HMM selftests and device driver tests for read/write faults, no-fault queries, invalid VMA/special/poisoned pages, device-private owner filtering, P2PDMA flags, high-order mappings, concurrent munmap/mprotect/migration, and default flag masking.
