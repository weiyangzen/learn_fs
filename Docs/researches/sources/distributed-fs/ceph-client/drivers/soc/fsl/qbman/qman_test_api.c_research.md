# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test_api.c

## Purpose
Functional test of the QMan frame queue API. It creates a dynamic local FQ, enqueues synthetic frame descriptors, validates volatile and scheduled dequeue paths, retires and takes the FQ out of service, and destroys it.

## Important APIs, types, and functions
`qman_test_api` drives the scenario. `fd_init`, `fd_inc`, and `fd_neq` build and compare deterministic `struct qm_fd` values. `do_enqueues` repeatedly calls `qman_enqueue`. Callback functions `cb_dqrr`, `cb_ern`, and `cb_fqs` validate dequeue order and retirement messages. Static waitqueue flags `retire_complete` and `sdqcr_complete` synchronize async callbacks with the main test.

## Control flow and state behavior
The test initializes `fd` and `fd_dq`, creates a dynamic FQ with callbacks, initializes it as local parked, performs a till-empty volatile dequeue, performs a partial volatile dequeue followed by another volatile dequeue for the remaining frames, then schedules the FQ and waits for SDQCR-driven callbacks to drain it. It retires the FQ, waits for FQS callback completion, checks `QMAN_FQ_STATE_BLOCKOOS`, issues OOS, and destroys the FQ. Callback state advances `fd_dq` in lockstep with dequeued frames and wakes the waitqueue when expected conditions are met.

## Dependencies and integration points
Uses exported QMan APIs from `qman.c`, constants from `qman_priv.h` and the public QMan header, and the portal interrupt/polling machinery that invokes DQRR and MR callbacks.

## Risks and test signals
The test assumes callbacks arrive and frame descriptors are preserved except for PPID. If an enqueue fails because EQCR has no space, the core API may still return `0`, weakening this test's ability to detect congestion. Strong signals are waitqueue completion, no `WARN_ON`, matching FD sequence, and successful retire/OOS/destroy.
