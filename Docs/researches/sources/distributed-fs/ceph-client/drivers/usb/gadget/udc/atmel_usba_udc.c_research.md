# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/atmel_usba_udc.c

## Purpose
Implements the Atmel/Microchip USBA high-speed USB device controller driver. It supports EP0 control handling, configurable endpoint FIFO layouts, DMA-capable endpoint transfers, FIFO fallback, debugfs inspection, VBUS-triggered start/stop, suspend/resume clock and bias handling, USB test modes, and OF platform binding for AT91SAM9, SAMA5D3, and SAM9X60 families.

## Important APIs, Types, And Functions
Endpoint operations are `usba_ep_enable`, `usba_ep_disable`, `usba_ep_alloc_request`, `usba_ep_free_request`, `usba_ep_queue`, `usba_ep_dequeue`, `usba_ep_set_halt`, `usba_ep_fifo_status`, and `usba_ep_fifo_flush`. Gadget operations are `usba_udc_get_frame`, `usba_udc_wakeup`, `usba_udc_set_selfpowered`, `atmel_usba_pullup`, `atmel_usba_start`, `atmel_usba_stop`, and `atmel_usba_match_ep`.

Transfer helpers include `next_fifo_transaction`, `submit_request`, `submit_next_request`, `receive_data`, `request_complete`, `request_complete_list`, `queue_dma`, `usba_update_req`, and `stop_dma`. EP0 and interrupt handling are centered on `handle_ep0_setup`, `usba_control_irq`, `usba_ep_irq`, `usba_dma_irq`, and `usba_udc_irq`. Platform/power code includes `usba_start`, `usba_stop`, `usba_vbus_irq_thread`, `start_clock`, `stop_clock`, `atmel_udc_of_init`, `usba_udc_probe`, remove, and PM callbacks.

## Control Flow
Probe maps separate control and FIFO resources, obtains clocks, initializes locks, disables the controller from a clean slate, parses OF compatible data and endpoint config, initializes endpoints and optional VBUS IRQ, registers the gadget UDC, and creates debugfs entries. Endpoint configuration is either automatic (`fifo_mode=0`, adjusted in `atmel_usba_match_ep`) or selected from static FIFO tables. Endpoint enable writes `EPT_CFG`, enables the endpoint, and enables endpoint and optional DMA interrupts; DMA endpoints set `AUTO_VALID` and disable endpoint interrupt reporting for DMA-owned transfers.

Queueing initializes request state. DMA-capable endpoints map the request, build a DMA control word, submit immediately if the queue is empty, and otherwise append to the queue. FIFO endpoints append and enable TX or RX readiness depending on direction and EP0 state. Completion removes requests, unmaps DMA when used, drops the spinlock, and calls gadget giveback.

EP0 is a state machine with `WAIT_FOR_SETUP`, data stages, status stages, address status, and test mode status. `handle_ep0_setup` handles standard GET_STATUS, CLEAR_FEATURE, SET_FEATURE, SET_ADDRESS, endpoint halt, remote wakeup, and test mode requests, delegating others to the gadget driver. `usba_control_irq` restarts until no immediately serviceable state remains, sequences TX complete and RX ready status stages, consumes setup packets, and stalls invalid state transitions.

The top-level IRQ handles suspend, wake, resume, DMA interrupts, endpoint interrupts, and bus reset. Reset reinitializes all endpoints, calls gadget reset if needed, determines speed, configures EP0, reenables key interrupts, and optionally preallocates claimed endpoint configs.

## State And Persistence Behavior
State is volatile: endpoint queues, endpoint config words, FIFO sizes/banks, DMA capability flags, EP0 state, devstatus bits, test mode, VBUS previous state, interrupt-enable cache, suspended/clocked flags, and errata bias state. `int_enb_cache` mirrors the hardware interrupt-enable register because the hardware appears to use write-style enable semantics. There is no disk persistence. Debugfs snapshots expose queues, DMA status, EP0 state, and registers when enabled.

## Dependencies And Integration Points
Depends on Linux gadget, DMA mapping, debugfs, GPIO descriptors, clocks, OF matching, syscon/regmap for PMC errata workarounds, runtime wakeup helpers, and Atmel PMC definitions. Compatible-specific endpoint arrays and errata tables cover `atmel,at91sam9rl-udc`, `atmel,at91sam9g45-udc`, `atmel,sama5d3-udc`, and `microchip,sam9x60-udc`.

## Risks
DMA queue error handling is subtle: `queue_dma` maps a request before taking the lock, but if the endpoint is no longer enabled it returns `-ESHUTDOWN` without unmapping the request. `usba_control_irq` assumes a request exists when TX ready is enabled; corrupted EP0 state or spurious bits could dereference a null request. FIFO auto-configuration changes maxpacket limits during endpoint matching, so gadget autoconfig behavior depends on call order. Suspend paths stop clocks and toggle bias; any register access while unclocked or missed bias pulse can break resume. Test mode deliberately reconfigures EP0 and resets endpoints. Interrupt status includes `USBA_HIGH_SPEED` even if not enabled, so reset speed detection relies on top-level status semantics.

## Test Signals
Validate high-speed and full-speed enumeration, EP0 standard and delegated setup requests, remote wakeup, USB test modes, DMA IN/OUT transfers including zero-length packets and 64 KiB boundary behavior, FIFO-mode transfers by disabling DMA-capable paths or using non-DMA endpoints, endpoint halt/clear, dequeue while DMA active, reset during traffic, VBUS insert/remove, suspend/resume with device wakeup, and all compatible endpoint maps. Debugfs queue/register files, DMA timeout errors, `DMA_CH_EN` warnings after completion, EP0 invalid-state stalls, and unbalanced DMA mapping reports are important signals.
