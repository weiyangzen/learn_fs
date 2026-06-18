# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp.rs

## Purpose

`gsp.rs` defines runtime data structures for the GSP manager: page constants, log buffers, command queue, LIBOS memory-region arguments, and RM argument storage.

## Important APIs, Types, And Functions

Important items are `GSP_PAGE_SHIFT`, `GSP_PAGE_SIZE`, `PteArray`, `LogBuffer`, `LogBuffers`, and pinned `Gsp`. `LogBuffer::new()` allocates a coherent log buffer and writes self page-table entries. `Gsp::new()` initializes command queue, RM arguments, LIBOS memory-region array, and debugfs log files.

## Control Flow

Construction allocates three log buffers (`LOGINIT`, `LOGINTR`, `LOGRM`), creates a `Cmdq`, builds padded RM arguments from the command queue, allocates one page of LIBOS memory-region descriptors, initializes entries for logs and RMARGS, then exposes log buffers under the module debugfs root using the PCI device name.

## State And Persistence Behavior

`Gsp` owns coherent LIBOS arguments, coherent RM args, a pinned command queue, and a debugfs scope that owns log buffers. These objects persist for the GPU lifetime and are shared with GSP-RM after boot. Log buffer contents are written by firmware and readable through debugfs.

## Dependencies And Integration Points

It depends on coherent DMA, debugfs, PCI device naming, `Cmdq`, GSP firmware ABI wrappers, and page-table entry helpers. `gsp/boot.rs` consumes this runtime object to pass LIBOS and command queue addresses into firmware.

## Risks And Test Signals

Risks include debugfs root lifetime assumptions, log buffer PTE layout, physical contiguity requirements, fixed log buffer size, and keeping RM/LIBOS arguments alive until initialization completes. Test by constructing GSP runtime, reading debugfs logs, validating LIBOS memory-region IDs and DMA addresses, and booting GSP until init-done.
