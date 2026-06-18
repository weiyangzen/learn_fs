## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc7_qm_regs.h

### Purpose
`tpc7_qm_regs.h` is the auto-generated register-address map for the queue manager attached to Gaudi TPC engine 7. It exposes host-visible symbols for producer queues, completion queues, command processors, arbitration, rate limiting, error reporting, and clock/power-management status in the TPC7 QM aperture.

### Important APIs, Types, And Functions
The file defines 406 `mmTPC7_QM_*` register addresses from `mmTPC7_QM_GLBL_CFG0` at `0xFC8000` through `mmTPC7_QM_GLBL_MEM_INIT_BUSY` at `0xFC8D00`. The register families include `GLBL_*` configuration/protection/status/error registers, four `PQ_*` producer queues, five `CQ_*` completion queues, five command-processor groups under `CP_*`, a large `ARB_*` arbitration/credit surface, `CGM_*` clock-gating controls, local range registers, rate-limit registers, and indirect gateway registers.

### Control Flow
The header contains no functions. Driver flow writes global enable/protection and error masks, programs PQ/CQ base and pointer registers, updates PI doorbells, uses CP/FENCE status during synchronization, and checks QM/CGM idle bits before reset or power transitions. `gaudi.c` has TPC7-specific references for CP stop, PI doorbell offsets, MMU preparation, and idle handling; `gaudi_security.c` builds register protection tables from these addresses.

### State, Persistence, And Dependencies
The state is the hardware queue-manager state: queue base pointers, producer/consumer indices, CQ pointers, CP message/fence status, arbitration counters, and error-cause/status latches. The constants are consumed through `gaudi_regs.h` and interpreted through masks in generated QM mask headers and composite masks in `gaudi_masks.h`, especially `QMAN_TPC_ENABLE`, `TPC_QMAN_GLBL_ERR_CFG_*`, `QM_IDLE_MASK`, and `CGM_IDLE_MASK`.

### Integration Points
This map is tied to Gaudi's command-submission path. It integrates with `QMAN_PQ_ENTRY_SIZE` and engine counts from `gaudi.h`, packet formats from `gaudi_packets.h`, event IDs such as `GAUDI_EVENT_TPC7_QM`, and reset/idle code in `gaudi.c`. Security policy uses these addresses when making selected queue-manager registers host accessible or protected.

### Risks
Queue-manager registers are sequencing-sensitive. Incorrect PI/CI, base, size, CP, or CQ addresses can corrupt queues or hang command submission. Misprogrammed protection and non-secure property registers can cause MMU violations or accidental privilege changes. Arbiter and error mask definitions must remain synchronized with hardware because stop-on-error and diagnostic paths depend on them after faults.

### Test Signals
Run command submission through TPC7 with all PQs and CQs enabled, exercise queue wraparound, fence completion, CP stop/reset, QM error injection or timeout paths, and idle detection before device reset. Compare TPC7 behavior with other TPC QMs to catch one-instance address drift. Security validation should include protection-bit coverage for the full `0xFC8000` to `0xFC8D00` range.
