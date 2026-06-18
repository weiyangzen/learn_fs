# sources/distributed-fs/ceph-client/drivers/extcon/extcon.h

### Purpose
`extcon.h` is the private extcon core header. It defines the internal layout of `struct extcon_dev` used by the provider implementation while exposing only the fields that provider drivers may initialize before registration.

### Important APIs, Types, And Functions
The only concrete type is `struct extcon_dev`. User-initialized fields are `name`, `supported_cable`, and `mutually_exclusive`. Internal fields include embedded `struct device dev`, numeric `id`, global list `entry`, per-cable and all-cable raw notifier heads, `max_supported`, IRQ-safe `lock`, state bitmask, dynamic `device_type`/cable sysfs group storage, and mutual-exclusion sysfs attribute storage.

### Control Flow, State, And Persistence
The header has no executable code, but it documents the lifecycle contract enforced by `extcon.c`: provider drivers allocate/fill the public fields, `extcon_dev_register()` overwrites internal fields, and consumers should not mutate runtime state directly. The persisted runtime state is in-memory only: attached cable bits in `state`, notifiers registered in `nh`/`nh_all`, global list membership, and sysfs group allocations. `mutually_exclusive` uses bit masks over supported-cable indexes and must be 0-terminated.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on `<linux/extcon-provider.h>` for public extcon IDs and property definitions. It couples tightly to `extcon.c` allocation and free paths because the struct embeds dynamic sysfs group pointers rather than opaque private data. Risks include drivers treating internal fields as stable ABI, setting too many supported cables for the 32-bit mask, or misunderstanding `name` fallback semantics. Test signals are mainly build-time and provider registration behavior: initialized public fields survive registration, internal fields are reset, mutual-exclusion arrays terminate correctly, and unregister frees the dynamic members described here.
