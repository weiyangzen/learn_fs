## sources/distributed-fs/ceph-client/drivers/acpi/sbs.c

### Purpose
`sbs.c` implements the ACPI Smart Battery System platform driver. It exposes SBS chargers and up to four smart batteries through the Linux power-supply subsystem using ACPI SMBus host-controller transactions.

### Important APIs, Types, And Functions
The driver defines `struct acpi_sbs`, `struct acpi_battery`, power-supply descriptors and property arrays, `acpi_sbs_probe()`, `acpi_sbs_remove()`, `acpi_sbs_callback()`, battery info/state/alarm helpers, charger helpers, and resume handling. SMBus field readers are described by `struct acpi_battery_reader` arrays.

### Control Flow
Probe obtains the ACPI companion and parent SMBus host-controller data, allocates `acpi_sbs`, registers a charger if charger status is valid, queries the SBS manager unless running on Apple x86, registers all manager-reported battery slots or falls back to battery 0, and registers an SMBus callback. Battery registration selects charge-based or energy-based property sets depending on battery mode, reads static info on presence changes, caches dynamic state for `cache_time`, and registers power supplies with an `alarm` sysfs attribute. The callback updates charger presence and battery presence and emits `power_supply_changed()` notifications. Remove unregisters callback, batteries, charger, and frees state under a mutex.

### State, Persistence, And Dependencies
State is in the allocated `acpi_sbs` and embedded battery array: cached static strings, capacities, state values, update timestamps, presence flags, and charger flags. Dependencies include `sbshc` ACPI SMBus helpers, power-supply core, jiffies caching, Apple platform detection, platform driver binding, and ACPI device IDs.

### Integration Points
The driver binds ACPI HID `ACPI0002` as a platform child of an SBS host controller. Userspace observes `BAT0`-style batteries and `sbs-charger` through power-supply sysfs and uevents.

### Risks
SMBus block reads write directly into fixed-size battery string buffers and rely on host helper behavior respecting `ACPI_SBS_BLOCK_MAX`. Dynamic state is cached even after read failure. Manager selection writes to selector registers before battery reads. Apple systems skip manager probing. Remove assumes valid driver data and serializes only its own teardown, while callbacks depend on host-controller unregister semantics.

### Test Signals
Test charger-present/absent and invalid charger status, manager-present multi-battery systems, no-manager fallback, Apple x86 path, battery insertion/removal callbacks, cache expiration, charge versus energy mode property reporting, alarm show/store, SMBus read/write failures, resume refresh, and module removal during callback activity.
