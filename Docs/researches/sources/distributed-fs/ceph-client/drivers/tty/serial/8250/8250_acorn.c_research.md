# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_acorn.c

## Purpose
Supports Acorn expansion-card 8250-compatible serial boards, mapping ecard resources and registering each UART with the 8250 core.

## Important APIs, types, and functions
- `struct serial_card_type` describes port count, UART clock, resource type, and per-port offsets.
- `struct serial_card_info` stores port line numbers and mapped virtual address.
- `serial_card_probe()` maps the ecard resource and calls `serial8250_register_8250_port()` for each port.
- `serial_card_remove()` unregisters registered ports.
- `serial_cids[]` matches Atomwide and Serport products; `serial_card_driver` registers with the ecard bus.

## Control flow
On ecard probe, the driver allocates info, maps the card resource, builds a reusable `uart_8250_port` template with shared IRQ, memory I/O, regshift 2, and card-specific clock, then iterates over offsets to register each UART. Removal unregisters positive line numbers and frees the info structure.

## State and persistence behavior
Per-card state stores mapped resource and registered 8250 line numbers. Hardware mapping persists for card lifetime. No persistent storage.

## Dependencies and integration points
Depends on ARM ecard infrastructure, 8250 registration APIs, memory-mapped UART access, and shared IRQ handling through generic 8250.

## Risks and edge cases
- Probe does not unwind ports if a later `serial8250_register_8250_port()` fails; stored negative line numbers are skipped on removal.
- `ecardm_iomap()` mapping lifetime is tied to ecard APIs, while only `info` is freed explicitly.
- Fixed offsets/clocks must match the specific expansion-card type.

## Test signals
Probe/remove on Atomwide and Serport cards, all expected port offsets registered, shared IRQ operation, failure injection for mapping/allocation/partial port registration, and tty data transfer on each port.
