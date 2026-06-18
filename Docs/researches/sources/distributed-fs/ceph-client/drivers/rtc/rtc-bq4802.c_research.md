# sources/distributed-fs/ceph-client/drivers/rtc/rtc-bq4802.c

## Purpose
TI BQ4802 platform RTC driver supporting either I/O port or memory-mapped register access. It provides basic read/set time only.

## Important APIs, types, and functions
- `struct bq4802` stores mapped memory or I/O base, an RTC device, a spinlock, resource pointer, and polymorphic `read`/`write` callbacks.
- `bq4802_read_io/write_io()` and `bq4802_read_mem/write_mem()` abstract register access for IORESOURCE_IO and IORESOURCE_MEM.
- `bq4802_read_time()` locks, sets the update-transfer bit in register `0x0e`, reads time/date/century registers, restores control, unlocks, then converts BCD to `rtc_time`.
- `bq4802_set_time()` converts `rtc_time` to BCD, locks, enables update mode, writes seconds/minutes/hours/day/month/year/century, restores control, and unlocks.
- `bq4802_probe()` allocates state, selects resource mode, maps memory when needed, stores driver data, and registers the RTC using `devm_rtc_device_register()`.

## Control flow
Probe determines the register access path from the platform resource and installs the same `rtc_class_ops` regardless of transport. Runtime calls are short critical sections protected by `spin_lock_irqsave()`.

## State and persistence behavior
Time and century persist in BQ4802 hardware registers. The driver has no alarm or NVRAM interface and maintains no persistent software state. The spinlock protects multi-register snapshots and programming sequences.

## Dependencies and integration points
Depends on platform resources, I/O accessors, RTC class, BCD helpers, and optional memory mapping. It binds through platform alias `"rtc-bq4802"` and driver name `"rtc-bq4802"`.

## Risks
- No explicit range metadata, so century math relies on raw hardware values and RTC core defaults.
- Memory resources are mapped with `devm_ioremap()` rather than `devm_ioremap_resource()`, so resource ownership/conflict checking is minimal for MMIO.
- There is no oscillator validity check or alarm handling.

## Test signals
Probe with both I/O and MMIO resources, read/write round trips across century boundaries, concurrent read/set stress for lock coverage, and faulted resource configurations.
