# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc5_qm_regs.h

## Purpose

This generated header defines the TPC5 queue-manager register offsets for Gaudi. It is the TPC5-specific instance of the QMAN map used for queue control, producer/completion queues, command processors, arbitration, rate limiting, indirect APB gateway access, and error reporting. It contains 406 macros from `mmTPC5_QM_GLBL_CFG0` at `0xF48000` through `mmTPC5_QM_GLBL_MEM_INIT_BUSY` at `0xF48D00`.

## Important APIs, types, and macros

The file exports only `#define` constants. The macro layout covers `GLBL_*` global/protection/security/status/error registers, four `PQ_*` producer queues, five `CQ_*` completion/command queues, five `CP_*` command processor lanes, the large `ARB_*` credit/choice/status/error region, `CGM_*` clock gating controls, local range and strict-priority settings, HBW/LBW rate-limit controls, `GLBL_AXCACHE`, and `IND_GW_APB_*` indirect gateway registers.

## Control flow and state behavior

Consumers perform the runtime work. Gaudi stop logic writes `mmTPC5_QM_GLBL_CFG1` to stop CPs, queue doorbell selection maps `GAUDI_QUEUE_ID_TPC_5_0..3` to `mmTPC5_QM_PQ_PI_0..3`, MMU setup writes non-secure property registers, and security code builds protection masks from TPC5 QMAN offsets. Queue indices, CP state, fence counts, arbiter credits, and error captures are hardware state.

## Dependencies and integration points

The header is aggregated by `gaudi_regs.h` and aligns with `mmTPC5_QM_BASE` in `gaudi_blocks.h` (`0x7FFCF48000ull`). It integrates with Gaudi queue IDs, async event `GAUDI_EVENT_TPC5_QM`, register access helpers such as `WREG32`, and shared TPC0 QMAN field definitions used for equivalent bit positions.

## Risks and test signals

Risks concentrate around queue doorbells, security properties, and arbitration state: an incorrect offset may submit to a wrong queue, leave CPs running during reset, or misprogram protection windows. Good signals are compile coverage, TPC5 queue submission/doorbell tests, reset tests that stop TPC QMANs, MMU ASID tests, and structural checks proving the TPC4/TPC5/TPC6 QMAN macro sets remain normalized-identical aside from prefix and base address.
