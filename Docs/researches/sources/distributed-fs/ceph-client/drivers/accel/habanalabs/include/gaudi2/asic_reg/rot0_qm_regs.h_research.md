# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_qm_regs.h

## Purpose
`rot0_qm_regs.h` is the generated register address map for rotator 0's queue manager. It exposes the MMIO surface used to configure queues, command processors, completion queues, arbitration, ARC completion paths, error reporting, rate limiting, indirect APB access, and performance counters.

## Important APIs, Types, And Functions
The macros include global configuration/status/error registers, error message enables and protection, four PQ base/size/PI/CI/config/status banks, five CQ config/status/pointer/transfer-size/control banks, CP message bases, fence read-data/count banks, CP barrier/LDMA/CQ offsets, CP status/current-instruction/predicate/debug/credit/input-data registers, PQC HBW/LBW bases and push data, arbiter masks/config/choice/weights/credit/choice-offset/error/status registers, strict-priority CSMR config, ARC CQ config/pointers/status/message bases, address override and shadow CI registers, CP configuration/watchdog/switch controls, ARC/local/engine/QMAN base addresses, PQC status, SEI status/mask, global error address/write-data, L2H compare/mask, local-range, HBW/LBW rate limiters, indirect gateway registers, and free/idle performance counters.

## Control Flow
The header has no executable flow. Runtime QMAN flow programs PQs and CQs, configures CP and fence behavior, sets arbitration and credits, enables error reporting/protection, updates producer indices to submit work, watches consumer/status registers, and services errors or SEI events.

## State, Persistence, And Dependencies
All state is in the hardware queue manager. Queue bases, sizes, PI/CI values, CP state, arbiter credits, masks, and performance counters persist until driver writes or reset. The header depends on matching QMAN masks, ARC auxiliary registers, AXUSER attributes, CGM controls, and common HabanaLabs queue abstractions.

## Integration Points
Security code references many of these addresses when defining protected rotator register ranges. The queue map integrates with command submission, completion handling, firmware/ARC communication, device reset, error handling, performance collection, and async event mapping such as `GAUDI2_EVENT_ROTATOR0_ROT0_QM`.

## Risks
Queue programming bugs can corrupt command streams or completion queues. PI/CI races can hang work submission. Arbiter and credit misconfiguration can starve masters. Error-message masks and protection bits can either hide real faults or generate noisy interrupts. Indirect gateway misuse can touch unintended APB targets.

## Test Signals
High-value tests include descriptor submission through all PQs, CQ completion and CI updates, fence and barrier behavior, QMAN error injection, arbiter fairness, reset while queues are active, SEI interrupt delivery, protected-register access checks, and performance counter sanity.
