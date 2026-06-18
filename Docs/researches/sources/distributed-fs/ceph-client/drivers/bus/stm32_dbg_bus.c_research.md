# sources/distributed-fs/ceph-client/drivers/bus/stm32_dbg_bus.c

## Purpose
This STM32 debug bus driver exposes an OP-TEE mediated firewall controller that grants or denies debug-bus access based on secure firmware policy, then populates permitted debug-bus children.

## Important APIs, Types, and Functions
`struct stm32_dbg_bus` stores the TEE client device and OP-TEE context. `stm32_dbg_pta_open_session()` and `stm32_dbg_pta_close_session()` manage PTA sessions. `stm32_dbg_bus_grant_access()` invokes `PTA_CMD_GRANT_DBG_ACCESS` with either `PERIPHERAL_DBG_PROFILE` or `HDP_DBG_PROFILE`. `stm32_dbg_bus_plat_probe()` registers a `struct stm32_firewall_controller` and calls `stm32_firewall_populate_bus()`. Separate TEE and platform drivers are registered from one module init path.

## Control Flow
The TEE client probe opens an OP-TEE context and installs a singleton `stm32_dbg_bus_priv`. The platform probe defers until that singleton exists, then registers the firewall controller, filters children through the common STM32 firewall bus helper, enables runtime PM, and populates children. The TEE remove path closes the context and depopulates TEE children.

## State and Persistence
The singleton `stm32_dbg_bus_priv` enforces one debug bus instance. Access decisions are not cached by this driver; each grant opens a TEE session and invokes secure firmware. Release is a required no-op callback.

## Dependencies and Integration Points
It depends on OP-TEE client APIs, the STM32 firewall framework exported by `stm32_firewall.c`, OF platform population, and runtime PM. Its DT compatibles are STM32MP131 and STM32MP151 debug bus nodes, and its TEE service is identified by a fixed UUID.

## Risks and Test Signals
Risks include singleton ordering, context lifetime coupling between TEE and platform devices, missing unregister on some platform-probe failure paths, and secure firmware returning access denial. Test signals include deferred probe until OP-TEE is ready, expected `-EACCES` on forbidden profiles, children detached when access is denied, and no stale singleton after TEE remove.
