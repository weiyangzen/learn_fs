# sources/distributed-fs/ceph-client/include/uapi/linux/usb/gadgetfs.h

Purpose: Defines the legacy GadgetFS userspace gadget ABI for events and endpoint ioctls.

Important APIs/types/functions: Event types include connect, disconnect, setup, suspend, and nop. `struct usb_gadgetfs_event` carries event type and setup packet for control requests. Endpoint ioctls mirror gadget endpoint controls: FIFO status, FIFO flush, and clear halt.

Control flow: Userspace writes descriptors to ep0, reads gadget events, handles setup requests and data phases, and performs endpoint I/O. Endpoint ioctls inspect or modify endpoint FIFO/halt state.

State and persistence behavior: Gadget state is runtime and tied to open GadgetFS files, descriptor upload, host connection, and endpoint enablement.

Dependencies and integration points: Includes USB chapter 9 definitions; integrates with USB gadget UDC drivers and legacy userspace gadget implementations.

Risks: GadgetFS is older and less structured than FunctionFS. Correct setup direction/data phase handling and descriptor validity are critical.

Test signals: Enumerate a GadgetFS sample gadget, handle setup/suspend/disconnect events, use endpoint FIFO/halt ioctls, and verify behavior across host reset/reconnect.
