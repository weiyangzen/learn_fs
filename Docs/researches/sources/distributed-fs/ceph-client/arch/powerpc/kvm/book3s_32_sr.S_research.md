# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_32_sr.S

## Purpose
Provides 32-bit Book3S PR assembly macros for switching segment-register and BAT state between host and guest on KVM entry/exit.

## Important APIs, Types, And Functions
Defines `LOAD_GUEST_SEGMENTS` and `LOAD_HOST_SEGMENTS` macros. Internal helper macros include `XCHG_SR`, `KVM_KILL_BAT`, and `KVM_LOAD_BAT`. It references shadow-vCPU offsets such as `SVCPU_SR`, saved BAT data in `BATS`, and kernel MM context fields.

## Control Flow
On guest entry, `LOAD_GUEST_SEGMENTS` loads all 16 guest shadow segment registers with `mtsr` and clears guest-visible BATs by writing zero to IBAT/DBAT upper and lower registers. On exit, `LOAD_HOST_SEGMENTS` restores saved host BAT registers, reconstructs high kernel segment registers for segments `0xc` to `0xf`, briefly enables data relocation to call `switch_mmu_context(current->mm)`, and disables paging again before returning to the exit path.

## State And Persistence
The macros directly mutate CPU segment registers, BAT SPRs, MSR[DR], and temporary GPRs. Persistent state is the saved host BAT table and shadow-vCPU segment array maintained elsewhere.

## Dependencies And Integration Points
Used by Book3S PR assembly entry/exit code. Depends on `asm-offsets`, SPR constants, `switch_mmu_context`, `current->mm`, and the convention that the guest runs with host R1/R2 and shadow-vCPU pointer in the expected registers.

## Risks And Edge Cases
Wrong register clobber assumptions or offset mismatches corrupt host or guest address translation. Calling `switch_mmu_context` requires paging enabled and preserves the exit-handler ID explicitly. BAT restoration only overwrites saved upper/lower pairs and must match host setup.

## Test Signals
Signals are 32-bit PR guest entry/exit stability, host memory access after guest exit, segment-register stress, BAT-using guests, and exception exits taken immediately after segment switches.
