# sources/distributed-fs/ceph-client/drivers/usb/gadget/epautoconf.c

## Purpose
`epautoconf.c` provides endpoint autoconfiguration helpers so gadget function drivers can request endpoints by descriptor requirements instead of hard-coding controller endpoint names or numbers. It assigns endpoint addresses, sets initial max packet values, marks endpoints claimed, and resets/releases autoconfig state.

## Important APIs, Types, and Functions
Exports are `usb_ep_autoconfig_ss()`, `usb_ep_autoconfig()`, `usb_ep_autoconfig_release()`, and `usb_ep_autoconfig_reset()`. The inputs are `struct usb_gadget`, `struct usb_endpoint_descriptor`, and optionally `struct usb_ss_ep_comp_descriptor`. The code relies on controller `gadget->ops->match_ep` when present and otherwise uses `usb_gadget_ep_match_desc()` over `gadget->ep_list`.

## Control Flow
`usb_ep_autoconfig_ss()` first lets the UDC choose an endpoint with `match_ep()`. If that fails, it scans unclaimed endpoints for descriptor compatibility. Once found, it fills `wMaxPacketSize` from `ep->maxpacket_limit` if the function left it zero, derives an endpoint address either from numeric endpoint names like `ep2...` or from gadget `in_epnum`/`out_epnum` counters, assigns `ep->address`, clears `ep->desc` and `ep->comp_desc`, and marks `ep->claimed`. `usb_ep_autoconfig()` wraps the SS helper and caps full-speed bulk maxpacket at 64 bytes. Release and reset clear `claimed`/`driver_data`; reset also zeros the address counters.

## State and Persistence
Autoconfig state is held on each `struct usb_ep` (`claimed`, `address`, `driver_data`) and on the gadget counters `in_epnum` and `out_epnum`. It persists during a bind/config construction pass and is reset between configurations or on cleanup by composite/configfs code.

## Dependencies and Integration Points
Function bind methods for ACM, ECM, EEM, and other functions call these helpers before `usb_assign_descriptors()`. Composite code calls `usb_ep_autoconfig_reset()` after adding configs and during cleanup. The UDC can override matching via `match_ep`, enabling hardware-specific constraints.

## Risks
Endpoint address derivation from `ep->name[2]` assumes common endpoint naming and falls back to counters with a 15 endpoint limit. A selected endpoint may not be optimal for controller-specific FIFO/transfer constraints. Releasing an endpoint invalidates it for the releasing function. Missing reset between alternate configuration construction could cause false endpoint exhaustion.

## Test Signals
Test UDCs with and without `match_ep`, named and unnamed endpoint patterns, bulk/interrupt/isoc descriptors, SuperSpeed companion descriptors, counter overflow beyond endpoint 15, release/rebind paths, and multi-configuration gadgets that need different endpoint assignments.
