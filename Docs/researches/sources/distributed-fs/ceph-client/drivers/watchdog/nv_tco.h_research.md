# sources/distributed-fs/ceph-client/drivers/watchdog/nv_tco.h

## Purpose
`nv_tco.h` defines the NVIDIA TCO register offsets and chipset-specific control bits used by `nv_tco.c`.

## Important APIs, types, and functions
The header provides address macros `TCO_RLD`, `TCO_TMR`, `TCO_STS`, `TCO_CNT`, and `MCP51_SMI_EN`, plus bit definitions for boot/timeout status, status reset masks, halt control, TCO reboot enable, and TCO SMI enable bits.

## Control flow
There is no executable control flow. The macros are expanded by the TCO driver to reload, configure, stop/start, detect reset cause, clear status, disable SMI, and adjust reboot behavior.

## State and persistence
The header describes hardware state only. `TCO_STS` bits can survive warm boots; `TCO_CNT_TCOHALT`, SMI enable, and reboot-enable bits alter live chipset behavior.

## Dependencies and integration points
It is private to `nv_tco.c` and depends on callers using a valid TCO base derived from chipset PCI config.

## Risks and test signals
Risks are incorrect base arithmetic, especially `MCP51_SMI_EN(base)` subtracting the TCO offset, and stale bit definitions for newer chipsets. Test signals are compile coverage, PCI hardware probe, status clear verification, halt/start behavior, and SMI/reboot bit readback.
