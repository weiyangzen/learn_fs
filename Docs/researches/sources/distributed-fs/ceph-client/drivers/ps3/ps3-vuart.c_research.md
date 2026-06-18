# sources/distributed-fs/ceph-client/drivers/ps3/ps3-vuart.c

Purpose: PS3 virtual UART transport for inter-partition byte streams, primarily AV settings on port 0 and system manager on port 2. It provides exported read/write/async helpers and a wrapper driver registration model for VUART port clients.

Important APIs/types/functions: `struct ps3_vuart_port_priv`, `ps3_vuart_get_triggers()`, `ps3_vuart_set_triggers()`, interrupt enable/disable helpers, exported `ps3_vuart_write()`, `ps3_vuart_read()`, `ps3_vuart_read_async()`, `ps3_vuart_cancel_async()`, `ps3_vuart_clear_rx_bytes()`, `ps3_vuart_port_driver_register()`, and unregister. Internal `list_buffer` queues TX/RX data.

Control flow: bus init checks PS3 LV1 firmware and initializes probe mutex. A port driver registers through `ps3_vuart_port_driver_register()`, which substitutes common probe/remove/shutdown hooks. Probe obtains the shared bus interrupt, claims the port, allocates per-port state, initializes queues/work, clears stale RX, enables RX interrupts, sets triggers, then calls the client probe. Writes attempt immediate LV1 write when the TX queue is empty, queue remaining bytes, and enable TX interrupts. RX interrupts pull all waiting bytes into list buffers and schedule client work once the requested async threshold is met. Reads queue pending bytes if necessary and dequeue exactly the requested amount or return `-EAGAIN`. The shared IRQ scans a hypervisor-updated port bitmap and dispatches per-port interrupt handlers.

State/dependencies: global `vuart_bus_priv` holds the aligned port bitmap, virq, probe mutex, use count, and active port devices. Each port has interrupt mask, TX/RX list locks, async trigger, bytes-held count, and stats. Depends on PS3 LV1 VUART calls, PS3 system bus, workqueues, IRQs, and physical-to-LPAR address conversion.

Risks: several impossible states use `BUG_ON()`; disconnect handling is unimplemented and intentionally BUGs; IRQ bitmap scanning assumes nonzero status semantics; `use_count` assumes at most two users despite `PORT_COUNT` being three; queued buffer allocations in RX interrupt use `GFP_ATOMIC`; shutdown leaves polling usable for system-manager final power sequence.

Test signals: register AV/system-manager clients, shared IRQ setup/teardown across multiple ports, partial TX write queue draining, RX async threshold scheduling, polled reads returning `-EAGAIN`, stale RX clearing, shutdown polling behavior, and error paths for busy ports or unsupported firmware.
