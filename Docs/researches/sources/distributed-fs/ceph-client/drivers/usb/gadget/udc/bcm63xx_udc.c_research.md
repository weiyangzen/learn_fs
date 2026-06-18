<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bcm63xx_udc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bcm63xx_udc.c

## Purpose
This file implements the Broadcom BCM63xx high/full-speed USB device controller driver. It registers a `usb_gadget` backed by the BCM63xx USBD block plus an internal IUDMA engine, exposes one control endpoint and fixed bulk/interrupt endpoints, and bridges gadget driver requests to hardware descriptor rings. It is platform-data driven and depends on BCM63xx SoC register helpers, clocks, IRQ resources, and USB USBD/IUDMA register definitions.

## Important APIs, Types, And Functions
The main state containers are `struct bcm63xx_udc`, `struct bcm63xx_ep`, `struct bcm63xx_req`, and `struct iudma_ch`. Static `iudma_defaults[]` defines the hardware endpoint/channel mapping, FIFO sizing, packet sizes, and descriptor ring depths. Gadget endpoint operations are implemented by `bcm63xx_ep_enable()`, `bcm63xx_ep_disable()`, `bcm63xx_udc_queue()`, `bcm63xx_udc_dequeue()`, `bcm63xx_udc_set_halt()`, and `bcm63xx_udc_set_wedge()`. Gadget controller operations are `bcm63xx_udc_get_frame()`, `bcm63xx_udc_pullup()`, `bcm63xx_udc_start()`, and `bcm63xx_udc_stop()`. Hardware setup is split across `bcm63xx_init_udc_hw()`, `iudma_init()`, `bcm63xx_fifo_setup()`, `bcm63xx_ep_setup()`, and PHY/pullup helpers. Interrupt entry points are `bcm63xx_udc_ctrl_isr()` for USBD events and `bcm63xx_udc_data_isr()` for per-channel IUDMA completion. Debugfs views are provided through `bcm63xx_usbd_dbg_show()` and `bcm63xx_iudma_dbg_show()`.

## Control Flow
Probe allocates the UDC, maps USBD and IUDMA resources, initializes endpoint objects, clocks, DMA rings, IRQs, debugfs, and registers the gadget. `udc_start` switches the shared USB PHY to device mode, configures FIFOs/endpoints, and records the gadget driver. Pullup transitions EP0 from shutdown to a requeue state, enables control IRQs, and asserts D+. Non-EP0 requests are DMA-mapped, appended to an endpoint queue, and the head request is submitted to `iudma_write()`. IUDMA completion interrupts call `iudma_read()`, update `actual`, either queue the next fragment/request or complete the request outside the spinlock.

EP0 is workqueue-driven. Hardware delivers ordinary setup packets through EP0 RX IUDMA, but it auto-acks SET_CONFIGURATION and SET_INTERFACE. The control ISR therefore records pending synthetic events, and `bcm63xx_ep0_process()` runs a state machine covering setup receive, IN data, OUT data, OUT status, fake IN status, reset, and shutdown. Standard requests consumed by hardware are replayed to the gadget driver using synthesized `usb_ctrlrequest` objects.

## State And Persistence
State is in RAM and hardware registers only. Persistent driver state includes gadget speed, current config/interface/alternate interface, endpoint queues, IUDMA ring pointers, EP0 pending flags, EP0 reply/request pointers, and the wedged endpoint bitmap. DMA descriptors are coherent allocations owned by the device while the owner bit is set. Debugfs is observational and does not persist configuration. Module parameters `use_fullspeed` and `irq_coalesce` affect runtime mode and transfer interrupt behavior.

## Dependencies And Integration Points
The driver integrates with the Linux USB gadget core via `usb_add_gadget_udc()`, endpoint ops, and gadget ops; with platform device resources for two MMIO regions and seven IRQs; with BCM63xx board platform data for `port_no`; with BCM63xx clock and PHY/USBH private register helpers; with DMA mapping APIs; and with debugfs under `usb_debug_root`.

## Risks
The file explicitly documents that RX IRQ coalescing is less robust and does not reliably pass `testusb`; cancellation of partially complete RX transfers is a hardware limitation. EP0 is complex because hardware auto-acks some requests, so bad SET_CONFIGURATION/SET_INTERFACE cannot be stalled after the fact. `bcm63xx_udc_dequeue()` completes the request after releasing the lock even if the request was not found, so callers rely on valid queued requests. Shutdown waits by polling `ep0state` with sleeps, which is sensitive to worker progress and memory barriers. Several paths use SoC-specific global register writes, making port-number and clock ordering mistakes high impact.

## Test Signals
Useful validation signals are successful enumeration at full and high speed, `testusb` transfer and cancellation tests with `irq_coalesce=0`, explicit regression checks with `irq_coalesce=1`, SET_CONFIGURATION/SET_INTERFACE gadget callbacks, EP0 IN/OUT control transfers, stall/wedge persistence across CLEAR_FEATURE and reset, link down/reset callbacks, debugfs descriptor state, and suspend/resume or pullup cycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bcm63xx_udc.c -->
