# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq_copy.h

## Purpose

`vnic_wq_copy.h` defines FNIC copy work queue state and inline helpers for FCPIO host request descriptor management.

## Important APIs, types, and data

- `VNIC_WQ_COPY_MAX` declares a single copy WQ.
- `struct vnic_wq_copy` stores queue identity, device, WQ control MMIO pointer, DMA ring, producer index, and consumer index.
- `vnic_wq_copy_desc_avail()` and `vnic_wq_copy_desc_in_use()` expose descriptor ownership.
- `vnic_wq_copy_next_desc()` returns the next `struct fcpio_host_req` descriptor.
- `vnic_wq_copy_post()` advances producer state, decrements availability, applies a write barrier, and writes `posted_index`.
- `vnic_wq_copy_desc_process()` and `vnic_wq_copy_service()` return descriptors through a completed index or all outstanding descriptors.

## Control flow

Callers fill the next FCPIO descriptor, post it, and later process completions by completed index. The service helper optionally invokes a callback for each descriptor and advances `to_clean_index` until it reaches the completion or catches up to `to_use_index` when called with `(u16)-1`.

## State and persistence behavior

The queue is a ring with one reserved descriptor, tracked through `ring.desc_avail`, `to_use_index`, and `to_clean_index`.

## Dependencies and integration points

It depends on `vnic_wq.h` for control-register layout and `fcpio.h` for descriptor types. It integrates copy WQ submission with copy CQ completion handling.

## Risks and edge cases

- The service helper increments availability itself; callers must not also call `vnic_wq_copy_desc_process()` for the same completion.
- `(u16)-1` is a sentinel for clean-all, so real completion indexes must never be confused with it.
- Descriptor memory ordering depends on the barrier in `vnic_wq_copy_post()`.

## Test signals

Tests should exercise descriptor availability, wraparound, clean-all behavior, callback invocation order, and producer/consumer synchronization.
