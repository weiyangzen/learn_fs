<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.c_research.md`.

Purpose: provides the main kfabric LND integration with LNet: module init/exit, NI startup/shutdown, send/receive entry points, tunable netlink export, and device-priority lookup.

Important APIs/types/functions: global `kfilnd_wq` and `kfilnd_debug_dir`; LNet callbacks `kfilnd_startup()`, `kfilnd_shutdown()`, `kfilnd_send()`, `kfilnd_recv()`, `kfilnd_tun_defaults()`, `kfilnd_nl_get()`, `kfilnd_nl_set()`, and `kfilnd_get_dev_prio()`; hello helper `kfilnd_send_hello_request()`; `the_kfilnd` registration; `kfilnd_init()` and `kfilnd_exit()`.

Control flow: init creates debugfs, validates tunables, initializes libcfs and transaction mempools, creates the workqueue, then registers the LND. Startup validates LND type, applies tunables, requires one interface string, allocates a kfabric device, records device CPT, and posts immediate receive buffers. Sends classify LNet ACK/GET/PUT/REPLY as immediate or bulk based on size, routing, and GPU buffers, allocate a transaction/key, trigger hello if needed, copy immediate payloads or map bulk buffers, then enter the transaction state machine. Receives complete immediate payload copies or set up target-side bulk RMA and feed transaction events.

State and persistence behavior: runtime state lives under `struct kfilnd_dev` in `ni->ni_data`, per-peer hello state, per-transaction buffers/status, debugfs entries, and the module workqueue. Module parameters and NI tunables determine provider version, auth key, traffic class, credits, and timeout. No durable state is stored.

Dependencies and integration: depends on LNet `struct lnet_lnd`, LNet message/finalization APIs, kfilnd transaction/device/tunable helpers, debugfs, workqueues, kfabric provider headers, GPU detection via `lnet_md_is_gpu()`, and netlink attribute helpers.

Risks: the immediate send path returns `-EFAULT` on failed copy without freeing the allocated transaction, which deserves review. The receive default case notes a TODO leak. Hello throttling can delay or cancel sends to new/stale peers. GET reply creation and bulk buffer mapping must be unwound correctly on errors. Module init has an error path after `libcfs_setup()` that may not mirror all setup steps.

Test signals: register/unregister LND, startup with missing/wrong interface, immediate ACK/PUT/GET/REPLY traffic, bulk PUT/GET including GPU buffers, hello negotiation with new/stale peers, netlink get/set of kfilnd tunables, shutdown with live receives, and fail-location tests for allocation/copy/map errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.c -->
