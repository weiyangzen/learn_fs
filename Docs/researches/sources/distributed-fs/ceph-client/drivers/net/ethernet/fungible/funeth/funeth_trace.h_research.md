# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_trace.h

## Purpose
Defines tracepoints for funeth Tx enqueue, Tx reclaim, and Rx completion handling. These are low-overhead observability hooks for driver data-path debugging.

## APIs and Types
Declares `TRACE_SYSTEM funeth` and three `TRACE_EVENT`s: `funeth_tx`, `funeth_tx_free`, and `funeth_rx`. Events record netdev name, queue index, descriptor index/head, packet length, gather/list counts, hash, and classification vector. It includes `funeth_txrx.h` for queue structures and ends with `<trace/define_trace.h>`.

## Control Flow and Integration
`funeth_tx.c` emits `trace_funeth_tx()` after descriptor construction and `trace_funeth_tx_free()` during reclaim. `funeth_rx.c` defines `CREATE_TRACE_POINTS` before including this header and emits `trace_funeth_rx()` before GRO handoff.

## State and Persistence
Tracepoints do not persist state in the driver. They expose snapshots of queue state and descriptor metadata to ftrace/perf/BPF consumers.

## Dependencies and Risks
Depends on Linux tracepoint infrastructure and correct `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` values for generated trace headers. Risks are mostly build-time include path issues and trace fields reading invalid queue pointers after teardown; current usage is within active datapath code. Test signals include building with tracing enabled and capturing events under Tx/Rx traffic to verify queue names and descriptor indices progress.
