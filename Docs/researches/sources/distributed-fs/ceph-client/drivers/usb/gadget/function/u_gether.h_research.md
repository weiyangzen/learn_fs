## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_gether.h

Purpose: defines option storage for the CDC subset/generic Ethernet gadget function.

Important APIs and types:
- `struct f_gether_opts` embeds `usb_function_instance`, associated `net_device`, legacy/shared `bound` flag, `bind_count`, `lock`, and `refcnt`.

Control flow and integration:
- The subset function uses this options object to coordinate configfs instance lifetime with the shared `u_ether` netdev.
- Binding increments `bind_count`; unbinding decrements and unregisters/cleans the netdev only when the last binding is gone.

State and persistence:
- Per-instance in-memory configfs state. `net` usually persists across individual `usb_function` allocations.

Dependencies:
- USB composite and the shared Ethernet utility implementation.

Risks:
- Same lifecycle imbalance risks as ECM/EEM: double registration, stale netdev pointers, and live configfs mutation if `lock`/`refcnt` checks are missed.

Test signals:
- Create subset gadget, configure MAC/qmult/ifname before bind, run network traffic, and unbind/rebind repeatedly.
