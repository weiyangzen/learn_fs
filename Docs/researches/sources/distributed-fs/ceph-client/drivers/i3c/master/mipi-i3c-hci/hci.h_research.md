# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/hci.h

## Purpose

`hci.h` is the central internal header for the MIPI I3C HCI driver. It defines register bit helpers, MMIO access macros, the main controller structure, the transfer structure shared by command and I/O backends, backend operation vtables, per-device private data, quirk flags, and cross-file function declarations.

## Important APIs, Types, and Functions

- `W0_MASK` through `W3_MASK` and `W*_BIT_` adapt 128-bit descriptor bit positions to 32-bit descriptor words.
- `reg_read()`, `reg_write()`, `reg_set()`, and `reg_clear()` are core-register MMIO helpers assuming a local `hci` variable.
- `struct i3c_hci` persists all core controller state: `i3c_master_controller`, MMIO sections, selected `hci_io_ops`/`hci_cmd_ops`, locks, TID counter, quirks, DAT/DCT metadata, HCI version/vendor IDs, and vendor data.
- `struct hci_xfer` represents a master transfer descriptor plus response, payload, completion, timeout, and backend-specific PIO or DMA linkage.
- `struct hci_io_ops` abstracts PIO and DMA operations including queue/dequeue/error, IBI pool operations, init/cleanup, and PM hooks.
- `struct i3c_hci_dev_data` stores per-device DAT index and IBI backend data.
- Quirk bits model raw CCC, AMD PIO/timing/threshold needs, and runtime PM behavior.

## Control Flow

Core code allocates `hci_xfer` arrays with `hci_alloc_xfer()`, command ops fill descriptors, and I/O ops consume the same structure for queueing and completion. The selected backend stores either PIO linked-list fields or DMA ring fields in the union. Attach callbacks store `i3c_hci_dev_data` on I3C/I2C descriptors, making DAT and IBI state available to later command and IBI paths.

## State and Persistence Behavior

`struct i3c_hci` is device-lifetime state. Its DAT cache and backend `io_data` survive across transfer calls and are restored or reinitialized across PM transitions. `struct hci_xfer` is request-lifetime state and must remain valid until the backend completes or dequeues it.

## Dependencies and Integration Points

The header is included by every HCI implementation file. It integrates with Linux I3C master structures, completions, spinlocks, mutexes, atomic counters, MMIO APIs, PIO/DMA backends, PCI glue PM exports, and AMD quirk helpers.

## Risks and Edge Cases

The PIO/DMA union means a transfer cannot be owned by both backends. MMIO helper macros depend on local variable naming. Device-data `dat_idx` is meaningful mainly for v1 descriptors, so users must account for v2. Quirk combinations affect initialization and PM behavior across several files.

## Test Signals

Compile-time tests should catch structure member drift across all HCI files. Runtime signals include correct backend selection, transfer completion with both union layouts, DAT persistence, quirk-specific register writes, and shared IRQ inactive synchronization.
