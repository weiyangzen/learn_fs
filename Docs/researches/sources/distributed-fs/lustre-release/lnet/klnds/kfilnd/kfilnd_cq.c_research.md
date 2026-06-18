<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.c_research.md`.

Purpose: drains kfabric completion queues and translates provider completion/error records into kfilnd transaction events or immediate-buffer reposts.

Important APIs/types/functions: `kfilnd_cq_process_error()` maps `kfi_cq_err_entry` flags to `TN_EVENT_*` and statuses. `kfilnd_cq_process_event()` maps successful `kfi_cq_data_entry` completions. `kfilnd_cq_process_completion()` drains events and error queues. `kfilnd_cq_completion()` is the KFI CQ callback that queues per-CPT work. `kfilnd_cq_alloc()` and `kfilnd_cq_free()` manage CQ objects.

Control flow: provider callback queues one work item per CPU in the endpoint CPT, optionally skipping the provider's signaling-vector CPU when `prov_cpu_exclusive` is set. Work repeatedly calls `kfi_cq_read()`, handles `-KFI_EAVAIL` by draining `kfi_cq_readerr()`, processes successful events, exits on `-EAGAIN`, and flushes endpoint replay queues if pending. Immediate receive completions call `kfilnd_tn_process_rx_event()` and repost/release multi-receive buffers; tagged/RMA/send completions call `kfilnd_tn_event_handler()`.

State and persistence behavior: each `struct kfilnd_cq` persists for an endpoint lifetime and owns flexible-array work items bound to CPT CPUs. It does not persist completion history; transaction and endpoint state are updated synchronously by event handlers.

Dependencies and integration: depends on KFI CQ APIs, endpoint replay helpers, transaction event handler, immediate-buffer handling, workqueues, CPT CPU masks, and byte-order conversion for remote CQ data status.

Risks: exact flag combinations drive event classification; provider changes can trip `LBUG()`. `kfilnd_cq_free()` flushes the global workqueue before closing the CQ, which can affect unrelated endpoint work. Error status is negated from provider errno and must match transaction health semantics. Remote CQ data is interpreted as big-endian absolute errno.

Test signals: generate send, receive, tagged receive, RMA read/write, cancel, and error completions; inject fake errors from fail locations; test `prov_cpu_exclusive`; verify replay flush after `-EAGAIN`; and run teardown while CQ work is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_cq.c -->
