# sources/distributed-fs/ceph-client/drivers/mfd/mcp-core.c

Purpose: Generic Multimedia Communications Port bus layer. It registers a custom `mcp` bus, wraps MCP host operations with spinlock serialization, manages host device allocation/lifetime, and exposes MCP driver registration helpers.

Important APIs, types, and functions: `mcp_bus_type` has a match function that accepts all devices and probe/remove adapters that call `struct mcp_driver` callbacks. Exported functions include `mcp_set_telecom_divisor()`, `mcp_set_audio_divisor()`, `mcp_reg_write()`, `mcp_reg_read()`, `mcp_enable()`, `mcp_disable()`, `mcp_host_alloc()`, `mcp_host_add()`, `mcp_host_del()`, `mcp_host_free()`, `mcp_driver_register()`, and `mcp_driver_unregister()`.

Control flow: module init registers the bus. A host driver allocates an `mcp` object plus private tailroom, initializes `ops`, then calls `mcp_host_add()`, which publishes a device named `mcp0`. MCP client drivers register through `mcp_driver_register()`, and bus probe calls their `probe(mcp)` function. Operation wrappers spinlock around low-level callbacks.

State and persistence: state lives in `struct mcp`, including use count, spinlock, ops, attached device, and private host data. `mcp_enable()`/`mcp_disable()` maintain a reference-like `use_count` and only toggle hardware on transitions between zero and nonzero.

Dependencies and integration points: depends on `<linux/mfd/mcp.h>` and custom bus infrastructure. It is consumed by host drivers such as `mcp-sa11x0.c` and codec or peripheral MCP drivers.

Risks: `mcp_bus_match()` always returns true, so only one attached device and careful driver registration ordering make this safe. `mcp_disable()` decrements without underflow protection. Register access comments warn that callers must enable the interface first or hardware can hang. Test signals include bus registration, host add/remove, probe/remove callback dispatch, enable/disable reference counts, and lock coverage of all ops.
