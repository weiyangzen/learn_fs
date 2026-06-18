# sources/distributed-fs/ceph-client/drivers/rapidio/switches/idt_gen2.c

## Purpose
RapidIO switch driver for IDT CPS Gen2 devices. It supplies switch-specific route-table operations, domain configuration, error-management initialization/handling, and an `errlog` sysfs attribute.

## Important APIs, types, and functions
`idtg2_route_add_entry/get_entry/clr_table()` implement route programming using local route-table select and standard route CSRs, translating `RIO_INVALID_ROUTE` to device default/no-route values. `idtg2_set_domain/get_domain()` access `IDT_RIO_DOMAIN`. `idtg2_em_init()` configures port-write based error reporting across LT, port, lane, auxiliary, and config-block facilities. `idtg2_em_handler()` clears implementation-specific L/T and port error records. `idtg2_show_errlog()` drains `IDT_ERR_RD` into sysfs. `idtg2_probe/remove()` attach/detach `idtg2_switch_ops` and create/remove sysfs state.

## Control flow
The driver registers a `rio_driver` at `device_initcall`. Probe takes the switch lock, refuses to replace existing ops, stores `idtg2_switch_ops`, disables default routing during enumeration, releases the lock, and creates `errlog`. Core enumeration and route APIs call these ops through `rio_route_*()` and `rio_init_em()`. Removal verifies the ops pointer before clearing it and removing sysfs.

## State and persistence
Persistent hardware state includes route tables, default route behavior, switch domain, port-write/error-reporting enable bits, log-overwrite policy, TVAL, and cleared error capture registers. Kernel state is limited to the ops pointer and sysfs attribute.

## Dependencies and integration
Depends on RapidIO core switch ops, IDT device IDs, config-space accessors, delay helpers, and the Linux device attribute API. It is selected by `CONFIG_RAPIDIO_CPS_GEN2`.

## Risks
Sysfs `errlog` reads consume the hardware log. Error init writes many broadcast and per-port/per-lane implementation-specific registers and assumes Gen2 layout and lane count by DID. Route clear only covers 8-bit extended config entries. Probe creates sysfs after releasing the switch lock and does not unwind ops if sysfs creation fails.

## Test signals
Probe/remove on all IDs, route add/get/clear including invalid routes and per-port tables, domain set/get, enumeration default-route disable, EM initialization register writes, implementation-specific error clearing, and `errlog` behavior with empty and full logs.
