## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ecm.h

Purpose: defines configfs/function-instance option storage for the CDC ECM Ethernet gadget function.

Important APIs and types:
- `struct f_ecm_opts` embeds `usb_function_instance`, points to the shared ECM `net_device`, records whether the netdev is already `bound`, tracks `bind_count`, and protects configfs/refcount state with `lock` and `refcnt`.

Control flow and integration:
- The ECM function allocator creates this options object, usually initializes `net` through `u_ether` helpers, and uses `bind_count` to avoid duplicate netdev registration when the same instance is linked into configurations.
- Configfs attributes and symlink lifecycle use `lock` and `refcnt` to reject changes while active.

State and persistence:
- State is per function instance in kernel memory and persists while the configfs function instance exists.
- `bound` distinguishes legacy/shared netdev ownership from function-local registration.

Dependencies:
- Includes USB composite definitions and integrates with `u_ether.c` via `struct net_device` and `gether_*` helpers in ECM implementation files.

Risks:
- Incorrect `bind_count` or `bound` handling can double-register or prematurely unregister the netdev.
- Configfs writes must hold `lock` and respect `refcnt`; otherwise MAC/queue changes can race function binding.

Test signals:
- Create/remove ECM configfs functions repeatedly, link into multiple configurations, and verify netdev registration count.
- Change dev/host address and qmult only while unbound and confirm `-EBUSY` while active.
