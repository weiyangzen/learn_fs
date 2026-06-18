# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sysfs.h

`sysfs.h` declares b43 sysfs registration helpers for device lifecycle code.

It forward-declares `struct b43_wldev` and exposes `b43_sysfs_register(struct b43_wldev *dev)` and `b43_sysfs_unregister(struct b43_wldev *dev)`. The implementation creates and removes the `interference` sysfs attribute.

There is no control flow, state, or persistence in the header itself. It integrates b43 initialization/teardown code with `sysfs.c`, which uses Linux device attributes.

Risks are lifecycle-contract risks: unregister should be paired only with successful registration, and declarations must stay in sync with implementation. Test signals include b43 build coverage plus runtime checks that the sysfs file appears after initialization and disappears after removal.
