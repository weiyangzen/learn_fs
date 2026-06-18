# sources/distributed-fs/ceph-client/drivers/hv/ring_buffer.c

## Purpose
`ring_buffer.c` implements Hyper-V VMBus ring buffer management for guest-to-host and host-to-guest packet exchange. It initializes double-mapped ring storage, writes outbound packets with Hyper-V-compatible signaling, reads inbound packets through a private iterator, exposes ring debug information, and carefully enforces memory ordering around shared indices.

## Important APIs, types, and functions
The file operates on `struct hv_ring_buffer_info`, `struct hv_ring_buffer`, `struct vmbus_channel`, `struct vmpacket_descriptor`, `struct hv_ring_buffer_debug_info`, and scatter/gather `struct kvec` input.

Exported functions include `hv_ringbuffer_get_debuginfo()`, `hv_ringbuffer_pre_init()`, `hv_ringbuffer_init()`, `hv_ringbuffer_cleanup()`, `hv_ringbuffer_spinlock_busy()`, `hv_ringbuffer_write()`, `hv_ringbuffer_read()`, `hv_pkt_iter_first()`, `__hv_pkt_iter_next()`, and `hv_pkt_iter_close()`.

## Control flow
Initialization builds a `pages_wraparound` array where the data pages are mapped twice after the header page, allowing linear copies across wrap boundaries. The mapping uses encrypted or decrypted page protections depending on confidential VMBus mode. The ring data size excludes the header page; feature bit 0 enables pending-send flow control.

Outbound writes reject rescinded channels, sum vector lengths plus the trailer, lock `outbound.ring_lock`, check available space, copy all vectors, allocate or derive the transaction ID, write `desc->trans_id` with `WRITE_ONCE()`, append previous indices, issue `virt_mb()`, update `write_index`, release the lock, and signal when the ring transitioned from empty to non-empty.

Inbound reads use `priv_read_index` as an iterator. `hv_pkt_iter_first()` uses acquire semantics on `write_index`, validates packet length/offset from shared memory, copies the packet into `pkt_buffer`, sanitizes descriptor fields, and returns the private copy. `hv_pkt_iter_close()` commits `priv_read_index` and signals the host only for pending-send unblock transitions.

## State and persistence behavior
The ring object holds persistent shared indices (`read_index`, `write_index`, `pending_send_sz`, `interrupt_mask`) plus kernel-only state (`ring_datasize`, `ring_size`, reciprocal sizing metadata, `priv_read_index`, `pkt_buffer`, locks). The host can update inbound ring memory concurrently, so inbound packet descriptors are copied and sanitized before use.

## Dependencies and integration points
This file integrates with VMBus channel state and callbacks, Hyper-V event signaling through `vmbus_setevent()`, architecture memory-barrier helpers, vmap/vunmap page mappings, confidential VMBus page protections, debug-delay hooks, and channel metrics consumed by sysfs in `vmbus_drv.c`.

## Risks
The dominant risks are memory-ordering mistakes, host/guest shared-memory races, and off-by-one errors in ring full/empty detection. Inbound packet metadata comes from the host and may change concurrently; losing the copy/sanitize pattern would expose callers to inconsistent packet lengths or offsets. `hv_ringbuffer_init()` can fail after `vmap()` succeeds if `pkt_buffer` allocation fails, so callers must clean up to avoid a mapped-ring leak. Incorrect signaling can trigger performance loss or host throttling.

## Test signals
Tests should exercise wraparound writes/reads, exact-full rejection, empty-to-nonempty signaling, pending-send unblock signaling, rescind behavior before and after write, invalid inbound packet length/offset sanitization, confidential and non-confidential mapping protections, debug info snapshots, and cleanup after partial initialization failures.
