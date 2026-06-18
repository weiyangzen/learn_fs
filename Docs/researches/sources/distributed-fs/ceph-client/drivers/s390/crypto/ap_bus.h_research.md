## sources/distributed-fs/ceph-client/drivers/s390/crypto/ap_bus.h

Purpose: defines the AP bus public/internal contract for card, queue, zcrypt, pkey, and VFIO AP code. It centralizes AP constants, response codes, state-machine enums, device structures, driver callbacks, message format, permissions, and exported helper prototypes.

Important APIs/types/functions: defines `struct ap_driver`, `struct ap_device`, `struct ap_card`, `struct ap_queue`, `struct ap_message`, `struct ap_perms`, AP response constants, AP device types CEX4-CEX8, queue state enums, and exported helpers for driver registration, message allocation, queuing/cancel/flush, queue usability, APQN lookup, mask parsing, binding completion, and uevents.

Control flow: drivers register with `ap_driver_register()` using match ids and optional callbacks. Request users allocate/fill `ap_message`, set `receive`, call `ap_queue_message()`, and receive completion in tasklet context. Bus code invokes queue state-machine events and driver callbacks during scans.

State and persistence: structures reveal the core persistent state: per-card hardware info and counters; per-queue qid, device state, config/checkstop flags, SE bind state, list counts, timeout timer, reply buffer, and state-machine state; global permission bitmaps.

Dependencies and integration: depends on Linux device model/hashtable and s390 AP/ISC definitions. It is shared by `ap_bus.c`, `ap_card.c`, `ap_queue.c`, zcrypt, pkey, and VFIO AP.

Risks and test signals: risks are ABI-like structure expectations across modules, queue receive callbacks running in tasklet context, and endianness of inverted AP masks. Test build coverage across all consumers, queue lifecycle transitions, APQN lookup reference counts, and mask parser behavior.
