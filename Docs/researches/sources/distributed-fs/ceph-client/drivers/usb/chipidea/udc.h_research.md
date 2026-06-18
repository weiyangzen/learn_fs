# sources/distributed-fs/ceph-client/drivers/usb/chipidea/udc.h

Purpose: defines the private DMA descriptor and request wrapper contract used by the ChipIdea UDC implementation. It is the narrow interface between generic gadget request objects and the hardware queue-head/transfer-descriptor format programmed by `udc.c`.

Important APIs, types, and constants: `CTRL_PAYLOAD_MAX` fixes EP0 max packet size at 64 bytes. `RX` and `TX` provide internal direction indexes. `struct ci_hw_td` mirrors a hardware transfer descriptor with `next`, `token`, and five page pointers plus status, IOC, active, halted, data-error, transaction-error, byte-count, mult, terminate, and address masks. `struct ci_hw_qh` mirrors a queue head with capability bits (`QH_IOS`, `QH_MAX_PKT`, `QH_ZLT`, `QH_MULT`), current TD pointer, overlay TD, reserved word, and setup packet storage. `struct td_node` wraps a DMA TD in a kernel list node and tracks remaining packed scatterlist room. `struct ci_hw_req` wraps `struct usb_request`, its endpoint queue link, TD list, and optional saved scatter-gather table used when bouncing.

Control flow: the header itself has no active control flow, but its layouts govern `udc.c` allocation, TD chaining, QH priming, setup-packet copying, completion decoding, and cleanup. When `CONFIG_USB_CHIPIDEA_UDC` is enabled it declares `ci_hdrc_gadget_init` and `ci_hdrc_gadget_destroy`; otherwise inline stubs make callers fail cleanly with `-ENXIO` and no-op destruction.

State and persistence: all state is volatile DMA or heap memory allocated by the controller driver. The packed/aligned attributes are part of the ABI to hardware and must remain stable. `ci_hw_req.sgt` preserves the original scatterlist only while a bounced request is in flight.

Dependencies and integration points: includes list infrastructure and relies on Linux USB request/control-request and DMA types from surrounding includes. It is consumed by the ChipIdea UDC implementation and indirectly by the ChipIdea core when registering the gadget role.

Risks: the main risks are layout drift, incorrect endian or alignment assumptions, and stale bit masks causing hardware-visible descriptor corruption. Test signals are mostly indirect: successful gadget enumeration, EP0 setup handling, DMA transfer completion, scatter-gather transfer tests, and build coverage with `CONFIG_USB_CHIPIDEA_UDC=y/m/n`.
