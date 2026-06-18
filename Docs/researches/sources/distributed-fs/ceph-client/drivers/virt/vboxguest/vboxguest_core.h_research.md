# sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_core.h

## Purpose
`vboxguest_core.h` is the private shared interface between the VirtualBox Guest core, the Linux PCI/misc/input wrapper, and the utility/HGCM implementation. It defines the driver state objects, session state, ABI compatibility ioctl constants, and internal function prototypes.

## Important APIs, types, and functions
Key types are `struct vbg_mem_balloon`, `struct vbg_bit_usage_tracker`, `struct vbg_dev`, and `struct vbg_session`. `vbg_dev` owns the VMMDev I/O port/MMIO mapping, host version/features, event/HGCM wait queues, pending event state, request buffers, input device, memory balloon, session/capability tracking, heartbeat timer, and two miscdevices. `vbg_session` tracks per-open HGCM clients, event filters, acquired/set capabilities, requestor flags, and waiter cancellation. Prototypes expose core lifecycle, ioctl dispatch, ISR, Linux mouse callback, request allocation/submission, and compat HGCM calls.

## Control flow
The header’s structure mirrors runtime ownership: `vboxguest_linux.c` allocates/fills `vbg_dev`, calls `vbg_core_init`, registers IRQ and miscdevices, then hands per-open ioctls to `vbg_core_ioctl`. `vboxguest_utils.c` uses the declared helpers to allocate DMA32 request packets and execute HGCM calls against the `vbg_dev` transport.

## State and persistence
All state declared here is in-memory driver state. The header documents which fields are protected by `event_spinlock`, `session_mutex`, or `cancel_req_mutex`; the balloon pages and heartbeat request survive only while the PCI device is bound.

## Dependencies and integration points
It includes Linux input, interrupt, miscdevice, wait, workqueue, and list APIs, the UAPI `linux/vboxguest.h`, and the VMMDev protocol header. It is the coupling point for the core, Linux bus wrapper, and HGCM utility code.

## Risks and test signals
Risks are ABI compatibility drift in the `_ALT` ioctl numbers, incorrect lock assumptions around shared fields, stale prototypes when core/helper behavior changes, and lifetime issues for exported `vbg_get_gdev` consumers that dereference `vbg_dev`. Test signals include allmodconfig builds, compat ioctl builds, lockdep under concurrent sessions, and loading related VirtualBox modules such as vboxsf against the exported device handle.
