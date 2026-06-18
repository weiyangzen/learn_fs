# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/mmutrace.h

## Purpose

`mmutrace.h` defines the `kvmmmu` tracepoint subsystem for x86 KVM MMU internals. It provides compact trace events for page-table walks, shadow page lifecycle, MMIO SPTE caching, fast page faults, SPTE changes, TDP MMU changes, and hugepage splitting. The file is included by `mmu.c` with `CREATE_TRACE_POINTS`, so it both declares the event formats and generates their tracepoint definitions.

## Important APIs, Types, And Functions

Shared formatting macros:

- `KVM_MMU_PAGE_FIELDS` declares common trace fields for `struct kvm_mmu_page`: valid generation, GFN, role word, root count, and unsync state.
- `KVM_MMU_PAGE_ASSIGN(sp)` copies those fields from a shadow page into a trace entry.
- `KVM_MMU_PAGE_PRINTK()` decodes `union kvm_mmu_page_role` and formats generation, GFN, level, guest PTE size, quadrant, direct flag, access bits, invalid state, NX/A-D mode, root count, and sync state.
- `kvm_mmu_trace_pferr_flags` maps page-fault error-code bits to readable flag names.

The file exports `TRACE_DEFINE_ENUM()` entries for every `RET_PF_*` value so trace consumers can decode page-fault outcomes consistently.

Trace events include `kvm_mmu_pagetable_walk`, `kvm_mmu_paging_element`, `kvm_mmu_set_accessed_bit`, `kvm_mmu_set_dirty_bit`, `kvm_mmu_walker_error`, `kvm_mmu_get_page`, `kvm_mmu_sync_page`, `kvm_mmu_unsync_page`, `kvm_mmu_prepare_zap_page`, `mark_mmio_spte`, `handle_mmio_page_fault`, `fast_page_fault`, `kvm_mmu_zap_all_fast`, `check_mmio_spte`, `kvm_mmu_set_spte`, `kvm_mmu_spte_requested`, `kvm_tdp_mmu_spte_changed`, and `kvm_mmu_split_huge_page`.

## Control Flow

The header is passive until tracepoints are enabled by the kernel tracing framework. MMU code calls `trace_*` helpers at important transitions. The tracepoint macros snapshot event fields in `TP_fast_assign` and format them in `TP_printk`. Many event payloads intentionally store raw role words or SPTE values and decode them at print time, keeping call-site overhead low.

The final `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `#include <trace/define_trace.h>` section follows the kernel tracepoint convention and must remain outside the include guard so the trace generator can re-read the header.

## State And Persistence Behavior

Tracepoints do not own MMU state. They snapshot selected fields at the call site into the tracing ring buffer. The events can expose transient states such as an SPTE old/new pair, a shadow page becoming unsync, or a stale MMIO SPTE generation. Persistent behavior depends on the kernel tracing backend, not on this file.

## Dependencies And Integration Points

The header depends on Linux tracepoint/trace-events APIs and on x86 KVM MMU types/macros visible from its includer, including `struct kvm_mmu_page`, `struct kvm_page_fault`, `union kvm_mmu_page_role`, `RET_PF_*`, SPTE permission masks, PFERR masks, `get_mmio_spte_generation()`, `is_executable_pte()`, and `shadow_*` masks.

The event namespace is `kvmmmu`. Users can consume it through ftrace/perf/tracefs tooling to correlate MMU behavior with KVM page faults, dirty logging, memslot invalidation, and TDP MMU changes.

## Risks And Edge Cases

Tracepoint formats are a user-visible debugging ABI in practice. Renaming fields or changing enum exposure can break scripts. `KVM_MMU_PAGE_PRINTK()` decodes the role word, so it must stay synchronized with `union kvm_mmu_page_role` layout. `kvm_mmu_set_spte` computes read/execute/user display bits using global shadow masks and SPTE helpers; changes in SPTE encoding need matching trace updates.

The header assumes its includer has already included the right MMU/SPTE definitions. It should not be included as a standalone public API header.

## Test Signals

Build tests should verify trace generation with and without multiple reads of the header. Runtime tests can enable `kvmmmu:*` tracepoints while exercising page faults, MMIO, dirty logging, TDP maps, global zaps, and hugepage splits. Useful sanity checks include matching `RET_PF_*` names in `fast_page_fault`, seeing MMIO generation mismatch events after memslot updates, and confirming `kvm_mmu_split_huge_page` errno values during dirty-log eager splitting.
