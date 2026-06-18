# sources/distributed-fs/ceph-client/drivers/rapidio/switches/idt_gen3.c

## Purpose
RapidIO switch driver for IDT RXS Gen3 devices. It provides Gen3 route-table operations, hot-swap/error port-write setup, Gen3-specific error handling, and shutdown mitigation for repeated port-write generation.

## Important APIs, types, and functions
`idtg3_route_add_entry/get_entry/clr_table()` program broadcast or per-port L2 route table entries and translate invalid routes to `RIO_RT_ENTRY_DROP_PKT`. `idtg3_em_init()` disables interrupts, suppresses port writes during setup, enables OK-to-uninitialized and link-init notifications on usable ports, routes port writes to the ingress port, re-enables port writes, and sets TVAL. `idtg3_em_handler()` soft-resets a port to clear error-stopped bits on insertion. `idtg3_shutdown()` disables port-write transmission if this enumerator is the configured target. Probe attaches ops and disables hierarchical routing during enumeration.

## Control flow
The driver registers a `rio_driver` at device init. Route ops validate 8-bit destination IDs and table bounds. Global route writes use broadcast registers because the hardware lacks a dedicated global table; global reads use the ingress port table. Core port-write handling invokes `em_handle()` before generic error processing. Shutdown runs from the RapidIO driver shutdown callback and only affects enumerator-owned devices.

## State and persistence
Hardware state includes L2 route table entries, hierarchical routing control, EM port-write TX control, per-port event enables, port-write route, soft reset bits, and optional shutdown disabling of port-write TX. Kernel state is the switch ops pointer.

## Dependencies and integration
Depends on RapidIO core switch ops and error-management flow, IDT RXS device IDs, and Gen3 register layout. Selected by `CONFIG_RAPIDIO_RXS_GEN3`.

## Risks
Only route destIDs up to 0xff are supported despite wider RapidIO systems. The error handler intentionally treats link-up error-stopped as insertion and uses soft reset; comments note this is not sufficient for all cable-down/up cases requiring full ackID realignment. Shutdown parses 8-bit/16-bit destID target fields and must match hardware encoding.

## Test signals
Route add/get/clear for global and per-port tables, invalid destID/table rejection, probe disabling hierarchical routing, EM init on ports with and without `PORT_UA`, soft reset on error-stopped insertion, no-op on removal, and shutdown disabling port-write TX only when the host destID matches.
