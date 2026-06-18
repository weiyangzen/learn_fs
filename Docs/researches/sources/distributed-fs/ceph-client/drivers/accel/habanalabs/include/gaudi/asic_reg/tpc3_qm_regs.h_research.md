# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc3_qm_regs.h

## Purpose
`tpc3_qm_regs.h` is an auto-generated Gaudi ASIC register map for the TPC3 queue manager. It names the QMAN global, producer queue, completion queue, command processor, arbitration, error, security, clock-gating, local-range, rate-limit, indirect-gateway, and memory-init registers used by the HabanaLabs Gaudi driver to submit and control work on TPC engine 3.

## Important APIs, types, and functions
This header defines no functions or types. Its API surface is 407 `#define` constants guarded by `ASIC_REG_TPC3_QM_REGS_H_`. The register window starts at `mmTPC3_QM_GLBL_CFG0` (`0xEC8000`) and ends at `mmTPC3_QM_GLBL_MEM_INIT_BUSY` (`0xEC8D00`).

The main register families are:
- Global QMAN configuration, protection, error configuration, secure/non-secure properties, status, and message enable registers.
- Four producer queue sets for base, size, producer/consumer index, config, AXI user attributes, and status.
- Five completion queue sets for configuration, AXI user attributes, status, pointers, transfer sizes, control, and FIFO counts.
- Command processor registers for message base addresses, local DMA offsets, fences, status/current instruction, barriers, debug, and AXI user attributes.
- Arbitration registers for WRR weights, master credits, choice queue offsets, watchdog, message attributes, base, state/status, and error status/reporting.
- Clock gating, local range, priority/rate-limit, AXCACHE, indirect APB gateway, global error address/data, and memory-init busy symbols.

## Control flow
The header is passive, but the constants are used directly in TPC3 queue control flow. Command submission maps `GAUDI_QUEUE_ID_TPC_3_0` through `GAUDI_QUEUE_ID_TPC_3_3` to `mmTPC3_QM_PQ_PI_{0..3}` doorbell registers. Reset/stop paths write `mmTPC3_QM_GLBL_CFG1` with CP stop bits. MMU setup writes `mmTPC3_QM_GLBL_NON_SECURE_PROPS_{0..4}`. Error paths rely on TPC3 QMAN error and arbitration message registers to route faults to the CPU/firmware event model.

Initialization logic often reaches TPC3 by applying the common TPC QMAN stride rather than by spelling out every TPC3 symbol. This file must therefore preserve exact prototype register spacing for all queue, CP, arbitration, and global registers.

## State and persistence
The header has no software persistence. It identifies hardware state that lives in TPC3_QM: queue bases and indices, completion pointers and sizes, CP fence/current-instruction state, barrier/debug state, arbitration credits, ASID/security attributes, error routing, rate limits, clock gating, and local range configuration. This state is programmed during initialization and MMU setup, changes as queues run, and is cleared or reinitialized during reset.

## Dependencies and integration points
The file integrates with `gaudi.c` queue initialization, doorbell selection, QMAN stop/reset, clock-gating disable, MMU ASID programming, state dump support, and event handling through `GAUDI_EVENT_TPC3_QM`. It depends on generated mask headers and on the common Gaudi QMAN programming assumptions used for TPC0 through TPC7.

## Risks and edge cases
- Incorrect `PQ_PI_*` symbols can break only TPC3 submissions while leaving other TPC engines healthy.
- Queue base, size, and CP local DMA offset registers must match the command-buffer layout expected by QMAN initialization.
- Security/non-secure property mistakes can show up as TPC3-specific RAZWI or isolation bugs.
- If explicit TPC3 symbols disagree with loop-derived offsets, initialization, doorbells, stop, and ASID setup can target different hardware blocks.
- Arbitration watchdog and error-message registers are critical for diagnosing QMAN stalls; bad offsets can suppress or misroute the errors needed for recovery.

## Test signals
Positive signals include successful execution and completions on `GAUDI_QUEUE_ID_TPC_3_*`, moving producer/consumer indices, advancing CP/fence counters, clean QMAN stop during reset, and no `GAUDI_EVENT_TPC3_QM` errors under representative TPC workloads. Negative signals include TPC3-only queue hangs, stuck CP current instruction, arbitration error causes, memory-init busy stuck, missing completions, or QMAN errors reported under an unexpected engine id.
