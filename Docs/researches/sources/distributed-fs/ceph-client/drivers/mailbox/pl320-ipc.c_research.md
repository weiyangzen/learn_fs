# sources/distributed-fs/ceph-client/drivers/mailbox/pl320-ipc.c

Purpose: implements legacy ARM PL320 IPC support for Calxeda-style A9/M3 communication. It is not a generic `mbox_controller`; it exports blocking transmit and atomic notifier APIs directly.

Important APIs/types/functions: exported functions are `pl320_ipc_transmit`, `pl320_ipc_register_notifier`, and `pl320_ipc_unregister_notifier`. Static globals hold `ipc_base`, IRQ number, transmit mutex, completion, and `ATOMIC_NOTIFIER_HEAD`. Helpers `__ipc_send` and `__ipc_rcv` move seven 32-bit data registers.

Control flow: AMBA probe maps the PL320 resource, clears TX send state, requests the IRQ, initializes TX mailbox source/destination/mask registers, and initializes RX mailbox routing. `pl320_ipc_transmit` serializes with a mutex, sends seven words through mailbox 1, waits up to 1 second for the IRQ completion, then reads the response and returns `data[1]` as status. The IRQ handler completes TX when mailbox 1 fires and handles RX mailbox 2 by reading data, calling the atomic notifier chain with `data[0]` as event and `data + 1` as payload, then acknowledging.

State and persistence: global singleton state reflects one PL320 block. Runtime state includes a single blocking TX transaction and notifier subscribers; nothing persists after reboot.

Dependencies and integration: depends on AMBA device id `0x00041320`, PL320 register layout, completion/mutex/notifier APIs, and platform code that calls the exported functions.

Risks: singleton globals prevent multiple instances. Blocking transmit is explicitly unusable in interrupt context. No remove path frees IRQ or mapping, matching old init-only usage.

Test signals: AMBA probe, TX timeout and response status, RX notifier ordering, and concurrent transmit serialization.
