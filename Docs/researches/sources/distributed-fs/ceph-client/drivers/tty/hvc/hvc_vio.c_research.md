# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_vio.c

## Purpose
`hvc_vio.c` connects IBM pSeries VIO virtual terminal devices to the HVC core. It supports raw `hvterm1` consoles and packetized `hvterm-protocol` HVSI consoles, plus early boot and udbg paths.

## Important APIs, Types, and Functions
`struct hvterm_priv` stores the firmware term number, protocol, `hvsi_priv`, a raw-input bounce buffer, and offset/remaining counters. Raw operations are `hvterm_raw_get_chars()` and `hvterm_raw_put_chars()`. HVSI operations are `hvterm_hvsi_get_chars()`, `hvterm_hvsi_put_chars()`, `hvterm_hvsi_open()`, `hvterm_hvsi_close()`, `hvterm_hvsi_hangup()`, and modem-control callbacks. Runtime probing uses `hvc_vio_probe()` and driver registration uses `hvc_vio_init()`. Early setup is in `hvc_vio_init_early()`.

## Control Flow
Early init checks `/chosen/stdout` for a `vty` node, reads its unit address, selects raw or HVSI protocol, initializes HVSI if needed, installs udbg hooks, optionally adds preferred `hvc0`, and calls `hvc_instantiate(0, 0, ops)`. Runtime VIO probe matches compatible strings, reuses the boot private object when the device is the early console, otherwise finds a free HVC slot, allocates private state, initializes HVSI, then calls `hvc_alloc(termno, irq, ops, MAX_VIO_PUT_CHARS)`.

Raw reads call `hvc_get_chars()` into an internal buffer, remove a firmware bug pattern of NUL after CR, and serve callers from the buffered data. Raw writes call `hvc_put_chars()`. HVSI mode delegates packet handling and modem control to `hvsi_lib.c`.

## State and Persistence Behavior
`hvterm_privs[]` maps HVC virtual term numbers to protocol state, and `hvterm_priv0` preserves the boot console private object. State is in-memory and tied to VIO device lifetime.

## Dependencies and Integration Points
It integrates with the VIO bus, Open Firmware nodes, PowerPC hypervisor console calls, `hvsi_lib.c`, udbg, and the generic HVC core. IRQ-capable devices reuse the notifier callbacks from `hvc_irq.c`.

## Risks and Edge Cases
Raw `put_chars()` requires a buffer of at least 16 bytes; udbg output uses a bounce buffer for single-character writes. Array slots are limited by `MAX_NR_HVC_CONSOLES`. The raw input workaround modifies received data and should be tested on firmware that emits CR/NUL. `HVC_OLD_HVSI` can suppress HVC registration for HVSI boot consoles.

## Test Signals
Signals include OF discovery of `hvterm1` and `hvterm-protocol`, early console output, udbg fallback, VIO probe hotplug, IRQ-driven reads, HVSI handshake and DTR handling, and the CR/NUL raw input workaround.
