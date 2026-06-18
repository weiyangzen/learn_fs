# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip_network.h

Purpose: `usbip_network.h` defines the userspace usbip protocol PDUs and networking helper API.

Important types and constants: `struct op_common` contains version, code, and status. Request/reply opcodes are defined for devinfo, import, export, unexport, crypkey, and devlist. PDU structs include import request/reply and devlist reply layouts using `struct usbip_usb_device` and `struct usbip_usb_interface`. Packing macros call byte-order helpers for structs with multi-byte fields.

Control flow and integration: `usbip_attach`, `usbip_list`, and `usbipd` share these definitions to exchange OP_REQ_IMPORT and OP_REQ_DEVLIST messages. Some opcodes are defined but unused by current handlers.

State, dependencies, risks, and tests: it declares global port configuration and socket helpers. It depends on packed common USB structs. Risks include wire ABI coupling to struct packing, empty packing macros for currently byte-neutral structs, unused legacy protocol definitions, and no bounds for variable-length trailing arrays beyond negotiated counts. Test signals are interoperability between `usbip` and `usbipd` built from the same headers and correct network byte order on mixed-endian systems.
