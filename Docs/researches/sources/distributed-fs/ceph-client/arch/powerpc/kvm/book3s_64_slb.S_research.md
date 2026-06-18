# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_slb.S

## Purpose
Provides 64-bit Book3S PR assembly macros for loading guest SLB entries on entry and restoring host bolted SLB entries on exit.

## Important APIs, Types, And Functions
Defines `LOAD_GUEST_SEGMENTS` and `LOAD_HOST_SEGMENTS`. It uses shadow SLB entry offsets `SVCPU_SLB`, `SVCPU_SLB_MAX`, PACA `PACA_SLBSHADOWPTR`, `SLBSHADOW_SAVEAREA`, `SLB_NUM_BOLTED`, firmware feature patch sections, and labels `slb_loop_enter`, `slb_do_enter`, and `slb_do_exit`.

## Control Flow
Guest entry clears the LPAR SLB shadow count, invalidates the SLB with `slbia`, then iterates the shadow-vCPU SLB array and issues `slbmte` for valid guest entries. Host exit clears the current SLB, restores the LPAR shadow count for bolted entries, reads bolted ESID/VSID pairs from the PACA shadow save area, reloads nonzero entries, and synchronizes.

## State And Persistence
The macros mutate hardware SLB entries and the firmware-visible PACA SLB shadow count. Guest SLB state is sourced from the shadow vCPU; host bolted state is sourced from PACA shadow storage.

## Dependencies And Integration Points
Used by Book3S PR entry/exit code for 64-bit hash MMU guests. Depends on generated offsets, SLB instruction availability, LPAR firmware feature detection, and PACA SLB shadow layout.

## Risks And Edge Cases
Failure to restore bolted host SLB entries can leave the host unable to address kernel mappings after exit. Guest SLB count and entry validity must be trusted only within the allocated shadow array. LPAR shadow count handling must match firmware expectations.

## Test Signals
Boot 64-bit PR guests under LPAR and non-LPAR, stress guest SLB insert/remove/all-invalidate operations, force exits after many guest SLB entries, and verify host stability after repeated entry/exit.
