## sources/distributed-fs/eos/mgm/balancer/FsBalancer.hh

Purpose: declares `FsBalancer`, the per-space manager that owns a background assisted thread and a transfer thread pool for balancing files between filesystems inside groups. Construction seeds default config (`threshold=10`, two transfers per node, 25 MB/s rate value, 60-second stats interval, 1000 queued jobs, max 100 worker threads) and starts `Balance()`. Destruction calls `Stop()`.

Important APIs: `Stop()`, `SetMaxThreadPoolSize()`, `GetThreadPoolInfo()`, `SignalConfigUpdate()`, `Balance()`, `TakeTxSlot()`, and `FreeTxSlot()`. Private helpers include `ConfigUpdate()`, `GetFileToBalance()`, and templated `GetRandomIter()`, which returns an iterator at a random one-based index.

State behavior: `mDoConfigUpdate` is atomic; `mRunningJobs` is atomic; most other fields are mutated by the balancer thread and task callbacks. `mBalanceStats` owns group and node-transfer caches. Integration is with `FsBalancerStats`, EOS metadata IDs, `common::ThreadPool`, and `AssistedThread`. Risks include thread start in constructor, join in destructor, no explicit restart API, and exposed internals under `IN_TEST_HARNESS`. Tests should validate random iterator bounds, config-update signaling, thread-pool resizing, and that slot accounting stays balanced under asynchronous completion.
