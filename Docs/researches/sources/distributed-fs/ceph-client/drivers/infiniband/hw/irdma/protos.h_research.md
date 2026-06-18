# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/protos.h

## Purpose
`protos.h` declares lower-level shared-control prototypes used across IRDMA control, HMC, queue, stats, VSI, work scheduler, termination, and CQP code. It also defines thresholds for pause/PFC and CQP completion waits.

## Important APIs, types, and functions
Important constants include `PAUSE_TIMER_VAL`, `REFRESH_THRESHOLD`, traffic-control thresholds, `CQP_COMPL_WAIT_TIME_MS`, `CQP_TIMEOUT_THRESHOLD`, and `CQP_DEF_CMPL_TIMEOUT_THRESHOLD`. Prototypes cover device initialization, CQP WQE handling, fast MR registration, HMC/FPM setup, stats commands, CEQ/AEQ commands, VSI initialization and stats, L2 parameter changes, QP suspend/resume, termination, HMC page allocation notification, feature query, bottom-half processing, SDS commands, FPM buffer allocation, HMC function management, and device refcount helpers.

## Control flow, state, and persistence
The header has no flow, but it defines cross-module call edges. Many routines mutate persistent `irdma_sc_dev`, `irdma_sc_vsi`, CQP, HMC, stats, and QP state in implementation files outside this subset.

## Dependencies and integration points
It is included by HMC, PBLE, hardware, and control files to avoid circular declarations. It bridges `hw.c` orchestration with low-level `ctrl.c`, `utils.c`, work scheduler, stats, and termination implementations.

## Risks and test signals
Risks include stale prototypes, hidden cross-file dependencies, and timeout constants that affect CQP reliability. Test signals include compile coverage, CQP timeout/deferred completion tests, FPM query/commit validation, stats gather tests, and QP suspend/resume behavior during TC changes.
