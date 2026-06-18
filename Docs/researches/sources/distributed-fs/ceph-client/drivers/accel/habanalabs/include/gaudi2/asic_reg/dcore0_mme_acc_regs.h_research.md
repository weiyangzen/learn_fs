<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_acc_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_acc_regs.h

## Purpose
`dcore0_mme_acc_regs.h` is the generated address map for the DCORE0 MME accumulator block, prototype `ACC`. It defines 25 `mmDCORE0_MME_ACC_*` registers in the 0x40F8000-0x40F8060 range for writeback-channel AXI/rate-limit controls, stall and cache/protection attributes, accumulator pseudo-random/LFSR controls, clock gating, inflight counters, E2E credits, interrupts, write AXI aggregation counters, BIST, and two-port BVALID aggregation status.

## Important APIs, types, and functions
The file exports address constants only. Key registers are `WBC0_AXI`, `WBC1_AXI`, `WBC0_RL`, `WBC1_RL`, `WBC_STALL`, `AWCACHE`, `AWPROT`, AP LFSR polynomial/seed select/write/read/clock-gate-delay registers, `WBC_SRC_BP`, `CLK_GATE_EN`, `WBC_INFLIGHTS`, `HBW_CLK_ENABLER_DIS`, `E2E_CRDT_TOP0/1`, `INTR_CAUSE`, `INTR_MASK`, `INTR_CLEAR`, write AXI aggregation counters, `BIST`, and `WR_AXI_AGG_2P_BVALID`.

## Control flow
The header contains no control flow. Initialization programs writeback channel policy, AXI attributes, clock gating, E2E credits, and interrupt masks before MME work is launched. Runtime/debug paths read inflight and aggregation counters, while interrupt handling reads cause, writes clear, and respects the mask register. BIST or LFSR seed controls are used by hardware test/diagnostic flows rather than normal command execution.

## State and persistence behavior
Accumulator configuration persists in hardware until reset or reprogramming. Inflight and aggregation counters reflect live MME writeback activity. Interrupt cause is latched until cleared, and clock-gating or HBW clock enabler state can affect whether the accumulator makes progress.

## Dependencies and integration points
This generated map integrates with MME initialization, command execution, writeback handling, interrupt processing, clock/power management, and BIST/diagnostic code. It is part of the broader DCORE0 MME register set and depends on generated block placement remaining stable.

## Risks and edge cases
Risks include stale writeback rate/AXI attribute state, masking accumulator interrupts, clearing causes before logging, using BIST/LFSR controls during active work, and leaving clock gating or source backpressure in a state that stalls MME completion.

## Test signals
Test signals include MME workloads with writeback, correct inflight counter drain at idle, interrupt cause/mask/clear behavior, rate-limit and stall recovery tests, BIST diagnostics where available, and reset cycles that restore writeback channel configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_acc_regs.h -->
