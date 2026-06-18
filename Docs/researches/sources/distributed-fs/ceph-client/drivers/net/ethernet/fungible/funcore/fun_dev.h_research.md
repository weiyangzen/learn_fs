# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_dev.h

## Purpose
Declares the Fungible core device abstraction used by PCI function drivers. It exposes admin command callbacks, service callbacks, doorbell helpers, device state, initialization parameters, and exported core APIs.

## Important APIs, Types, And Functions
Important types are `struct fun_dev`, `struct fun_dev_params`, `fun_admin_callback_t`, `fun_admin_event_cb`, and `fun_serv_cb`. Doorbell helpers are `fun_db_addr()`, `fun_sq_db_addr()`, and `fun_cq_db_addr()`. Declared APIs cover admin commands, resource count/destroy/bind, device enable/disable, IRQ reserve/release, and service scheduling.

## Control Flow
Consumers fill `struct fun_dev_params` with admin queue sizes, minimum MSI-X needs, event callback, and service callback before calling `fun_dev_enable()`. After enable, drivers submit HCI admin requests, allocate queues/IRQs, and use service callbacks for process-context work. Disable reverses state through `fun_dev_disable()`.

## State And Persistence
`struct fun_dev` stores all live function state: device pointer, BAR and doorbell addresses, admin queue and tag allocator, command contexts, suppress flag, CAP/CC shadows, queue limits, firmware handle, IRQ bitmap/lock, and work item. This state is process-kernel memory only.

## Dependencies And Integration Points
Includes `fun_hci.h` for command structures and Linux sbitmap/spinlock/workqueue types. It is included by funcore queue code and the Ethernet driver.

## Risks
The header exposes mutable internals rather than opaque accessors, so consumers can accidentally corrupt queue limits, IRQ maps, or command suppression state. Doorbell helpers assume valid BAR mapping and NVMe-style alternating SQ/CQ doorbells.

## Test Signals
Compile consumers against the header, verify doorbell address calculations for a known stride, and exercise the full `fun_dev_enable()`/admin-command/IRQ-reservation/`fun_dev_disable()` lifecycle through `funeth`.
