# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/max3420_udc.c

## Purpose
Implements a USB gadget UDC driver for Maxim MAX3420/MAX3421 device-mode controllers accessed over SPI. The driver exposes a full-speed gadget with EP0, one bulk OUT endpoint, and two bulk IN endpoints, using a kernel thread to serialize SPI register/FIFO work that cannot be done directly in hard IRQ context.

## Important APIs, Types, And Functions
Core state is in `struct max3420_udc`, `struct max3420_ep`, and `struct max3420_req`. Register constants define MAX3420 SPI command encoding, endpoint FIFOs/count registers, EPIRQ/EPIEN, USBIRQ/USBIEN, USBCTL, CPUCTL, PINCTL, EPSTALLS, and CLRTOGS bits. Endpoint operations are `max3420_ep_enable()`, `max3420_ep_disable()`, `max3420_ep_queue()`, `max3420_ep_dequeue()`, `max3420_ep_set_halt()`, allocation/free, and `max3420_nuke()`. Gadget operations are `max3420_udc_start()`, `max3420_udc_stop()`, and `max3420_wakeup()`.

SPI helpers include byte and buffer accessors (`spi_rd8_ack()`, `spi_rd8()`, `spi_wr8_ack()`, `spi_wr8()`, `spi_rd_buf()`, `spi_wr_buf()`, `spi_ack_ctrl()`). Hardware action helpers include `spi_max3420_enable()`, `spi_max3420_stall()`, `spi_max3420_rwkup()`, `__max3420_start()`, `__max3420_stop()`, and `max3420_start()`. EP0 and IRQ handling run through `max3420_handle_setup()`, `max3420_getstatus()`, `max3420_set_clear_feature()`, `max3420_do_data()`, `max3420_handle_irqs()`, `max3420_thread()`, `max3420_irq_handler()`, and optional `max3420_vbus_handler()`.

## Control Flow
Probe requires a full-duplex SPI controller, configures SPI mode 3 and 8-bit words, allocates controller state, initializes the gadget and endpoints, does a small initial SPI read/configuration, registers the gadget UDC, requests the UDC IRQ, creates the SPI worker thread, and optionally requests a named VBUS IRQ. Without a VBUS IRQ the design is treated as self-powered and VBUS-active; with VBUS IRQ, the handler toggles `vbus_active`, updates gadget state, queues a start/stop action, and wakes the worker.

The hard IRQ handler disables the SPI IRQ and sets a `ENABLE_IRQ` todo bit before waking the thread. The thread periodically re-enables the IRQ when idle, takes `spi_bus_mutex`, skips most work if not VBUS-active or not soft-connected, and then drains pending start/stop, MAX3420 IRQ registers, remote wakeup, EP0 IN ZLP work, endpoint enable/disable todo bits, and endpoint stall/unstall todo bits. All SPI I/O is therefore serialized in process context.

Device start resets and configures the chip, waits for oscillator OK, enables VBUS-gated connect, sets USB reset and EP0 interrupts, and enables CPU IRQ output. Stop nukes non-EP0 queues, disables IRQ output, and powers down the chip with different oscillator handling for self-powered versus bus-powered designs. Endpoint enable/disable and halt only set per-endpoint todo bits under the endpoint lock; the thread performs the actual SPI register changes.

Setup handling reads SUDFIFO, locally answers standard GET_STATUS, SET_ADDRESS, and SET/CLEAR_FEATURE for remote wakeup or endpoint halt, and forwards all other setup packets to the gadget driver, stalling EP0 on negative return. Data movement is packet-sized: `max3420_do_data()` takes the first queued request, transfers at most maxpacket bytes to or from the endpoint FIFO/count register, updates `actual`, detects short or complete transfers, removes completed requests, acknowledges EP0 control status when needed, and calls completion.

## State And Persistence
State is volatile memory plus MAX3420 register state. Persistent runtime fields include `driver`, `thread_task`, `remote_wkp`, `is_selfpowered`, `vbus_active`, `softconnect`, cached setup packet, `suspended`, controller todo bits, endpoint todo bits, endpoint halt flags, endpoint queues, request status/actual counters, and an internal EP0 buffer/request. There is no durable storage and no custom sysfs/debugfs state.

## Dependencies And Integration Points
The driver depends on the SPI core, OF IRQ lookup for `"udc"` and optional `"vbus"` IRQs, GPIO/OF-capable platform descriptions, kthreads, mutex/spinlock synchronization, USB gadget core registration and callbacks, and standard USB Chapter 9 definitions. It integrates with gadget function drivers through the usual UDC callbacks and with board wiring through VBUS IRQ presence or absence.

## Risks And Test Signals
Risk areas include hard IRQ masking/re-enable coordination with the worker loop, toggling `vbus_active` instead of reading an explicit VBUS level in the VBUS handler, SPI transfer errors being ignored by helper routines, EP0 setup endianness conversion using CPU conversion helpers on already-read raw data, completion callbacks called without the broader UDC lock but after queue removal, endpoint todo bits racing with remove/thread stop, and fixed endpoint direction/type capabilities that may surprise composite functions expecting more endpoints.

Useful test signals include full-speed enumeration over SPI, absence and presence of VBUS IRQ, cable bounce behavior, reset/suspend/resume and remote wakeup, EP0 standard and delegated setup requests, SET/CLEAR_FEATURE endpoint halt on each endpoint, bulk OUT on EP1 and bulk IN on EP2/EP3 with short packets and zero-length completions, disconnect while requests are queued, SPI fault injection or controller removal during worker activity, and lockdep/KCSAN checks around IRQ disable and thread wakeups.
