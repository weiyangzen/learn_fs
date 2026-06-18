# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_gadget_ep0.c

## Purpose

`musb_gadget_ep0.c` implements peripheral-mode endpoint zero control transfer handling for MUSB. It services standard USB requests that the controller driver must handle itself, forwards class/vendor or configuration requests to the gadget driver, drives the EP0 state machine, queues the gadget driver's EP0 response buffers, and exposes `musb_g_ep0_ops`. The source was read as a complete 1058-line file.

## Important APIs, Types, and Functions

The externally used entry point is `musb_g_ep0_irq`, and the exported operation table is `musb_g_ep0_ops`. Important helpers are `decode_ep0stage`, `service_tx_status_request`, `service_in_request`, `service_zero_data_request`, `musb_g_ep0_giveback`, `musb_try_b_hnp_enable`, `ep0_rxstate`, `ep0_txstate`, `musb_read_setup`, `forward_to_driver`, `musb_g_ep0_queue`, and `musb_g_ep0_halt`.

## Control Flow

The core calls `musb_g_ep0_irq` when EP0 interrupts arrive. The handler selects EP0, reads CSR0 and COUNT0, acknowledges sent stalls and SETUPEND, then dispatches based on `musb->ep0_state`. In setup state it reads an eight-byte `usb_ctrlrequest`, clears any previous queued EP0 request, sets `ackpend`, decides whether the request has no data, IN data, or OUT data, and handles mandatory standard requests locally where possible. Unhandled requests are forwarded to `gadget_driver->setup` with the controller lock dropped. For IN data, `musb_g_ep0_queue` can immediately call `ep0_txstate` to load the FIFO; for OUT data, the queued buffer is filled by `ep0_rxstate`. Status phases update address/test-mode state, complete any remaining request, and return to idle/setup.

## State and Persistence Behavior

EP0 state lives in `musb->ep0_state`, `ackpend`, `set_address`, `address`, `test_mode`, `test_mode_nr`, wakeup/HNP flags, and the EP0 request list (`musb->endpoints[0].ep_in`). The controller lock protects both queue and state except during gadget driver callbacks. There is no persistent storage.

## Dependencies and Integration Points

The file depends on USB control request definitions, gadget driver setup callbacks, MUSB CSR0/FADDR/TESTMODE registers, `musb_g_giveback` and `musb_ep_restart` from gadget support, FIFO helpers, OTG/HNP state, and EP0 stage constants from `musb_core.h`. It is tightly integrated with `musb_gadget.c` for request allocation and completion.

## Risks and Edge Cases

The delicate areas are correct delayed acknowledgement through `ackpend`, handling setup/status coalescing, preventing address changes until after status, not accepting OUT data without a driver-provided buffer, and allowing callbacks to stall while the lock is temporarily dropped. Test mode and HNP feature requests also depend on speed and OTG capability checks. EP0 dequeue is unsupported, so gadget functions must tolerate that contract.

## Test Signals

USB Chapter 9 enumeration tests are the primary signal: GET_STATUS, SET_ADDRESS, SET_CONFIGURATION delegation, endpoint halt set/clear, remote wakeup feature, malformed setup length, EP0 IN/OUT data stages, zero-data status handling, test mode requests at high speed, and gadget driver setup returning stalls.
