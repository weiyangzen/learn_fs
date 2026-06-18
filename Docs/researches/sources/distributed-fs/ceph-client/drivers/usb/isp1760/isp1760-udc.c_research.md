# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-udc.c

## Purpose
`isp1760-udc.c` implements the USB gadget/device-controller role for ISP1761/ISP1763 hardware. It registers a `usb_gadget`, implements endpoint operations, handles EP0 control transfers, moves data through endpoint FIFOs, processes shared IRQ status, monitors VBUS, and exposes pullup/start/stop operations to gadget drivers.

## Important APIs, Types, And Functions
The request wrapper is `struct isp1760_request`. Conversion helpers map gadget/endpoint/request objects back to UDC structures. Public functions are `isp1760_udc_register()` and `isp1760_udc_unregister()`. Endpoint operations are `isp1760_ep_enable()`, `isp1760_ep_disable()`, `isp1760_ep_alloc_request()`, `isp1760_ep_free_request()`, `isp1760_ep_queue()`, `isp1760_ep_dequeue()`, `isp1760_ep_set_halt()`, `isp1760_ep_set_wedge()`, and `isp1760_ep_fifo_flush()`. Gadget ops are `get_frame`, `wakeup`, `set_selfpowered`, `pullup`, `udc_start`, and `udc_stop`.

Core data paths are `isp1760_udc_receive()`, `isp1760_udc_transmit()`, `isp1760_ep_rx_ready()`, `isp1760_ep_tx_complete()`, `isp1760_ep0_setup()`, `isp1760_ep0_setup_standard()`, `isp1760_udc_irq()`, and `isp1760_udc_vbus_poll()`.

## Control Flow
Registration initializes the UDC lock/timer, validates hardware through scratch/chip ID, resets DC mode, allocates an IRQ name, requests a shared IRQ, initializes gadget static fields and endpoints, and calls `usb_add_gadget_udc()`. Gadget start validates speed, records the driver, sets attached state, enables global device interrupts, initializes hardware interrupt modes/masks, sets pullup if connected, and enables the device. Stop deletes the VBUS timer, clears the mode register, and drops the gadget driver.

EP0 setup IRQ reads the 8-byte setup packet, advances the EP0 state to data-in, data-out, or status, then handles standard requests internally where possible. GET_STATUS writes a two-byte IN response directly. SET_ADDRESS writes address/dev-enable and sends status. SET/CLEAR_FEATURE endpoint halt manipulates endpoint stall state. Nonstandard or configuration requests are passed to the gadget driver's setup callback. Data endpoint queueing starts IN transmission immediately when idle or consumes pending OUT FIFO data if `rx_pending` was set.

## State And Persistence
`struct isp1760_udc` holds the gadget driver pointer, gadget object, spinlock, VBUS timer, endpoint array, EP0 state/direction/length, connected flag, variant flag, and device status bits. Each `struct isp1760_ep` tracks descriptor, request queue, maxpacket, address, halted/wedged/rx_pending flags. State is volatile and reset by disconnect, bus reset, endpoint disable, and gadget stop. Hardware endpoint registers are banked by `DC_EPINDEX`.

## Dependencies And Integration Points
The file depends on USB gadget core, IRQ APIs, timers, regmap/raw FIFO access, local core pullup helper, and register definitions. It integrates with the common ISP1760 device through embedded UDC state and shared regmaps. Gadget drivers interact through standard `usb_ep_ops` and `usb_gadget_ops`.

## Risks
The FIFO read/write loops use 32-bit and 16-bit raw accesses and comments note hardware quirks around extra bytes and CLBUF not fully flushing transmit FIFO. `short_not_ok` is not implemented for OUT requests. Endpoint disable has a TODO to synchronize with the IRQ handler. Clearing halt on an IN endpoint with queued data can restart transmission, so queue and stall ordering is delicate. VBUS interrupt only reports attach; detach is detected by polling. EP array indexing maps IRQ endpoint numbers to IN/OUT entries in a compact way, which is easy to break. Remote wakeup/test mode are not implemented.

## Test Signals
Use gadget functions such as loopback, mass storage, ECM/RNDIS, or configfs to test enumeration, SET_ADDRESS, SET_CONFIGURATION, GET_STATUS, endpoint halt/wedge clear, IN/OUT bulk and interrupt transfers, zero-length packets, disconnect/reconnect, suspend/resume, high-speed status, VBUS removal polling, and bus reset. Fault tests should cover IRQ sharing, request dequeue, endpoint disable with active queues, and gadget driver unbind during traffic.
