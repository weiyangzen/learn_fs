## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_hid.h

Purpose: declares configfs option state and global setup/cleanup APIs for the HID gadget function.

Important APIs and types:
- `struct f_hid_opts` embeds `usb_function_instance` and stores HID minor, subclass, protocol, optional absence of OUT endpoint, report length, report descriptor pointer/length/allocation flag, interrupt interval and user-set flag, plus `lock` and `refcnt`.
- `ghid_setup(struct usb_gadget *g, int count)` and `ghid_cleanup()` initialize/tear down the HID gadget character-device infrastructure for a number of HID instances.

Control flow and integration:
- Configfs writes fill descriptor/protocol/report fields before the function is instantiated.
- HID function bind consumes these options to build descriptors and create the `/dev/hidg*` endpoint interface.
- `report_desc_alloc` tells cleanup whether `report_desc` is owned by the options object.

State and persistence:
- Options persist as long as the configfs function instance exists.
- Minor allocation and character-device infrastructure are global to HID gadget setup.

Dependencies:
- USB composite framework and HID function implementation files.

Risks:
- Report descriptor length/content must match `report_length`; invalid descriptors may enumerate but fail host HID parsing.
- `no_out_endpoint` changes endpoint topology and must match intended report direction.
- Concurrent configfs mutation while bound must be blocked through `lock`/`refcnt`.

Test signals:
- Instantiate keyboard/mouse/custom HID report descriptors, verify host enumeration, IN reports, optional OUT reports, and interval behavior.
- Repeated setup/cleanup should not leak minors or report descriptors.
