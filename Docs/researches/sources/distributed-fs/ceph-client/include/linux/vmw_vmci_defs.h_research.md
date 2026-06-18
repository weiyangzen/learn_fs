# sources/distributed-fs/ceph-client/include/linux/vmw_vmci_defs.h

## Purpose
`vmw_vmci_defs.h` defines VMware VMCI register offsets, capability bits, resource IDs, handle formats, error codes, ioctl values, datagram/event/queue-pair message layouts, callback types, and queue-header helpers. It is the ABI and internal shared-definition header for the VMCI driver and its clients.

## Important APIs, Types, and Functions
The header defines PCI/MMIO register offsets (`VMCI_STATUS_ADDR`, `VMCI_CONTROL_ADDR`, data in/out registers, capability registers), status/control/capability/interrupt bits, interrupt vector indexes, queue-pair memory limits, doorbell limits, BAR layout constants, and DMA datagram structures `vmci_data_in_out_header` and `vmci_sg_elem`. Resource and identity definitions include reserved resource IDs, `struct vmci_handle`, `vmci_make_handle()`, invalid/anonymous handles, context IDs, and `VMCI_CONTEXT_IS_VM()`. It enumerates VMCI success/error codes, event IDs and validators, privilege flags, version macros, and ioctl numbers. Data structures cover `vmci_queue_header`, `vmci_datagram`, event payloads/messages, resource query messages, notification bitmap messages, doorbell link/unlink/notify messages, queue-pair alloc/detach messages, and opaque `struct vmci_qp`. Inline helpers include handle equality/invalid checks, event payload accessors, queue pointer read/write/add helpers, queue header producer/consumer accessors, initialization, free-space calculation, and ready-byte calculation.

## Control Flow
VMCI device code reads capabilities, configures interrupts, and uses register or DMA datagram paths depending on device features. Clients address resources by `(context, resource)` handles. Datagrams carry source/destination handles and payload size. Events are datagrams with typed payloads. Queue pairs use two queue headers: each endpoint advances its producer tail and consumer head while reading peer header fields to compute free/ready bytes. `vmci_q_header_free_space()` detects corrupt head/tail values and preserves one empty byte to distinguish full from empty.

## State and Persistence
The header defines formats for in-memory shared state: queue headers shared with peer/device, datagram buffers, notification bitmap links, event messages, and resource handles. Register state is device state, not durable persistence. Queue pointer helpers use `READ_ONCE` and `WRITE_ONCE`, with 32-bit x86 special handling to avoid expensive or unsafe 64-bit atomics for values that fit in 32 bits.

## Dependencies and Integration Points
Dependencies include atomics, bit macros, page size, ioctl encoding, endian/alignment assumptions, and VMCI driver internals. Integration points include PCI/MMIO VMCI device handling, VMware hypervisor calls, userspace ioctls, VMCI sockets, queue-pair transport, doorbells, notification bitmaps, and event handling.

## Risks
This header is ABI-sensitive. Changing ioctl numbers, struct layout, alignment, or error codes can break VMware userspace or hypervisor compatibility. Queue pointer arithmetic must wrap correctly and detect corruption. A comment notes big-endian concern in `vmci_q_set_pointer()`. Capability-dependent DMA datagram flow must honor busy/result ownership. Limits guard against memory pressure and DoS; relaxing them changes host exposure.

## Test Signals
Signals include VMCI device capability probing, interrupt vector setup, register and DMA datagram send/receive, ioctl compatibility tests, queue-pair wraparound/free-space/ready-byte tests, event payload alignment checks, doorbell bitmap operations, 32-bit x86 builds, and compatibility with existing VMware products.
