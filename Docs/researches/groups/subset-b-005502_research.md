# subset-b-005502 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/lpc32xx_udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/lpc32xx_udc.c

## Purpose
Implements the Linux USB gadget UDC driver for the NXP/Philips LPC32xx USB device controller. It binds the platform device, configures the ISP1301/STOTG04 I2C transceiver, exposes a `usb_gadget` with 16 logical endpoints, drives the LPC32xx protocol engine and DMA descriptor table, and handles EP0 control requests plus non-control endpoint request queues.

## Important APIs, Types, And Functions
Core state lives in `struct lpc32xx_udc`, `struct lpc32xx_ep`, `struct lpc32xx_request`, `struct lpc32xx_usbd_cfg`, and the gadget-side DMA descriptor `struct lpc32xx_usbd_dd_gad`. The driver exports endpoint operations through `lpc32xx_ep_ops` (`lpc32xx_ep_enable()`, `lpc32xx_ep_disable()`, `lpc32xx_ep_queue()`, `lpc32xx_ep_dequeue()`, halt and wedge handling) and gadget operations through `lpc32xx_udc_ops` (`lpc32xx_get_frame()`, `lpc32xx_vbus_session()`, `lpc32xx_pullup()`, `lpc32xx_start()`, `lpc32xx_stop()`, self-powered state).

Important low-level helpers are the protocol-engine command wrappers `udc_protocol_cmd_w()`, `udc_protocol_cmd_data_w()`, and `udc_protocol_cmd_r()`, endpoint realization and state helpers such as `udc_realize_hwep()`, `udc_unrealize_hwep()`, `udc_stall_hwep()`, `udc_clrstall_hwep()`, `udc_clr_buffer_hwep()`, and DMA setup/completion helpers `udc_dd_alloc()`, `udc_ep_in_req_dma()`, `udc_ep_out_req_dma()`, and `udc_handle_dma_ep()`. EP0 is handled by `udc_handle_ep0_setup()`, `udc_handle_ep0_in()`, `udc_handle_ep0_out()`, `udc_ep0_in_req()`, and `udc_ep0_out_req()`. Platform lifecycle runs through `lpc32xx_udc_probe()`, `lpc32xx_udc_remove()`, shutdown, suspend, resume, and the four IRQ handlers for low-priority USB, high-priority USB, device DMA, and VBUS/ATX.

## Control Flow
Probe allocates and initializes a controller instance from a template, maps MMIO, obtains the slave clock and IRQs, allocates the UDCA DMA array and descriptor pool, sets endpoint capabilities, configures the ISP1301/STOTG04 transceiver over I2C, registers the gadget UDC, and creates optional debugfs state. `lpc32xx_start()` installs the gadget driver, powers/clocks the controller as appropriate, and enables pullup only when VBUS/session policy permits. `lpc32xx_stop()` and removal tear down pullup, stop activity, remove the UDC, free DMA resources, and disable clocks/IRQs.

On reset or enable, `udc_enable()` first calls `udc_disable()` for a known baseline, realizes EP0 OUT/IN hardware endpoints, clears stalls and buffers, installs the UDCA base, enables endpoint/device/DMA interrupts, sets address zero twice to force a protocol-engine latch, and records an unconfigured status. EP0 OUT interrupts detect setup packets, read the 8-byte control request from FIFO, update the local EP0 direction/state, handle standard GET_STATUS, SET_ADDRESS, SET/CLEAR_FEATURE locally, pass descriptors and function-specific requests to the gadget driver, and then send ZLP or STALL as needed. SET_CONFIGURATION additionally issues protocol-engine configure and mode commands after the function driver has enabled endpoints.

Non-control endpoint enable validates descriptors, maps logical endpoint number plus direction to a physical hardware endpoint, realizes the endpoint, clears DMA status, and leaves interrupts disabled until a request is queued. Queueing a non-EP0 request maps the buffer for DMA, allocates and fills one DMA descriptor, stores it in the UDCA slot, enables DMA, and marks `req_pending`. DMA EOT interrupts inspect descriptor status, handle system errors and short packets, update `req.actual`, send or defer a zero-length packet when `req.zero` requires it, complete the request outside the controller lock, and immediately starts the next queued request if present. EP0 uses FIFO read/write helpers instead of DMA.

VBUS and suspend paths coordinate external transceiver state and gadget state. VBUS/session changes update `vbus`, call `usb_udc_vbus_handler()`-style gadget state changes indirectly through local callbacks, enable clocks/pullup only when requested, and call `stop_activity()` on disconnect. Slow I2C work is deferred through `pullup_job` and `power_job`, while fast hardware state changes happen under `udc->lock`.

## State And Persistence
All state is volatile kernel memory and hardware register state. Persistent-like runtime state includes endpoint request queues, `ep0state`, `enabled_devints`, `enabled_hwepints`, `realized_eps`, `dev_status` remote-wakeup/self-powered bits, `vbus`/`last_vbus`, `pullup`, `poweron`, `enabled`, `clocked`, `suspended`, `enabled_ep_cnt`, UDCA descriptor pointers, and per-request DMA descriptor/mapping state. The only filesystem-facing state is optional debugfs output under `driver/udc`; no durable data is stored.

## Dependencies And Integration Points
The file integrates with the USB gadget core via `usb_add_gadget_udc()`, `usb_del_gadget_udc()`, `usb_gadget_giveback_request()`, `usb_gadget_map_request()`, and endpoint/gadget ops. It depends on platform-device resources, MMIO register access, Linux DMA pools and coherent memory, clocks, I2C SMBus access to ISP1301/STOTG04 registers, interrupt handling, workqueues, wait queues, optional debugfs, OF matching for `nxp,lpc3220-udc`, and standard USB Chapter 9 definitions. Board callbacks in `struct lpc32xx_usbd_cfg` receive connection, suspend, and remote-wakeup state changes.

## Risks And Test Signals
High-risk areas are protocol-engine polling loops with no explicit timeout failure propagation, races between deferred I2C pullup/power work and disconnect/remove, DMA descriptor lifetime on allocation or mapping failures, ZLP deferral when endpoint buffers are full, EP0 state transitions after failed setup handling, endpoint disable waiting while queues are being completed, and lock release around gadget callbacks. One visible bug risk is the request queue path: if DMA descriptor allocation fails after `usb_gadget_map_request()`, the mapped request is not unmapped before returning. Suspend/resume also schedules `pullup_job` while changing `poweron`, which is easy to misread against the separate `power_job`.

Useful test signals include enumeration and control transfers with SET_ADDRESS, SET_CONFIGURATION, GET_STATUS, remote-wakeup feature toggles, endpoint halt/wedge behavior, VBUS attach/detach with transceiver I2C present, suspend/resume with self-powered and bus-powered configurations, bulk/interrupt/iso DMA transfers including short packets and `req.zero` ZLP cases, DMA system-error injection, disconnect during active transfers, repeated endpoint enable/disable cycles, debugfs queue visibility, and lockdep/KASAN/KCSAN coverage around callbacks and workqueue teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/lpc32xx_udc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/m66592-udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/m66592-udc.c

## Purpose
Implements the Renesas M66592 USB gadget controller driver. It programs the controller clocks, FIFO/pipe allocation, endpoint operations, control-transfer handling, VBUS debounce, and interrupt-driven data movement for a high-speed capable platform UDC described by `m66592-udc.h`.

## Important APIs, Types, And Functions
The implementation centers on `struct m66592`, `struct m66592_ep`, `struct m66592_request`, and `struct m66592_pipe_info` from the companion header. Gadget-facing operations are `m66592_ep_ops` (`m66592_enable()`, `m66592_disable()`, `m66592_queue()`, `m66592_dequeue()`, `m66592_set_halt()`, `m66592_fifo_flush()`) and `m66592_gadget_ops` (`m66592_udc_start()`, `m66592_udc_stop()`, `m66592_get_frame()`, `m66592_pullup()`).

Key hardware helpers include `enable_pipe_irq()`, `disable_pipe_irq()`, PID/control helpers (`control_reg_get_pid()`, `control_reg_set_pid()`, `pipe_start()`, `pipe_stop()`, `pipe_stall()`, `control_reg_sqclr()`), FIFO/pipe configuration (`pipe_buffer_setting()`, `pipe_buffer_release()`, `pipe_initialize()`, `m66592_ep_setting()`, `alloc_pipe_config()`, `free_pipe_config()`), controller setup (`init_controller()`, `disable_controller()`, `m66592_start_xclock()`), transfer helpers (`start_ep0_write()`, `start_packet_write()`, `start_packet_read()`, `irq_ep0_write()`, `irq_packet_write()`, `irq_packet_read()`), and interrupt handlers (`irq_pipe_ready()`, `irq_pipe_empty()`, `irq_device_state()`, `irq_control_stage()`, `m66592_irq()`).

## Control Flow
Probe maps the register resource, validates platform data, allocates the controller, requests the IRQ, optionally enables an on-chip clock, initializes all endpoint objects and their USB capabilities, allocates an internal EP0 request for driver-generated GET_STATUS responses, calls `init_controller()`, and registers the gadget UDC. Removal unregisters the gadget, stops the VBUS timer, unmaps registers, frees IRQs and EP0 request storage, disables the optional clock, and frees the controller.

Endpoint enable selects a free hardware pipe based on USB transfer type. Bulk endpoints first consume the dedicated bulk pipes and may fall back to isochronous pipes configured as bulk; interrupt and isochronous endpoints have separate counters. `pipe_buffer_setting()` writes PIPECFG/PIPEBUF/PIPEMAXP/PIPEPERI, assigns double buffering and short-packet NAK policy for bulk OUT, and records endpoint-to-pipe maps. Queueing adds a request to the endpoint list, initializes status/actual, and if the endpoint is idle starts EP0 handling or calls `start_packet()` for the selected direction.

Data transfer is interrupt driven. BRDY interrupts indicate data can be read or written; BEMP interrupts indicate an IN buffer emptied and may complete a write. FIFO routines choose CFIFO or DMA FIFOs D0/D1 depending on pipe assignment and platform capabilities, use configured bus width and endian rules from the header, track `req.actual`, and stop or continue interrupts based on packet size, request length, and `req.zero`. `transfer_complete()` removes the request, converts disconnect to `-ESHUTDOWN`, drops the spinlock around `usb_gadget_giveback_request()`, then restarts the next queued request.

Control transfers are decoded from controller setup registers in `setup_packet()`. Standard GET_STATUS, CLEAR_FEATURE, and SET_FEATURE are handled locally, including endpoint halt state and test mode; other requests are passed to the gadget driver from `irq_control_stage()`. Device-state interrupts update speed after bus reset/default/configured transitions and call `usb_gadget_udc_reset()`. VBUS interrupts start a timer-based debounce loop; after stable samples, the driver connects by enabling interrupts and D+ pullup or disconnects by clearing pullup, calling the function driver's disconnect callback outside the lock, disabling the controller, and resetting EP0 queue state.

## State And Persistence
State is held in memory and controller registers only. The driver mutates endpoint queues, pipe-to-endpoint and endpoint-address maps, `gadget.speed`, `driver`, `old_vbus`, VBUS sample count, `old_dvsq`, pipe allocation counters (`bulk`, `interrupt`, `isochronous`, `num_dma`), per-endpoint `busy`, `internal_ccpl`, `use_dma`, `pipenum`, FIFO register selectors, and an internal EP0 data/request pair. No persistent storage or sysfs files are created by this file beyond normal gadget device registration.

## Dependencies And Integration Points
The driver depends on the USB gadget framework, Linux platform resources, IRQs, timers, optional clocks, MMIO accessors, M66592 platform data from `<linux/usb/m66592.h>`, and all register/bit definitions in `m66592-udc.h`. It supports on-chip and external-chip modes with different endian, clock, interrupt-sense, DMA, and FIFO width programming. It integrates with gadget function drivers through setup, disconnect, reset, endpoint queueing, and request completion callbacks.

## Risks And Test Signals
Risk areas include fixed pipe allocation limits and fallback from bulk to isochronous pipes, VBUS debounce timing, lock release around gadget callbacks, assumptions that queue entries exist in BRDY/BEMP/CTR handlers, endpoint address mapping that does not include direction in `epaddr2ep`, and controller-specific clock restart when on-chip register reads return zero. The local GET_STATUS path includes an in-code question about reusing the internal EP0 request if another request arrives before completion, making EP0 reentrancy worth testing.

Useful test signals include high-speed and full-speed enumeration, stable and bouncing VBUS attach/detach, every standard EP0 request handled locally, class/vendor setup forwarding, endpoint halt/clear-halt while traffic is queued, bulk pipe exhaustion and bulk-on-isoc fallback, interrupt and isochronous endpoint enablement, short packet and zero-length IN/OUT transfers, disconnect during request completion, clock-stop wake interrupt behavior on on-chip systems, and lockdep/KASAN fault injection around queue and timer paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/m66592-udc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/m66592-udc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/m66592-udc.h

## Purpose
Defines the register map, bit masks, pipe/FIFO constants, controller-private data structures, conversion macros, and inline MMIO/FIFO helpers used by the Renesas M66592 USB gadget driver. It is the hardware contract for `m66592-udc.c`.

## Important APIs, Types, And Functions
The header enumerates controller registers from `M66592_SYSCFG`, `M66592_DVSTCTR`, FIFO selectors/counters, interrupt enable/status registers, setup packet registers, DCP registers, pipe configuration registers, and pipe control registers. It defines bit fields for clocking, USB state, interrupt causes, setup/control stages, FIFO readiness, endpoint stall/PID state, transfer types, direction, buffer sizing, DMA configuration, and USB standard request values.

Important structures are `struct m66592_pipe_info`, `struct m66592_request`, `struct m66592_ep`, and `struct m66592`. Helper macros include object conversions (`to_m66592()`, `gadget_to_m66592()`, `m66592_to_gadget()`), pipe-class checks (`is_bulk_pipe()`, `is_interrupt_pipe()`, `is_isoc_pipe()`), pipe IRQ wrappers (`enable_irq_ready()`, `disable_irq_ready()`, `enable_irq_empty()`, `disable_irq_empty()`, `enable_irq_nrdy()`, `disable_irq_nrdy()`), and `get_pipectr_addr()`. Inline accessors are `m66592_read()`, `m66592_write()`, `m66592_mdfy()`, `m66592_read_fifo()`, and `m66592_write_fifo()`.

## Control Flow
The header has no independent runtime entry point, but it shapes the implementation control flow. `m66592-udc.c` uses register offsets and masks to initialize clocks, detect VBUS and bus reset, program pipe allocation, move FIFO data, and dispatch BRDY/BEMP/control-stage interrupts. The inline FIFO helpers branch on `pdata->on_chip`: on-chip controllers use 32-bit repeated I/O and external chips use 16-bit repeated I/O, with special odd-byte handling for boards where WR0 is shorted to WR1. The endian bits in platform data determine byte placement for partial on-chip writes.

## State And Persistence
The defined state is volatile and driver-private. `struct m66592` stores the spinlock, MMIO base, optional clock, platform data, IRQ trigger, `usb_gadget`, gadget driver pointer, endpoint array, pipe and address lookup tables, internal EP0 request/data, VBUS debounce state, timer, previous device state, pipe allocation counters, and DMA FIFO allocation count. `struct m66592_ep` stores its request queue, busy/control-completion flags, DMA/FIFO usage, pipe number, type, and register selectors. No persistent storage is described.

## Dependencies And Integration Points
The header depends on Linux clock declarations and `<linux/usb/m66592.h>` for platform data. It is included by the M66592 UDC implementation and binds that implementation to USB gadget core types (`struct usb_gadget`, `struct usb_ep`, `struct usb_request`) plus Linux MMIO helpers. The constants encode the M66592 hardware interface, including on-chip/external variations, so platform data correctness is a major integration requirement.

## Risks And Test Signals
Risks include macro drift from hardware documentation, duplicated macro names such as `M66592_CNTMD`, `M66592_DIR`, `M66592_BSTS`, `M66592_SQCLR`, and `M66592_PID` for different register contexts, a suspicious `M66592_GET_DT_TYPE(v)` macro that references `DT_TYPE` rather than `M66592_DT_TYPE`, FIFO odd-byte/endian handling errors, and bounds assumptions around `epaddr2ep[16]` and `pipenum2ep[M66592_MAX_NUM_PIPE]`.

Useful test signals are compile coverage for on-chip and external configurations, big- and little-endian platform settings, 16-bit and 32-bit FIFO access paths, odd-length writes with `wr0_shorted_to_wr1`, all pipe classes and pipe index boundaries, clock and interrupt sense programming from platform data, and static analysis for macro misuse or array-index assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/m66592-udc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/max3420_udc.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/max3420_udc.c -->
