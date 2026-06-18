# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/tlb_low.S

## Purpose
This assembly file provides low-level TLB invalidation primitives for non-hash PowerPC CPUs. It implements the hardware-specific backends used by C flush code: invalidate by virtual address, by PID/context, all entries, broadcast invalidation, and TLBCAM loading for e500-style systems.

## Important APIs, Types, And Labels
Important exported labels include `__tlbil_va`, `_tlbil_pid`, `_tlbil_all`, `_tlbivax_bcast`, `loadcam_entry`, and `loadcam_multi`. The implementation is selected by configuration: 8xx has inline handling elsewhere, 44x/47x uses `tlbsx`/`tlbwe` or set/way sweeps, PPC_85xx uses MMUCSR0 or `tlbilx`, and BOOK3E_64 uses MAS6 plus `tlbilx`/`tlbivax`.

## Control Flow
For 44x, `__tlbil_va` writes the target TID into MMUCR, disables normal interrupts to protect MMUCR during `tlbsx`, and invalidates the matching entry. 47x all/PID invalidation sweeps sets and ways while preserving bolted entries via `tlb_47x_boltmap`; `_tlbivax_bcast` performs broadcast invalidation and includes a 476 DD2 instruction-cache workaround. PPC_85xx paths choose between `MMUCSR0_TLBFI` full invalidation and targeted `tlbilx` feature sections. BOOK3E_64 paths program MAS6 with SPID, TSIZE, and indirect-entry bits before issuing `tlbilx` or `tlbivax`.

## State And Persistence
The file manipulates architectural state directly: MSR interrupt enable, MMUCR, MAS0/1/2/3/6/7, MMUCSR0, and TLB CAM entries. `loadcam_multi()` can temporarily switch to address space 1 and installs/removes a temporary TLB entry to safely rewrite multiple CAM entries.

## Dependencies And Integration Points
The C code in `tlb.c`, `tlb_64e.c`, and platform initialization call these labels. The code depends on SPR definitions, feature-fixup sections, bolted-entry maps, TLBCAM arrays, and CPU errata flags.

## Risks And Test Signals
Risks are architecture-specific: interrupt masking must protect clobbered SPRs, bolted entries must not be invalidated accidentally, MAS6 must include correct PID/page-size/indirect fields, and broadcast invalidations require ordering (`mbar`, `tlbsync`, `sync`, `isync`). Test signals include SMP invalidation storms, 44x/47x errata systems, e500 CAM reload across mappings, and boot tests with feature-fixup alternatives enabled.
