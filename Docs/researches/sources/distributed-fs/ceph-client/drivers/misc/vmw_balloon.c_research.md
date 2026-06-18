# sources/distributed-fs/ceph-client/drivers/misc/vmw_balloon.c

## Purpose
`vmw_balloon.c` is VMware's guest memory balloon driver. It communicates with the VMware hypervisor through the backdoor I/O port to inflate and deflate guest memory, supports batched and 2 MB balloon operations, optional VMCI doorbell wakeups, optional shrinker-based memory pressure relief, debugfs statistics, and balloon page migration.

## Important APIs, Types, and Functions
`struct vmballoon` holds target/current size, capabilities, batching page, page lists, work item, locks, VMCI doorbell, balloon migration info, and optional shrinker/stats. Hypervisor commands are sent with `__vmballoon_cmd()` and `vmballoon_cmd()`, with setup helpers `vmballoon_send_start()`, `vmballoon_send_guest_id()`, and `vmballoon_send_get_target()`. Page lifecycle is handled by `vmballoon_alloc_page_list()`, `vmballoon_lock()`, `vmballoon_inflate()`, `vmballoon_deflate()`, `vmballoon_pop()`, `vmballoon_enqueue_page_list()`, and `vmballoon_dequeue_page_list()`. Batching and VMCI helpers are `vmballoon_init_batching()`, `vmballoon_deinit_batching()`, `vmballoon_vmci_init()`, and `vmballoon_vmci_cleanup()`. Periodic control is `vmballoon_work()`. Optional hooks include `vmballoon_shrinker_scan()`, `vmballoon_debug_show()`, and `vmballoon_migratepage()`.

## Control Flow
Late init verifies the VMware hypervisor, initializes balloon state, optional shrinker, balloon migration info, locks, doorbell handle, and queues the worker immediately. The worker resets the protocol when required, negotiates capabilities, initializes batching if available, registers VMCI doorbell, sends guest ID, then periodically gets the host target and inflates or deflates toward it. Inflation allocates pages at the largest supported size, sends lock commands to the host, enqueues accepted pages, splits refused 2 MB pages down to 4 KB candidates, and stops on allocation/lock limits. Deflation dequeues pages, optionally unlocks them with the host, frees accepted pages, and returns refused pages to the balloon. VMCI doorbells reschedule the worker immediately when host target changes. Exit disables shrinker/debugfs/doorbell, resets host capabilities to zero, and pops all pages without coordinated unlock.

## State and Persistence
The singleton `balloon` keeps volatile target/current size, reset flag, negotiated capabilities, batch communication page, huge-page list, standard balloon page list, shrink timeout, stats pointer, and VMCI handle. The host's balloon target is refreshed through backdoor commands. Ballooned pages are marked offline and held until deflation; there is no durable persistence across unload or reboot.

## Dependencies and Integration Points
The driver depends on x86 VMware hypervisor detection, VMware backdoor port I/O, VMCI doorbell APIs, Linux balloon compaction/migration infrastructure, memory allocation and page offline flags, delayed work on `system_freezable_wq`, static keys, debugfs, shrinker APIs, and module parameters. It aliases VMware DMI and `vmware_vmmemctl`.

## Risks and Edge Cases
Backdoor command failures can set `reset_required`, causing asynchronous protocol reset. 2 MB pages are kept out of migration lists, while 4 KB pages integrate with balloon migration. Shrinker-driven deflation delays later inflation to avoid churn. Batching state uses a static key, so reset paths must keep `batch_page`, `batch_max_pages`, and host capabilities consistent. Exit calls `vmballoon_send_start()` after worker cancellation but without a guaranteed successful reset path if the host is gone. Page migration can deflate the old page and fail to inflate the new page, intentionally shrinking the balloon by one frame.

## Test Signals
Validate VMware-only init, start capability negotiation for basic/batched/2 MB/64-bit targets, periodic target polling, inflation and deflation size accounting, refused-page splitting, host reset recovery, VMCI doorbell wakeups, shrinker deflation and inflation delay, debugfs stat enabling/output, balloon migration outcomes, suspend-freezable work behavior, and unload returning all pages.
