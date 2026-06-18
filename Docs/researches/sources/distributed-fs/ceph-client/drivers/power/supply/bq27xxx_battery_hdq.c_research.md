# sources/distributed-fs/ceph-client/drivers/power/supply/bq27xxx_battery_hdq.c

Purpose: adapts the shared BQ27xxx battery core to HDQ/1-wire BQ27000-style devices. It registers a 1-wire family, creates a `bq27xxx_device_info` for each slave, and supplies a read-only HDQ bus callback to the core.

Important APIs/types/functions: `w1_bq27000_read()` performs the low-level HDQ read command under the 1-wire master bus mutex. `bq27xxx_battery_hdq_read()` reads one-byte or stable two-byte registers, retrying when high-byte samples change. `bq27xxx_battery_hdq_add_slave()` and `bq27xxx_battery_hdq_remove_slave()` bridge 1-wire add/remove events to `bq27xxx_battery_setup()` and teardown. `bq27xxx_battery_hdq_family` supplies `w1_family_ops`; `F_ID` can override the default family ID.

Control flow: module init optionally replaces the family ID, then registers with the w1 core. When a matching slave appears, add allocates device info, sets chip type `BQ27000`, names it `bq27000-battery`, installs only the read callback, and invokes shared setup. Reads issue HDQ command bytes; two-byte reads sample upper/lower/upper until the upper byte is stable or retries expire. Module exit unregisters the family.

State and persistence: driver-local state is limited to the optional family ID parameter and per-slave devm allocation. All battery cache and polling state is owned by `bq27xxx_battery.c`. The HDQ adapter provides no write or block operations, so persistent data-memory updates are not available through this path.

Dependencies and integration: depends on the 1-wire subsystem, `w1_slave`/`w1_family`, and the shared BQ27xxx core. It has a module alias for the default BQ27000 family ID.

Risks and test signals: two-byte consistency relies on only three high-byte retries; fast-changing registers can return `-EIO`. The low-level read returns an unsigned byte and cannot distinguish all bus-level failures from valid `0xff`; the core has a BQ27000-specific flags check for `0xff`. Test family-ID override, add/remove lifecycle, stable and unstable two-byte reads, absent write support, polling teardown, and 1-wire bus mutex behavior under concurrent reads.
