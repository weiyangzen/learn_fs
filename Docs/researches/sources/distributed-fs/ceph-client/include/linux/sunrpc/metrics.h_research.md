# sources/distributed-fs/ceph-client/include/linux/sunrpc/metrics.h

Purpose: declares per-operation RPC client I/O metrics exposed mainly through procfs for monitoring tools.

Important APIs and types: `RPC_IOSTATS_VERS` is `"1.1"`. `struct rpc_iostats` contains a spinlock, operation/transmission/timeout counters, byte counters, queue/RTT/execution time accumulators, and error status counts, cacheline-aligned. Procfs-enabled APIs allocate/free metrics, count task I/O stats, count timing metrics, and show client stats.

Control flow: RPC tasks update the per-procedure metrics after transmission and completion under the metrics lock. Consumers sample the cumulative counters and compute rates or moving averages externally.

State and persistence: metrics are per-client runtime counters and are intentionally not reset during a mount/client lifetime. Disabled procfs builds compile to no-op stubs.

Dependencies and integration points: integrates with `rpc_task`, `rpc_clnt`, `seq_file`, locks, and ktime. Monitoring tools such as iostat-style consumers rely on stable field meaning.

Risks and test signals: risks include counter lock contention, overflow assumptions in long-lived clients, procfs-disabled behavior differences, and changing field semantics. Test with procfs enabled/disabled, high RPC rates, error paths, and stats output parsers.
