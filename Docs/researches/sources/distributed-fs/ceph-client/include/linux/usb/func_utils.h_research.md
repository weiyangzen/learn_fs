<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/func_utils.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/func_utils.h

Purpose: provides utility macros and request allocation helpers for USB gadget function drivers.

Important APIs and types: VLA layout macros `vla_group`, `vla_group_size`, `vla_item`, `vla_item_with_sz`, and `vla_ptr` compute aligned offsets and total sizes for packed variable-length allocations with overflow detection. `alloc_ep_req()` allocates a gadget endpoint request and buffer, with OUT endpoint buffer length aligned to maxpacket. `free_ep_req()` frees the buffer and request.

Control flow: function drivers compute one allocation layout using VLA macros, allocate storage, derive typed subobject pointers with `vla_ptr()`, allocate endpoint requests with `alloc_ep_req()`, and release them with `free_ep_req()`.

State and persistence: VLA macros produce local offset/size variables. USB request state lives in allocated `struct usb_request` objects and buffers until freed.

Dependencies and integration points: depends on USB gadget API and overflow helpers. It integrates with composite gadget function implementations that need compact dynamic descriptors or request buffers.

Risks and test signals: risks include using VLA offsets after overflow set total size to `SIZE_MAX`, mismatched free paths, buffer length assumptions for OUT endpoints, and `WARN_ON` if freeing a request with a null buffer. Test variable-size allocation overflow, alignment of generated layouts, request allocation/free under endpoint maxpacket variants, and error unwind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/func_utils.h -->
