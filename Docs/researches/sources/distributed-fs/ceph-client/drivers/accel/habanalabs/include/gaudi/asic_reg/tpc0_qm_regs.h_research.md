# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc0_qm_regs.h

## Purpose

`tpc0_qm_regs.h` is an auto-generated MMIO address map for the Gaudi TPC0 queue manager. It defines `mmTPC0_QM_*` constants for global queue-manager control/status, producer queues, completion queues, command processors, arbitration, clock gating, local range, rate-limit, indirect gateway, error capture, and memory-initialization registers. It contains no functions, types, or executable control flow.

The map starts at `mmTPC0_QM_GLBL_CFG0` address `0xE08000` and ends at `mmTPC0_QM_GLBL_MEM_INIT_BUSY` address `0xE08D00`. Bitfield layout is defined by the paired `tpc0_qm_masks.h` header.

## Important APIs, Types, And Macros

The global register block starts with enable/stop/protection/error configuration and security properties at `0xE08000` through `0xE08034`, then status and message-enable registers through `0xE08068`. It exposes five secure and five non-secure property registers, five status/message-enable channels, and shared global queue state.

Producer queue addresses cover four PQ lanes: base low/high, size, producer index, consumer index, cfg0/cfg1, ARUSER, and status registers. This region runs roughly from `0xE08070` through `0xE0810C` and is used to back command queue storage and doorbell updates.

Completion queue addresses cover five CQ lanes: config, ARUSER, status, pointer low/high, target size, control, status copies of pointer/size/control, and internal FIFO counts. The CQ region starts at `0xE08110` and extends through `0xE08224`.

Command processor addresses cover five CP channels for four message base address pairs, LDMA offsets, four fence read-data and count groups, CP status, current instruction low/high, barrier config, debug, and ARUSER/AWUSER fields. This region spans `0xE08228` through `0xE08440`.

The arbitration block starts at `0xE08A00` and contains arbiter config, choice queue control, WRR weights, clear, 32 master available-credit registers, credit increment, 32 choice push offsets, slave/master controls, message AWUSER/security properties, base addresses, state/fullness/status registers, error cause/message-enable/drop status, and 32 master credit status registers. Later singleton blocks map clock-gating manager registers, local range, CSMR strict priority, HBW/LBW rate limits, global AXCACHE, indirect gateway APB registers, global error capture registers, and memory-init busy.

## Control Flow And State

There is no control flow in the header. These constants name hardware state locations. Driver code writes them to initialize and control the queue manager and reads them for status, debug, and error handling. Hardware updates many of these locations asynchronously as queues drain, command processors fetch commands, fences progress, arbitration credits change, clock-gating state changes, and errors are captured.

Gaudi initialization code uses these addresses to program PQ bases/sizes/indices, CP LDMA offsets and message bases, error registers, arbiter watchdogs, protection, and queue enables. Submission code selects PQ producer-index addresses as doorbells. Monitoring code maps CQ pointer/status registers and PQ consumer indices. Error paths read global status and arbitration error registers and examine CP status/fence fields.

## Dependencies And Integration Points

The header has no compile-time dependency beyond the include guard, but it is semantically coupled to `tpc0_qm_masks.h`. It integrates with register-access helpers and Gaudi per-instance offset logic. `TPC_QMAN_OFFSET` is derived from TPC queue-manager base differences so the TPC0 map acts as the base template for all TPC QMAN instances.

Important integration points include command queue allocation and initialization, PQ doorbell dispatch, CQ mmap/status reporting, CP fence monitoring, MMU ASID property programming, queue-manager stop/reset flows, error reporting, clock-gating configuration, and debug collection. The same address families appear in Gaudi code paths for initialization, reset, command submission, MMU preparation, interrupt/error handling, and idle checks.

## Risks And Edge Cases

The constants are hardware ABI. A wrong address can corrupt unrelated queue-manager state or cause MMIO faults. The risk is highest for producer indices, queue bases/sizes, global enable/stop registers, security properties, CP message bases, fence counters, and arbitration controls.

The register map is not fully contiguous. There are visible gaps before the arbitration block and around selected singleton registers, so generic register dumping or validation must use the explicit macro list rather than assuming every offset is valid. Repeated regions have different lane counts: four PQs, five CQs/CPs, and 32 arbitration master-credit entries. Code that assumes one lane count everywhere can read or write the wrong address.

Some generated names preserve hardware-generator spelling such as `CHOISE`; renaming would break consumers. The map is also used as a base for offsetting other TPC instances, so TPC0 layout mistakes propagate beyond TPC0.

## Test Signals

Compile tests should resolve all `mmTPC0_QM_*` references in Gaudi code. Generator tests should compare the address map against the hardware specification and verify strides for PQ, CQ, CP, and arbitration arrays.

Runtime signals include successful QMAN initialization without MMIO faults, correct command submission through PQ producer indices, CQ status updates at expected addresses, CP fence and current-instruction reporting, expected queue stop/flush behavior, ASID/security properties taking effect, idle checks observing global and clock-gating status, and error handlers reading the intended `GLBL_STS1`, `ARB_ERR_CAUSE`, and global error capture registers.
