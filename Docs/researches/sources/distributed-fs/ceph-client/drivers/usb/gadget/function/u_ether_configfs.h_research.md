## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ether_configfs.h

Purpose: provides macro-generated configfs item operations and attributes shared by USB Ethernet gadget functions.

Important APIs and types:
- `USB_ETHERNET_CONFIGFS_ITEM(_f_)` creates a configfs release callback that converts the item to `f_<name>_opts` and drops the function instance.
- `USB_ETHERNET_CONFIGFS_ITEM_ATTR_DEV_ADDR`, `HOST_ADDR`, `QMULT`, and `IFNAME` generate show/store attributes backed by `gether_*` helpers.
- `USB_ETHER_CONFIGFS_ITEM_ATTR_U8_RW` generates a generic hex u8 read/write attribute for protocol-specific option bytes.

Control flow:
- Function-specific configfs files include this header, instantiate macros for their option type, and include generated `CONFIGFS_ATTR()` objects in attribute arrays.
- Store paths take `opts->lock`; most reject writes when `opts->refcnt` is nonzero, preventing mutation while a function instance is in use.

State and persistence:
- Does not own state itself. It reads/writes fields in `f_*_opts`, mainly the shared `net_device` and qmult/MAC/ifname fields.

Dependencies:
- Requires each function to provide `struct f_<name>_opts`, `to_f_<name>_opts()`, an `opts->lock`, `opts->refcnt`, and usually `opts->net`.
- Depends on configfs, `u_ether.h` helper APIs, and kernel parsing helpers such as `kstrtou8()`.

Risks:
- Macro expansion hides type requirements; compile errors can be hard to trace if an options struct lacks expected fields.
- Generic u8 attribute does not check `refcnt`, unlike qmult/MAC/ifname attributes; function users must choose it only for fields safe to change live or add external protection.
- `QMULT` stores into `u8 val`, limiting accepted qmult to 0..255 even though `gether_set_qmult()` takes `unsigned`.

Test signals:
- For each Ethernet function, read/write generated configfs attributes before binding and verify `-EBUSY` after binding.
- Confirm generated release drops function-instance references exactly once.
- Fuzz invalid MAC, qmult, ifname, and u8 attribute input.
