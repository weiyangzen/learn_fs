## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_uvc.h

Purpose: declares configfs/legacy option state for the USB Video Class gadget function.

Important APIs and types:
- `fi_to_f_uvc_opts()` converts a function instance to `f_uvc_opts`.
- `struct f_uvc_opts` embeds `usb_function_instance`, streaming interval/maxpacket/maxburst, interface numbers, function name, last unit ID, interrupt endpoint enable flag, descriptor pointer arrays for control/streaming at full/high/super speed, default camera/processing/output terminal descriptors, configfs-owned control descriptor arrays, extension unit list, dynamically allocated streaming descriptor arrays, string descriptor indexes, `lock`, `refcnt`, and legacy-only `header`.

Control flow and integration:
- Configfs builds UVC control and streaming descriptor trees into the arrays in this options object.
- Legacy gadgets may override descriptor pointer arrays and use `header`.
- Bind consumes descriptors, interface numbers, endpoint parameters, and strings to instantiate `struct uvc_device` in `uvc.h`.

State and persistence:
- Descriptor pointers and allocated arrays persist while the function instance exists.
- `last_unit_id` coordinates descriptor unit IDs as configfs extension units are added.
- `refcnt` blocks mutation while functions are instantiated.

Dependencies:
- USB composite, USB video descriptor definitions, mutexes, and UVC implementation/configfs descriptor code.

Risks:
- Descriptor arrays are pointer-heavy and partially dynamic; cleanup must free only owned arrays and keep legacy overrides intact.
- Interface numbers and string indexes must stay consistent with composite allocation.
- `streaming_maxpacket`/`maxburst` must be valid for selected speeds and endpoint capabilities.

Test signals:
- Build UVC configfs trees with multiple formats/frames and extension units, bind/unbind, and verify descriptor arrays and host enumeration.
- Stream video at configured endpoint sizes and test interrupt endpoint enable/disable.
