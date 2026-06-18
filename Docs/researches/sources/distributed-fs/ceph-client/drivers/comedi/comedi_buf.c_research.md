# sources/distributed-fs/ceph-client/drivers/comedi/comedi_buf.c

## Purpose

`comedi_buf.c` implements COMEDI asynchronous data buffers. It allocates page-backed or DMA-coherent ring buffers, tracks mmap lifetime, supports producer/consumer reservation and release, performs optional sample munging, and exports helper APIs for low-level drivers and file operations.

## APIs And Flow

`struct comedi_buf_map` is kref-backed and stores page metadata, DMA direction, page count, and DMA hardware device reference. `comedi_buf_alloc()` resizes under `dev->mutex`; `comedi_buf_map_from_subdev_get()` and `comedi_buf_map_access()` support mmap; `comedi_buf_is_mmapped()` prevents unsafe resize. Write APIs allocate/free producer space and munge newly written bytes; read APIs expose munged readable bytes. Sample helpers clamp to full samples, copy across page boundaries, update scan progress, set `COMEDI_CB_BLOCK`, and set overflow events when writers overrun.

## State, Dependencies, Risks, Tests

Persistent state is in `struct comedi_async`: prealloc size, counters, pointers, scan and munge progress, and events. Memory barriers order data and counter visibility; mmap refs keep old pages alive. Dependencies include DMA APIs, page allocation/reservation, vmalloc, spinlocks, krefs, and run-state helpers from `comedi_fops.c`. Risks include busy/mmapped resize, DMA-disabled builds, partial-sample munging, barrier bugs, wraparound copy bugs, and overflow handling. Test read/write async commands, mmap, DMA/non-DMA buffers, raw and munged data, wraparound, overflow, and close/cancel with outstanding refs.
