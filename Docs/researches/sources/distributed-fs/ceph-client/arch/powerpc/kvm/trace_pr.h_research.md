
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_pr.h

## Purpose
Defines tracepoints for Book3S PR KVM reentry, MMU mapping/invalidations, SLB mapping, SLB failures, SLBMTE operations, and PR guest exits.

## Important APIs, Types, And Functions
Events include `kvm_book3s_reenter`, optional 64-bit `kvm_book3s_64_mmu_map`, `kvm_book3s_mmu_map`, `kvm_book3s_mmu_invalidate`, `kvm_book3s_mmu_flush`, `kvm_book3s_slb_found`, `kvm_book3s_slb_fail`, `kvm_book3s_slb_map`, `kvm_book3s_slbmte`, and `kvm_exit`. It uses `kvm_trace_symbol_exit` from `trace_book3s.h`.

## Control Flow
PR code emits these tracepoints around reentry decisions, HPTE/cache updates, MMU flushes, SLB translations, and guest exits. Events capture PTE cache fields, host VPN/PFN, effective/virtual/real addresses, permission flags, SLB masks, and vCPU exit state including PC, MSR, DAR, SRR1, and last instruction.

## State And Persistence
No state is owned. Events snapshot PR MMU and vCPU state into tracing buffers.

## Dependencies And Integration Points
Depends on Book3S PR types such as `struct hpte_cache` and `struct kvmppc_pte`, `trace_book3s.h`, and Linux tracepoints. It is compiled under the `kvm_pr` trace system.

## Risks
Tracepoint consumers rely on field names and formats. Some events expose address mappings and permission bits, so output can be sensitive. The 64-bit map tracepoint is config-gated and tooling must handle absence on non-64-bit builds.

## Test Signals
Enable `kvm_pr:*` tracepoints with a Book3S PR guest. MMU map/flush and SLB events should correlate with guest memory activity; exit events should show symbolic Book3S exception names.
