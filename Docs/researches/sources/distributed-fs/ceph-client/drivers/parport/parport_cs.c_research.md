# sources/distributed-fs/ceph-client/drivers/parport/parport_cs.c

## Purpose
`parport_cs.c` is a PCMCIA wrapper for PC-style parallel-port cards, originally targeting Quatech SPP-100 EPP-class adapters. It allocates PCMCIA resources and delegates actual port probing/unregistration to `parport_pc`.

## Important APIs, Types, and Functions
The local state type is `parport_info_t`, holding the `pcmcia_device`, number of registered ports, and `struct parport *`. `parport_probe()` allocates state and starts configuration. `parport_config_check()` requests 8-bit I/O windows. `parport_config()` loops CIS configs, enables the card, calls `parport_pc_probe_port()`, and marks EPP capabilities if requested. `parport_cs_release()` unregisters and disables the card. `parport_cs_driver` binds PCMCIA IDs.

## Control Flow
Probe allocates `link->priv`, sets `CONF_ENABLE_IRQ | CONF_AUTO_SET_IO`, then configures. Configuration optionally sets `FORCE_EPP_MODE`, requests I/O, requires an IRQ, enables the PCMCIA device, probes a PC-style parport at resource windows 0 and 1, and records success. Remove calls release and frees private state.

## State and Persistence
State is per-card heap memory referenced by `link->priv`; runtime hardware/resource state is managed through PCMCIA core and `parport_pc`. The module parameter `epp_mode` controls EPP forcing and advertised modes.

## Dependencies and Integration Points
The driver depends on PCMCIA core APIs, CIS IDs, `parport_pc_probe_port()`, and `parport_pc_unregister_port()`. It integrates PCMCIA hotplug with the parport PC low-level implementation.

## Risks
The failure path in `parport_config()` calls `parport_cs_release(link)` and frees `link->priv`; `parport_detach()` also frees `link->priv`, so probe-time failure handling must be reviewed against PCMCIA core expectations to avoid double-free or stale private data. The driver assumes two I/O windows and an IRQ. `epp_mode` may advertise EPP/TRISTATE on cards that do not behave like the original target.

## Test Signals
Hotplug tests should cover resource allocation, no-IRQ rejection, successful `parport_pc_probe_port()`, EPP-mode flagging, card removal, and probe failure paths under allocation or I/O request failure.
