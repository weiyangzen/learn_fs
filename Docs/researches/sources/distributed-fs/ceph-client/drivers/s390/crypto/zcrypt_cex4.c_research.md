# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex4.c

## Purpose
`zcrypt_cex4.c` registers AP bus card and queue drivers for CEX4 through CEX8 crypto hardware. It normalizes device metadata for accelerator, CCA coprocessor, and EP11 personality modes, attaches zcrypt card/queue objects, selects the right message type implementation, and exposes CCA/EP11 sysfs attributes.

## Important APIs, Types, And Functions
The module exports init/exit through `zcrypt_cex4_init()` and `zcrypt_cex4_exit()`. Internal probes are `zcrypt_cex4_card_probe()` and `zcrypt_cex4_queue_probe()`, with matching remove functions. Sysfs show routines include CCA serial and MKVP views plus EP11 API ordinal, firmware version, serial number, operational modes, wrapping-key verification patterns, and queue op modes. AP device ID tables match CEX4, CEX5, CEX6, CEX7, and CEX8 card and queue devices.

## Control Flow
On module init, the card driver is registered first; the queue driver is registered second, and card registration is unwound on queue-driver failure. Card probe allocates a `zcrypt_card`, stores it as driver data, classifies hardware via `ac->hwinfo.accel`, `cca`, or `ep11`, assigns type strings, user-space compatibility type, speed-rating tables, and RSA modulus limits, then calls `zcrypt_card_register()`. Depending on personality, it creates a CCA or EP11 card sysfs group. Queue probe allocates a `zcrypt_queue`, selects message type 50 for accelerators, type 6 default for CCA, or type 6 EP11 variant for EP11, initializes AP queue state/reply buffer and timeout, registers the queue, and adds matching queue sysfs attributes.

## State And Persistence
State is kernel-resident device state: `zcrypt_card`, `zcrypt_queue`, sysfs attributes, AP queue timeout, online flag, load counter, and speed tables. No on-disk persistence exists. Remove paths unregister sysfs groups and zcrypt objects.

## Dependencies And Integration Points
This file integrates the AP bus with zcrypt core (`zcrypt_card_*`, `zcrypt_queue_*`), message handlers (`zcrypt_msgtype50`, `zcrypt_msgtype6`), CCA info helpers, EP11 info helpers, and sysfs. Compatibility mappings intentionally report newer CEX7/CEX8 and CCA cards as older user-space types for legacy ioctl behavior.

## Risks And Test Signals
Risks include incorrect hardware-personality classification, sysfs group leaks on partial failure, stale speed ratings, and compatibility type regressions. Test signals include AP hotplug probe/remove, sysfs attribute reads on CCA and EP11 devices, queue operation routing by hardware mode, failure injection around `sysfs_create_group()`, and module init unwind when queue driver registration fails.
