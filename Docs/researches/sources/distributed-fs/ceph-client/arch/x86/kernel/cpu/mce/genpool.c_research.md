# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/genpool.c

Purpose: supplies a lockless, preallocated event pool for MCE records captured in machine-check context, where normal allocation and printk paths are unsafe.

Important APIs and flow: `mce_gen_pool_init()` lazily creates a `gen_pool` sized to at least 80 records or two records per possible CPU. `mce_gen_pool_add()` filters vendor-ignored records, allocates a node, copies the `mce_hw_err`, and pushes it onto a lockless list. `mce_gen_pool_process()` drains and reverses the list in workqueue context, calls the MCE decoder notifier chain for each record, and frees nodes back to the pool. `mce_gen_pool_prepare_records()` is panic-path support that drains records, reverses them into chronological order, and drops duplicates before console printing.

State and persistence: global state is the fixed gen_pool and lockless event list. Records persist only until processed, panic-dumped, or lost due to pool exhaustion.

Dependencies and integration: used by `mce_log()`, MCE workqueue processing, panic dumping, vendor filters, and decoder notifier consumers.

Risks and test signals: pool exhaustion can drop records, while duplicate suppression relies on bank/status/address/misc comparison. Signals include injection bursts, panic-path duplicate logs, notifier ordering, and pool-full ratelimited warnings.
