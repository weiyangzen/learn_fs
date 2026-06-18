# sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_book3s.S

## Purpose
Implements Book3S idle primitives for ISA 2.06/3.00 low-power states, including STOP/NAP/SLEEP/WINKLE entry, GPR-loss save/restore, and Power4/970 nap support.

## Important APIs, Types, And Functions
Exports `isa300_idle_stop_noloss`, `isa300_idle_stop_mayloss`, `idle_return_gpr_loss`, `isa206_idle_insn_mayloss`, `power4_idle_nap`, and `power4_idle_nap_return`. It uses PSSCR, `PPC_STOP`, `PPC_NAP`, `PPC_SLEEP`, `PPC_WINKLE`, `PACAR1`, `PACA_THREAD_INFO`, `_TLF_NAPPING`, and `PNV_THREAD_*` state constants.

## Control Flow
No-loss STOP simply writes PSSCR, executes STOP, returns zero for normal wakeup, and relies on SRESET wakeup to return via LR. May-loss STOP and ISA 2.06 idle save stack pointer, LR, CR, TOC, and nonvolatile GPRs in the red zone before entering the low-power instruction. SRESET wakeup code can call `idle_return_gpr_loss` with a return value to restore the saved context and return to the original caller. The ISA 2.06 path selects NAP/SLEEP/WINKLE and uses the required real-mode store/ptesync/load/false-dependency sequence. `power4_idle_nap` marks `_TLF_NAPPING`, enables POW/EE, and loops until exception fixup returns.

## State And Persistence
State is saved in the current stack red zone and `PACAR1` while in an idle state that may lose GPRs. PSSCR or MSR POW state is written before sleep. The napping flag persists only until wakeup fixup. No durable storage exists.

## Dependencies And Integration Points
Depends on Book3S idle callers saving non-GPR state, interrupt/SRESET wakeup code, PACA layout, cpuidle platform code, KVM nap requirements for r2, and `irq_set_pending_from_srr1` style wakeup reason handling. Power4 nap is called from `idle.c`.

## Risks And Edge Cases
Risks include using may-loss return on a no-loss entry, stack red-zone corruption, missing SPR/MSR/timebase save by the caller, failing the ISA-required idle entry sequence, SRESET wakeup with clobbered volatiles, and KVM requiring exact r2 restoration. The infinite branch after low-power instructions intentionally catches impossible direct fallthrough.

## Test Signals
Signals include POWER7/POWER8/POWER9/POWER10 cpuidle state tests, wakeup by decrementer/external IRQ/doorbell/system reset, GPR corruption tests after deep idle, KVM guest/host idle, Power4/970 nap tests, and tracing of SRR1 wakeup reasons.
