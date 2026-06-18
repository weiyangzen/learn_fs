# sources/distributed-fs/ceph-client/net/sunrpc/stats.c

## Purpose
`stats.c` provides procfs and seq_file reporting for generic SUNRPC client and server statistics, plus per-operation RPC I/O metrics collection for completed client tasks.

## Important APIs, Types, And Functions
Important APIs include `svc_seq_show()`, `rpc_alloc_iostats()`, `rpc_free_iostats()`, `rpc_count_iostats_metrics()`, `rpc_count_iostats()`, `rpc_clnt_show_stats()`, `rpc_proc_register()`, `rpc_proc_unregister()`, `svc_proc_register()`, `svc_proc_unregister()`, `rpc_proc_init()`, and `rpc_proc_exit()`. Internal helpers print client procedure counters, aggregate per-op metrics up parent client chains, and create proc entries under `/proc/net/rpc`.

## Control Flow
Client proc reads call `rpc_proc_show()`, which prints network counters, RPC counters, and per-version procedure counts from `rpc_stat`. Server stats call `svc_seq_show()`, which sums per-CPU service procedure counters. When an RPC task completes, `rpc_count_iostats_metrics()` locks the operation metrics, increments operation/transaction/timeout/error counters, accumulates sent/received bytes and queue/RTT/execute times, and emits latency trace data. `rpc_clnt_show_stats()` prints transport stats and aggregated per-operation metrics.

## State And Persistence
Persistent state is owned by callers: `rpc_stat`, `svc_stat`, per-version count arrays, per-CPU server procedure counters, and per-client `rpc_iostats` arrays. This file allocates and frees metrics arrays and creates per-net proc directory entries through `sunrpc_net->proc_net_rpc`.

## Dependencies And Integration Points
The file integrates with procfs, seq_file, RPC client and server program metadata, transport stat printers, `rpc_clnt_iterate_for_each_xprt()`, per-CPU counters, spinlocks, ktime, tracepoints, and network namespace proc directories initialized by the SUNRPC pernet lifecycle.

## Risks And Edge Cases
The opening comment warns that proc output must fit within PAGE_SIZE when service-specific routines append generic stats. Metrics accounting assumes `om_ops` does not exceed `om_ntrans`, forcing at least one transaction per operation. Callers must pass a valid stat index and initialized metrics array. Parent-chain aggregation in `rpc_clnt_show_stats()` depends on sane `cl_parent` links and matching procedure layouts.

## Test Signals
Useful tests include `/proc/net/rpc` directory creation/removal per net namespace, client and server proc output formatting, per-procedure counter increments, metrics allocation/free, error/timeout/byte accounting after RPC completion, parent client metric aggregation, transport stat printing, and tracepoint validation for latency accounting.
