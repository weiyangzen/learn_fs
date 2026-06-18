# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mpsse.c

Purpose: exposes FTDI MPSSE-capable USB interfaces as 16-line GPIO chips and synthesizes edge IRQs by polling input pins. It includes a quirk for a Bryx device with named, direction-limited pins.

Important APIs/types/functions: `struct mpsse_priv` stores the gpiochip, USB device/interface, endpoint descriptors, output/direction bytes for low/high banks, direction masks, IRQ worker list, atomics for IRQ type/enabled masks, and I/O/IRQ locks. `mpsse_bulk_xfer()`, `mpsse_write()`, and `mpsse_read()` wrap USB bulk transfers. GPIO bank helpers use FTDI `SET_BITS` and `GET_BITS` commands. IRQ polling is implemented by `struct mpsse_worker`, `gpio_mpsse_poll()`, and irqchip enable/disable/type callbacks.

Control flow: USB probe allocates state and an IDA id, initializes locks, builds a unique label from VID/PID/interface/id/serial, applies optional direction/name quirk, finds bulk endpoints, allocates a receive buffer, resets the FTDI bitmode, enters MPSSE mode, configures an internal IRQ chip with valid IRQ mask restricted to input-capable pins, and registers the gpiochip. Set/get_multiple operate per 8-bit bank under `io_mutex`. Direction output sets the MPSSE direction bit then writes value; direction input clears the direction bit and writes the bank. IRQ enable starts a polling work item when transitioning from no enabled IRQs to some enabled IRQs; the worker polls selected input pins, compares against old values, and calls `generic_handle_irq()` on matching edges.

State and persistence behavior: `gpio_outputs[2]` and `gpio_dir[2]` are software shadows mirrored to MPSSE bank state. IRQ type and enabled state are atomics; worker lifetime is tracked in a raw-spinlock-protected list and coordinated with `irq_race` to avoid double-free between self-teardown and disconnect. No hardware state persists after USB disconnect or reset.

Dependencies and integration points: depends on USB core, FTDI vendor bitmode requests, gpiolib, IRQ domains, workqueues, IDA allocation, and optional product quirks. GPIO operations can sleep because they perform USB control/bulk transfers.

Risks: IRQs are polling based with a 1 ms interval, so fast pulses can be missed and latency is not deterministic. `gpio_mpsse_disconnect()` sets `priv->intf = NULL` after stopping workers, but ordinary GPIO I/O paths rely on the interface while the gpiochip is devm-managed, so disconnect ordering is important. Worker allocation happens in irqchip enable with `GFP_NOWAIT` and silently gives no polling worker on allocation failure. Quirk direction masks must be correct or valid pins become inaccessible.

Test signals: USB probe/reset/MPSSE mode commands, bulk status-byte stripping, banked get/set and direction bytes, quirk valid-mask enforcement and line names, polling IRQ delivery for rising/falling/both edges, worker teardown on IRQ disable and disconnect, and behavior under USB transfer failures.
