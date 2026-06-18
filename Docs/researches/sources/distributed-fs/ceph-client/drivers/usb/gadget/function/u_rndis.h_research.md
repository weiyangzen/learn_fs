## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_rndis.h

Purpose: defines option storage and a netdev borrowing hook for the RNDIS Ethernet gadget function.

Important APIs and types:
- `struct f_rndis_opts` embeds `usb_function_instance`, vendor/manufacturer identity, associated `net_device`, `bind_count`, `borrowed_net`, RNDIS OS descriptor group and descriptor data, class/subclass/protocol bytes, `lock`, and `refcnt`.
- `rndis_borrow_net()` lets a legacy/composite gadget provide a pre-created netdev to an RNDIS function instance.

Control flow and integration:
- RNDIS configfs uses these fields for Microsoft OS descriptors, class codes, and Ethernet attributes.
- Bind uses `borrowed_net` to decide whether the RNDIS function owns netdev registration/cleanup or is sharing a pre-registered netdev.
- The underlying packet transport uses `u_ether` with RNDIS wrap/unwrap callbacks.

State and persistence:
- Per-instance in-memory configfs state. Manufacturer string is a pointer whose lifetime is managed by implementation/configfs.

Dependencies:
- USB composite, configfs, USB OS descriptor support, and shared Ethernet utility.

Risks:
- Windows interoperability depends heavily on OS descriptor compatibility ID and class/subclass/protocol values.
- Incorrect borrowed-net ownership can leak or double-free/register netdevs.
- RNDIS framing allows padding and internal packet boundaries, so `u_ether` buffer sizing and unwrap error handling are important.

Test signals:
- Enumerate RNDIS on Windows/Linux hosts, verify OS descriptor content, MAC addresses, and network traffic.
- Test `rndis_borrow_net()` with legacy multi-function gadgets sharing a netdev.
