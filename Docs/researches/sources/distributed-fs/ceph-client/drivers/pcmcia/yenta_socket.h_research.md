# sources/distributed-fs/ceph-client/drivers/pcmcia/yenta_socket.h

Purpose: Defines CardBus/Yenta register offsets, bit masks, vendor override contracts, and the `struct yenta_socket` state container.

Important APIs and types: Defines CardBus socket event/mask/state/force/control/power registers, bridge base/limit/control fields, ExCA page register, Yenta 16-bit power flags, `struct cardbus_type`, and `struct yenta_socket`.

Control flow: No executable logic. `cardbus_type` function pointers let vendor headers provide override, save/restore, and socket-init hooks used by `yenta_socket.c`.

State and persistence: `struct yenta_socket` is the runtime state for one PCI CardBus bridge function, including mapped registers, timer, embedded PCMCIA socket, vendor-private words, and saved PCI state.

Dependencies and integration points: Includes `asm/io.h` and is included before vendor headers so they can access Yenta types and helper functions from `yenta_socket.c`.

Risks: Bit definitions directly control socket power, event masks, and bridge windows; mistakes can mispower cards or hide events. The private array is shared by vendor hooks and requires disciplined indexing. `cb_irq` uses zero as "no IRQ" even though zero can be a valid IRQ on some systems, matching legacy assumptions in the driver.

Test signals: Compile coverage, correct status decoding from `CB_SOCKET_STATE`, vendor override callbacks receiving valid `struct yenta_socket`, and suspend/resume preserving `saved_state`.
