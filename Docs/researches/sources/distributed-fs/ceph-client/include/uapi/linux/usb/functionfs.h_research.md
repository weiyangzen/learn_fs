# sources/distributed-fs/ceph-client/include/uapi/linux/usb/functionfs.h

Purpose: Defines the FunctionFS userspace gadget ABI for supplying descriptors/strings, receiving control events, endpoint ioctls, and DMABUF-backed transfers.

Important APIs/types/functions: Magic values identify descriptor and string blocks, with v2 descriptor flags for FS/HS/SS descriptors, MS OS descriptors, virtual addresses, eventfd, all-control-recipient handling, and config0 setup. Structs include endpoint descriptor without audio fields, DFU functional descriptor, v2 and legacy descriptor headers, MS OS descriptor headers, extended compatibility/property descriptors, `usb_functionfs_strings_head`, `usb_functionfs_event`, and `usb_ffs_dmabuf_transfer_req`. Ioctls expose FIFO status/flush, clear halt, interface/endpoint reverse mapping, endpoint descriptor retrieval, and DMABUF attach/detach/transfer.

Control flow: Userspace mounts FunctionFS, writes descriptor and string blobs to ep0, reads bind/enable/setup/suspend/resume events from ep0, handles setup data phases, and performs I/O on endpoint files. Optional DMABUF flow attaches a dma-buf fd to an endpoint and enqueues it for transfer.

State and persistence behavior: Function state is tied to the FunctionFS instance, descriptor upload, gadget binding, endpoint enablement, and open endpoint file descriptors. Attached DMABUFs are automatically detached when endpoint descriptors close.

Dependencies and integration points: Includes USB chapter 9 definitions and Linux ioctl/types. Integrates with configfs gadget composition, USB gadget controller drivers, DFU, Microsoft OS descriptors, eventfd, and dma-buf.

Risks: Descriptor blobs are variable-layout and endian-specific; unrecognized v2 flags are rejected. Setup direction controls data phase ordering. DMABUF lifetime and endpoint shutdown races must be handled carefully.

Test signals: Mount FunctionFS and enumerate FS/HS/SS gadgets, validate v2/legacy descriptor parsing, string language tables, setup/event sequencing, endpoint reverse mapping, halt/fifo ioctls, DMABUF attach/transfer/detach, and malformed descriptor fuzzing.
