# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_gadget_ep0.c

## Purpose

`mtu3_gadget_ep0.c` implements control endpoint 0 handling for MTU3 gadget mode. It manages SETUP decoding, standard USB requests handled by the controller, forwarding class/vendor requests to the gadget driver, PIO FIFO transfers, delayed status, stalls, and EP0 interrupt state transitions.

## Important APIs, Types, and Functions

Key functions include `ep0_read_setup()`, `ep0_handle_setup()`, `handle_standard_request()`, `ep0_get_status()`, `ep0_handle_feature()`, `ep0_set_sel()`, `handle_test_mode()`, `ep0_rx_state()`, `ep0_tx_state()`, `ep0_stall_set()`, `ep0_queue()`, and public `mtu3_ep0_isr()`. `mtu3_ep0_ops` exposes the EP0-specific endpoint operations.

## Control Flow

The EP0 ISR reads EP interrupt status, clears W1C bits, handles SETUPEND and sent-stall cleanup, then dispatches by `mtu->ep0_state`. SETUP state reads exactly eight bytes, completes any leftover EP0 request, chooses TX or RX data stage based on direction, handles standard requests locally when required, or forwards to the gadget driver. TX state writes maxpacket-sized chunks to FIFO and transitions to TX_END when complete; RX state reads FIFO packets until short or full request completion. Delayed status is recorded until a later EP0 queue call triggers the status stage.

## State and Persistence Behavior

EP0 state is runtime-only: `ep0_state`, `address`, `may_wakeup`, U1/U2 flags, `delayed_status`, `test_mode`, `test_mode_nr`, and the reusable `ep0_req`/`setup_buf`. The device address and link-power bits are mirrored into hardware registers during standard request handling.

## Dependencies and Integration Points

The file depends on USB chapter 9 definitions, composite gadget setup callbacks, MTU3 MMIO registers, debug trace helpers, and request completion from `mtu3_gadget.c`. It is invoked from the core IRQ path under `mtu->lock`.

## Risks and Test Signals

Risks include malformed SETUP lengths, request queue busy behavior, pointer use for `setup_buf`, test mode entering hardware state that requires platform restart, function-suspend forwarding, and correct lock release around gadget driver setup callbacks. Test signals include enumeration through SET_ADDRESS and SET_CONFIGURATION, GET_STATUS for device and endpoints, SET/CLEAR_FEATURE for halt, remote wake, U1/U2, SET_SEL six-byte OUT stage, delayed status from composite drivers, EP0 stall clear on next setup, and USB2 electrical test modes.
