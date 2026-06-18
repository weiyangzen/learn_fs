# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_32_mmu.c

## Purpose
Implements guest effective-address translation for 32-bit Book3S PR KVM. It emulates BAT and hash-page-table lookup, updates guest PTE accessed/dirty bits, handles segment-register state, and installs function pointers in `vcpu->arch.mmu`.

## Important APIs, Types, And Functions
Key helpers are `find_sr`, `sr_vsid`, `sr_valid`, `sr_ks`, `sr_kp`, `kvmppc_mmu_book3s_32_xlate_bat`, `kvmppc_mmu_book3s_32_xlate_pte`, `kvmppc_mmu_book3s_32_xlate`, `kvmppc_mmu_book3s_32_mfsrin`, `kvmppc_mmu_book3s_32_mtsrin`, `kvmppc_mmu_book3s_32_tlbie`, `kvmppc_mmu_book3s_32_esid_to_vsid`, `kvmppc_mmu_book3s_32_ea_to_vp`, and `kvmppc_mmu_book3s_32_init`.

## Control Flow
Translation first checks the supervisor-only magic page override, then tries matching DBAT/IBAT entries with permission checks, then searches primary and secondary guest PTE groups derived from SDR1, VSID, and page index. PTE groups are read from guest memory through HVA mapping, decoded as big-endian 32-bit pairs, and permissions are derived from segment key bits plus PTE PP bits. If an entry is used, the code writes guest accessed and dirty bits back as single-byte updates to mimic hardware. Segment updates write guest SR state and map the corresponding shadow segment; `tlbie` flushes matching shadow PTEs on all vCPUs.

## State And Persistence
State lives in the vCPU Book3S extension: segment registers, BAT arrays, SDR1, magic-page addresses, and MMU callback table. Guest PTE A/C bits are persisted into guest memory, so swapper and OS memory management see hardware-like reference/change behavior.

## Dependencies And Integration Points
Depends on generic Book3S KVM MMU data structures, guest memory access helpers, PR shadow HPTE caching, segment mapping in `book3s_32_mmu_host.c`, and PPC 32-bit hash MMU formats. It is wired into PR guest execution by `kvmppc_mmu_book3s_32_init`.

## Risks And Edge Cases
Guest PTE reads can fail if SDR1 points outside memslots. BAT permissions differ by MSR[PR] and segment key state. The magic-page path uses `pte->raddr` offset bits and must not leak stale values. Primary/secondary hash lookup and single-byte A/C updates are subtle and race-prone with guest modification. The code assumes 4 KiB pages.

## Test Signals
Boot 32-bit Book3S guests under PR KVM, exercise BAT mappings, primary and secondary hash PTEs, read-only and no-access faults, dirty/accessed bit updates, `tlbie`, SR changes, magic page access, and 32-bit real/relocated MSR combinations.
