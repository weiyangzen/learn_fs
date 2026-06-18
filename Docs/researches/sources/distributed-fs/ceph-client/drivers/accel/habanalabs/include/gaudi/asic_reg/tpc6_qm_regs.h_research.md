# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc6_qm_regs.h

## Purpose

This auto-generated header defines the TPC6 QMAN register map for Gaudi. It provides symbolic offsets for queue-manager global control, producer queues, completion queues, command processors, arbitration, clock/rate controls, indirect gateway registers, and error capture. It contains 406 macros from `mmTPC6_QM_GLBL_CFG0` at `0xF88000` through `mmTPC6_QM_GLBL_MEM_INIT_BUSY` at `0xF88D00`.

## Important APIs, types, and macros

No executable API is declared. The exported register families are `GLBL_*`, `PQ_*` for four producer queues, `CQ_*` for five queues, `CP_*` for five command-processor lanes, `ARB_*` for scheduling/credits/errors, `CGM_*`, `LOCAL_RANGE_*`, `CSMR_STRICT_PRIO_CFG`, HBW/LBW rate limits, `GLBL_AXCACHE`, `IND_GW_APB_*`, and global error/memory-init status registers.

## Control flow and state behavior

Driver users provide control flow. `gaudi_stop_tpc_qmans()` writes `mmTPC6_QM_GLBL_CFG1`; queue ID handling maps `GAUDI_QUEUE_ID_TPC_6_0..3` to `mmTPC6_QM_PQ_PI_0..3`; MMU setup prepares `mmTPC6_QM_GLBL_NON_SECURE_PROPS_0..4`; and security code derives protection masks from TPC6 QMAN offsets. Register contents are hardware queue-manager state and are not persisted by this header.

## Dependencies and integration points

The header is included by the Gaudi register aggregate and aligns with `mmTPC6_QM_BASE` in `gaudi_blocks.h` (`0x7FFCF88000ull`). It integrates with Gaudi queue IDs, async event `GAUDI_EVENT_TPC6_QM`, MMIO helpers, shared QMAN bitfield definitions, and security/protection-bit setup.

## Risks and test signals

The highest-risk offsets are `PQ_PI_*` doorbells, global stop/security registers, and arbiter credit/status regions. A mismatch can cause hangs, lost submissions, or incorrect isolation. Test signals include successful Gaudi builds, TPC6 queue submission tests, reset paths that stop CPs, MMU ASID and security-window validation, and structural diffing against TPC4/TPC5 QMAN maps.
