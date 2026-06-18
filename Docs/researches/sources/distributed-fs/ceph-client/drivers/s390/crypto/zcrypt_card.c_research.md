# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_card.c

Purpose: implements common zcrypt AP card device helpers: sysfs attributes, online/offline propagation, reference counting, allocation/free, and registration/unregistration in the global zcrypt card list.

Important APIs and functions: `type_show()` exposes the card type string. `online_show()` reports online only when the AP card is configured, not checkstopped, and zcrypt online is set. `online_store()` validates requested state, rejects online for unavailable cards, updates `zc->online`, emits AP uevents, and force-updates child queues. It collects queue references under `zcrypt_list_lock` and sends queue uevents after releasing the spinlock. `load_show()` reports `atomic_t load`. `zcrypt_card_alloc()` initializes list heads and kref. `zcrypt_card_get()`/`zcrypt_card_put()` manage lifetime. `zcrypt_card_register()` adds to `zcrypt_card_list`, marks online, and creates sysfs attributes. `zcrypt_card_unregister()` removes sysfs/list membership and drops the final reference.

Control flow: AP card-specific drivers allocate and populate `struct zcrypt_card`, then call register. Userspace writes `online`; queue online state is forced accordingly and events are sent. Unregister removes visibility before releasing object references.

State and persistence: persistent runtime state includes global card-list membership, `zc->online`, load, request count, and child queue list. The online flag is not stored across driver reloads.

Dependencies and integration: depends on zcrypt global list/lock, AP card device state, queue helpers, sysfs, krefs, and AP online uevents. It is used by zcrypt message-type card drivers rather than by userspace directly.

Risks: online propagation crosses spinlock and sleepable uevent contexts, so reference collection must be correct. Register error paths must remove list entries if sysfs creation fails. Online state combines AP hardware state and zcrypt user state; tests should avoid treating `zc->online` alone as availability.

Test signals: card allocation/free kref balance, sysfs attribute creation failure, online write validation, checkstopped/configured transitions, child queue force-online propagation, uevent emission, list removal, and concurrent status reads during unregister.
