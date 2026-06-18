# sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_64e.S

## Purpose
Provides generic 64-bit Book3E/e500 idle entry routines, including normal `wait` idle and ePAPR event-driven idle hypercall loops.

## Important APIs, Types, And Functions
Defines the macro `BOOK3E_IDLE`, loop macros `BOOK3E_IDLE_LOOP` and `EPAPR_EV_IDLE_LOOP`, exported labels `epapr_ev_idle`, `e500_idle`, and patch site `epapr_ev_idle_start`. It uses PACA fields `PACAIRQHAPPENED`, `PACAIRQSOFTMASK`, `PACACURRENT`, thread flag `_TLF_NAPPING`, and ePAPR `EV_IDLE` hcall token.

## Control Flow
The idle wrapper saves LR, hard-disables interrupts, checks whether a soft-disabled interrupt already happened, traces hard IRQs on, marks soft IRQs enabled, arranges LR so an interrupt returns to the caller, sets `_TLF_NAPPING`, hard-enables interrupts, and executes the selected idle loop. Normal e500 idle spins on `PPC_WAIT_v203`; ePAPR idle repeatedly issues the patched EV_IDLE hypercall sequence. If a pending interrupt is observed before sleeping, it marks `PACA_IRQ_HARD_DIS` and returns without entering idle.

## State And Persistence
State is per-CPU PACA soft-mask/pending IRQ state, the current thread's local flags, LR saved on the stack, and patched hcall opcodes at `epapr_ev_idle_start`. It persists only across the idle entry/wakeup interval.

## Dependencies And Integration Points
Depends on 64-bit Book3E interrupt return code honoring `_TLF_NAPPING`, PACA layout, trace IRQ flags, ePAPR hypercall patching, and `arch_cpu_idle`/platform power-save callbacks. It integrates with lazy interrupt replay and hypervisor idle facilities.

## Risks And Edge Cases
The critical edge case is losing an interrupt that arrived while soft-disabled but before hard-enable and idle. The early `PACAIRQHAPPENED` check and `PACA_IRQ_HARD_DIS` marking are intended to close that window. The ePAPR loop depends on runtime patching of hcall instructions; bad patching traps or spins forever.

## Test Signals
Signals include Book3E 64-bit idle wakeups by decrementer, doorbell, and external IRQ, trace IRQ flag consistency, ePAPR guest idle under a hypervisor, no lost-interrupt stress, and inspection that `epapr_ev_idle_start` is patched during initialization.
