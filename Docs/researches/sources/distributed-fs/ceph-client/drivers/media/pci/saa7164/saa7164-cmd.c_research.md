# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-cmd.c

Purpose: command/response orchestration layer for SAA7164 firmware messages. It allocates command sequence slots, splits large requests, waits for firmware responses, handles IRQ/deferred dequeue, validates responses, maps firmware error codes, and releases sequence state.

Important APIs, types, and functions: internal helpers include `saa7164_cmd_alloc_seqno()`, `saa7164_cmd_free_seqno()`, `saa7164_cmd_timeout_seqno()`, `saa7164_cmd_timeout_get()`, `saa7164_cmd_dequeue()`, `saa7164_cmd_set()`, and `saa7164_cmd_wait()`. Public functions are `saa7164_irq_dequeue()` for interrupt-side response signaling and `saa7164_cmd_send()` for synchronous firmware commands. It uses `dev->cmds[]` entries containing sequence number, lock, waitqueue, in-use, signalled, and timeout state.

Control flow: `saa7164_cmd_send()` validates parameters, allocates a sequence, fills a command header, sends it through `saa7164_cmd_set()` which chunks payloads by bus max request size, then loops waiting for responses. Wait uses `wait_event_timeout()` on the sequence waitqueue; IRQ/dequeue paths peek bus responses, mark `signalled`, and wake the waiter. The sender peeks the response, dequeues unrelated responses if necessary, handles firmware error flags by reading error data and mapping PVC error codes, validates id/command/control/size, consumes response payload into the caller buffer, and repeats until all split response bytes are received.

State and persistence: command slots in `dev->cmds[]` are transient synchronization state. Timeout flags persist until a slot is freed. Firmware responses are consumed from the bus ring. No persistent storage.

Dependencies and integration points: sits between all high-level API calls and `saa7164_bus_set/get()`. Depends on device locks, per-command locks, waitqueues, `waitsecs`, IRQ/work handling, PVC/SAA error code definitions, and bus ring semantics.

Risks: timeout paths can return without freeing sequence numbers in some branches, relying on timeout cleanup/dequeue behavior. Concurrent responses require careful dequeue; safety loop protects against endless wrong-event handling but can return busy. `buf + offset` arithmetic on `void *` relies on GNU C extension. Split command/response size validation must match firmware exactly. If IRQ dequeue misses a response, synchronous wait can time out even when data is on the bus.

Test signals: normal firmware commands during initialization; debug with concurrent API calls; large descriptor/I2C transfers that split across request sizes; injected wrong-sequence responses; firmware error responses mapped to expected SAA errors; command timeout recovery followed by successful later commands; no leaked in-use command slots after repeated failures.
