# sources/distributed-fs/ceph-client/drivers/block/sunvdc.c

## Purpose
Implements the Sun LDOM virtual disk client driver. It binds to VIO `vdc-port` devices, negotiates a VIO/LDC virtual disk connection, creates a blk-mq disk, maps requests into LDC descriptor-ring cookies, and recovers from LDC resets.

## Important APIs, types, and functions
- `struct vdc_port` is the central per-port state: VIO driver state, disk, completion, request id/sequence, descriptor ring request array, transfer limits, media attributes, blk-mq tag set, and reset work.
- Handshake functions: `vdc_send_attr()`, `vdc_handle_attr()`, `vdc_handshake_complete()`.
- Event and ring handling: `vdc_event()`, `vdc_ack()`, `vdc_end_one()`, `__vdc_tx_trigger()`, `vdc_alloc_tx_ring()`, `vdc_free_tx_ring()`.
- I/O path: `vdc_queue_rq()` and `__send_request()` map blk requests to `vio_disk_desc` entries and trigger peer notification.
- Generic control operations use `generic_request()` for flush, write-cache, geometry, VTOC, SCSI, and devid style commands.
- Probe/remove/reset: `vdc_port_probe()`, `probe_disk()`, `vdc_port_remove()`, `vdc_ldc_reset()`, `vdc_requeue_inflight()`, and reset timer/work handlers.

## Control flow
Module init creates a workqueue, registers block major `vdisk`, and registers the VIO driver. Probe filters duplicate mpgroup ports, allocates a `vdc_port`, initializes VIO state, allocates LDC and exported descriptor ring, performs the VIO handshake, probes disk capacity/media, allocates blk-mq disk, and adds it. Queueing starts a request, checks drain and ring space, maps sg entries with correct LDC permissions, fills the current descriptor, uses a write barrier before marking it ready, triggers the peer, and advances the producer index. ACK events unmap cookies, free descriptor slots, end requests, and restart stopped queues. Reset stops queues, requeues inflight requests, tears down LDC/ring state, reallocates, and restarts handshake.

## State and persistence behavior
Runtime state is per VIO port. Descriptor-ring producer/consumer indices, request pointers, request ids, negotiated disk attributes, and reset timers are in memory only. The block disk persists for the bound VIO device lifetime. `drain` gates queue behavior during prolonged link-down handling.

## Dependencies and integration points
Depends on SPARC VIO/LDC APIs, machine description properties, Linux blk-mq, scatterlist mapping, CD-ROM ioctls for virtual optical media, workqueues, timers, and block queue limits. It integrates with firmware-described `vdc-port` devices and peer LDOM virtual disk servers.

## Risks and test signals
- `vdc_nack()` is unimplemented, so peer NACK behavior may leave requests unresolved.
- Descriptor ring exhaustion and LDC reset races require stress testing with queue depth 512, link flaps, and timeout-driven drain.
- `generic_request()` notes missing TX ring exhaustion handling.
- Test protocol versions 1.0/1.1/1.2, CD/DVD ioctl paths, mpgroup duplicate detection, media reserved cases (`vdisk_size == -1` or missing physical block size), and reset recovery with inflight I/O.
