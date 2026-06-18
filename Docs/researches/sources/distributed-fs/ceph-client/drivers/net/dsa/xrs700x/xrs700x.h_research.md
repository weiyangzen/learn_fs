# sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x.h

Purpose: this header defines the shared data model and exported core lifecycle for XRS700x DSA transport drivers.

Important APIs, types, and functions: `struct xrs700x_info` describes an expected chip ID, name, and port count and is exported for OF match data. `struct xrs700x_port` stores per-port MIB lock, accumulated counter array, stats64 snapshot, and u64 sync primitive. `struct xrs700x` stores the DSA switch, device, transport private pointer, regmap, per-port regmap fields for port state/speed, delayed MIB work, and port array. Public functions allocate, register, remove, and shutdown a switch instance.

Control flow: a bus frontend calls `xrs700x_switch_alloc()`, initializes `priv->regmap`, and then calls `xrs700x_switch_register()`. The core uses the fields declared here to register DSA and later to service callbacks. Remove and shutdown are frontend-facing wrappers.

State and persistence: the header defines all persistent common runtime state but owns no allocations itself. The port array and MIB arrays are allocated by the core after chip detection sets the port count.

Dependencies and integration points: it includes Linux device, mutex, regmap, workqueue, u64 stats, and if_link definitions. It is shared by I2C and other transport frontends plus the common core.

Risks: frontends must set a valid regmap before registration; otherwise detection and regmap-field allocation fail. MIB data is dynamically sized to the static MIB table in the C file, so any table changes must keep allocation and copy sizes synchronized. Transport private data is opaque and must be cast only by the owning frontend.

Test signals: compile all XRS700x transports, allocate/register/remove through each bus, verify per-port MIB allocation for 3- and 4-port variants, and confirm stats synchronization on 32-bit and 64-bit builds.
