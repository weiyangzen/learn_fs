# sources/distributed-fs/ceph-client/drivers/usb/isp1760/isp1760-udc.h

## Purpose
`isp1760-udc.h` declares the device-controller private state and public registration API for the ISP1761/ISP1763 gadget role. It also provides disabled-role stubs when UDC support is not compiled.

## Important APIs, Types, And Functions
`enum isp1760_ctrl_state` models EP0 as setup, data-in, data-out, or status. `struct isp1760_ep` embeds a `usb_ep`, request queue, endpoint address/name, maxpacket, descriptor pointer, and flags for pending RX, halt, and wedge. `struct isp1760_udc` embeds the common device pointer, IRQ metadata, regmap and fields, gadget driver and gadget object, spinlock, VBUS timer, endpoint array, EP0 state fields, connection flag, variant flag, and device status bits. Public functions are `isp1760_udc_register()` and `isp1760_udc_unregister()`, or stubs.

## Control Flow
The header has no executable flow. Registration and endpoint logic in `isp1760-udc.c` mutate these structures under `lock`, especially around banked endpoint register selection and EP0 state transitions.

## State And Persistence
The structures define all volatile UDC state for a bound controller. Endpoint queues persist while a gadget function is bound and endpoints are enabled. Device status tracks self-powered state and is reported through standard GET_STATUS.

## Dependencies And Integration Points
The header depends on ioport, list, spinlock, timer, USB gadget types, and local register definitions. It is embedded by `struct isp1760_device` in the common core.

## Risks
The endpoint array is fixed at 15 entries, representing EP0 plus IN/OUT pairs for endpoints 1-7. Hardware or driver changes for more endpoints require array, IRQ dispatch, and naming changes. The spinlock comment defines ownership for driver, timer, endpoint, EP0, and `DC_EPINDEX`; violating that contract can corrupt banked endpoint register accesses.

## Test Signals
Build gadget-disabled and gadget-enabled configurations. Runtime gadget tests should validate endpoint enumeration, queue lifetime, halt/wedge state, EP0 transitions, and unregister after active gadget use.
