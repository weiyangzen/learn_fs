<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ioc3kbd.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/ioc3kbd.c

## Purpose
`ioc3kbd.c` is the SGI IOC3 PS/2 serio driver. It exposes separate keyboard and auxiliary serio ports backed by IOC3 keyboard/mouse registers and dispatches packed receive data from a shared interrupt.

## Important APIs, types, and functions
- `struct ioc3kbd_data` stores the mapped IOC3 serio registers, keyboard/AUX serio objects, active flags, and IRQ.
- `ioc3kbd_wait()` polls IOC3 CSR write-pending bits with a bounded 50 us delay loop.
- `ioc3kbd_write()` and `ioc3aux_write()` wait for keyboard or mouse write-pending bits to clear before writing `k_wd` or `m_wd`.
- `ioc3kbd_start()`/`ioc3kbd_stop()` and AUX equivalents toggle whether IRQ data is delivered.
- `ioc3kbd_process_data()` extracts up to three valid bytes from an IOC3 receive word and calls `serio_interrupt()`.
- `ioc3kbd_intr()` reads keyboard and mouse receive registers and dispatches data to active ports.
- `ioc3kbd_probe()` maps resources, allocates two serio ports, registers them, requests the shared IRQ, and enables the ports by writing `km_csr`.

## Control flow
The platform driver matches `"ioc3-kbd"`. Probe maps register resource 0, gets IRQ 0, allocates driver data and two serio objects, fills type/write/start/stop/name/phys fields, stores driver data, registers both serio ports, requests the shared IRQ, and enables keyboard/mouse clamps. Remove frees the IRQ and unregisters both ports.

## State and persistence
The driver tracks only runtime port-active booleans and the mapped register pointer. It does not persist configuration. The hardware CSR is changed on probe to enable ports.

## Dependencies and integration points
It depends on platform device resources, SGI IOC3 register definitions from `<asm/sn/ioc3.h>`, MMIO accessors, IRQs, and the serio core.

## Risks
- Serio ports are registered before IRQ request; IRQ request failure unregisters both, but transient users may have seen the ports.
- The interrupt handler always returns handled after reading registers, relying on shared IRQ tolerance.
- `ioc3kbd_process_data()` does not attach parity/frame flags; hardware error details are not surfaced.
- Active booleans are not explicitly locked; they rely on serio start/stop and IRQ ordering.

## Test signals
- Build with SGI IOC3 platform support.
- Hardware tests should verify keyboard and mouse writes, three-byte receive packing, shared IRQ behavior, IRQ request failure cleanup, and removal while ports are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ioc3kbd.c -->
