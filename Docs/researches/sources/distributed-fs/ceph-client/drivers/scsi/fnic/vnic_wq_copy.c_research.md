# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq_copy.c

## Purpose

`vnic_wq_copy.c` implements allocation, initialization, enable/disable, cleanup, and release of the FNIC copy work queue used for FCPIO host requests.

## Important APIs, types, and functions

- `vnic_wq_copy_alloc()` binds a copy WQ to a normal WQ resource, disables it, and allocates a coherent descriptor ring.
- `vnic_wq_copy_init()` programs ring base/size, fetch/posted indexes, CQ index, error interrupt settings, and error status.
- `vnic_wq_copy_enable()`/`vnic_wq_copy_disable()` control hardware execution.
- `vnic_wq_copy_clean()` services outstanding descriptors with an optional cleaner, resets indexes/status, and clears descriptor memory.
- `vnic_wq_copy_free()` releases the descriptor ring.

## Control flow

The copy WQ uses index-based state rather than a per-descriptor buffer metadata array. Producers fill `struct fcpio_host_req` descriptors through the inline helper and post them. Completion/cleanup advances `to_clean_index` and restores descriptor availability.

## State and persistence behavior

Software state is `to_use_index`, `to_clean_index`, and `ring.desc_avail`. Hardware state is the shared WQ control block for ring base/size, posted/fetch, enable/running, CQ, and error fields.

## Dependencies and integration points

It depends on `vnic_wq_copy.h`, `vnic_dev_alloc_desc_ring()`, and WQ MMIO register definitions. It is integrated with FNIC FCPIO request submission.

## Risks and edge cases

- Disable timeout returns `-ENODEV`, unlike normal WQ/RQ timeout paths that return `-ETIMEDOUT`.
- Cleaning requires the queue to be disabled and warns through `BUG_ON()` if not.
- Allocation uses `RES_TYPE_WQ`, so index ownership must not conflict with normal WQs.

## Test signals

Tests should cover copy WQ descriptor posting, completion cleanup, disable timeout logging, reset cleanup with outstanding descriptors, and queue-index assignment.
