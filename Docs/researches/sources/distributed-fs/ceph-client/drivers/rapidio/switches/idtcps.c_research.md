# sources/distributed-fs/ceph-client/drivers/rapidio/switches/idtcps.c

## Purpose
RapidIO switch driver for IDT CPS Gen1/CPS-xx switches. It supplies route-table and switch-domain operations for older IDT devices.

## Important APIs, types, and functions
`idtcps_route_add_entry/get_entry/clr_table()` access standard route destination/port select CSRs, while preserving upper bits of the port-select register on add. `CPS_DEFAULT_ROUTE` and `CPS_NO_ROUTE` are translated to `RIO_INVALID_ROUTE` for core route caches. `idtcps_set_domain/get_domain()` access `IDTCPS_RIO_DOMAIN`. `idtcps_probe/remove()` attach/detach `idtcps_switch_ops`.

## Control flow
Probe registers `idtcps_switch_ops` under the switch lock if no ops are already attached. During enumeration, it sets link timeout TVAL and disables default routing by writing `CPS_NO_ROUTE`. Core route APIs and enumeration then invoke the driver-specific ops. Removal clears the ops pointer only if it still points to this driver.

## State and persistence
Hardware state includes route table entries, default route configuration, switch domain, and TVAL. Kernel state is the switch ops pointer.

## Dependencies and integration
Depends on RapidIO core switch ops, IDT Gen1 device IDs, and config-space access helpers. Selected by `CONFIG_RAPIDIO_CPS_XX`.

## Risks
Route clear is fixed to 8-bit entries `0x80000000..0x800000ff`, so it is not a full 16-bit route-table clear. There is no device-specific EM support. Probe assumes `phys_efptr` is valid when setting TVAL.

## Test signals
Probe/remove on every ID, route add/get/clear default/no-route translation, domain set/get, enumeration startup default-route disable, and route behavior in fabrics using Gen1 switches.
