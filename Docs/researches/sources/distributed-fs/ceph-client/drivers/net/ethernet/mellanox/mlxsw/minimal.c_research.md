# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/minimal.c

## Purpose
`minimal.c` is a lightweight mlxsw driver for I2C-attached systems that need front-panel module access without full switch data-plane support. It creates simple Ethernet netdevs for modules, exposes ethtool module EEPROM/power/reset operations, maps modules to local ports, and responds to line-card activation/inactivation.

## Important APIs, Types, and Functions
- `struct mlxsw_m` stores core/bus references, base MAC, port table, slot/module topology, and line-card mapping arrays.
- `struct mlxsw_m_port` is netdev private data tying a netdev to local port, slot, module, and module offset.
- Port operations are `mlxsw_m_port_open()` and `mlxsw_m_port_stop()`, delegating to `mlxsw_env_module_port_up()` / `_down()`.
- Ethtool operations expose driver info, EEPROM, page-based EEPROM read/write, module reset, and module power mode through `core_env` helpers.
- Initialization and teardown are `mlxsw_m_init()` / `mlxsw_m_fini()`, registered through `struct mlxsw_driver`; module init also registers an I2C driver through `mlxsw_i2c_driver_register()`.

## Control Flow
Driver init validates minimum firmware minor/subminor, reads base MAC, allocates topology arrays, registers line-card event callbacks, maps modules to local ports by querying `PMLP`, and creates netdevs for the main board. Each port creation initializes the core port, allocates an etherdev, links it to mlxsw core, derives its MAC from `PPAD`, and registers the netdev. Line-card active callbacks remap ports and create netdevs for that slot; inactive callbacks remove those netdevs and unmap modules. Module exit unregisters the I2C backend and the mlxsw core driver.

## State and Persistence
State is in-memory: `ports[local_port]`, per-slot `module_to_port[]` arrays initialized to `-1`, active flags per slot, and base MAC. Hardware-visible state includes module-to-port maps, module port up/down state, and any EEPROM/power/reset operations requested via ethtool.

## Dependencies and Integration Points
The file depends on the common mlxsw core driver model, I2C bus backend, `core_env` module helpers, devlink line-card events from `core_linecards.c`, netdev registration, and ethtool module APIs. It provides `ports_remove_selected` so line-card unprovisioning can remove ports for one slot.

## Risks
The line-card active flag is used both to skip duplicate mapping and to drive removal assertions; incorrect flag sequencing can leak netdevs or skip new ports. Module offset math assumes uniform maximum modules per line card. `mlxsw_m_port_open()` and `stop()` pass slot `0` in this source for port up/down, while other module operations use `slot_index`; that is a detail to verify against intended hardware semantics. Port mapping skips width-zero and clustered duplicate modules by tracking `last_module`.

## Test Signals
Boot an I2C minimal device and verify firmware compatibility checks, netdev creation for all mapped modules, ethtool EEPROM/page/power/reset operations, line-card hotplug netdev creation/removal, module-to-port unmap on teardown, and clean unwind when a port registration fails mid-slot.
