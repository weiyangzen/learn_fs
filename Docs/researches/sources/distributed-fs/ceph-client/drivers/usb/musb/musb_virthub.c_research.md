# sources/distributed-fs/ceph-client/drivers/usb/musb/musb_virthub.c

## Purpose

`musb_virthub.c` implements the single-port virtual root hub used when MUSB operates as a host. It translates usbcore hub class requests into MUSB port power, reset, suspend, resume, test-mode, disconnect, and status-change behavior. The source was read as a complete 439-line file.

## Important APIs, Types, and Functions

Public functions are `musb_host_finish_resume`, `musb_port_suspend`, `musb_port_reset`, `musb_root_disconnect`, `musb_hub_status_data`, and `musb_hub_control`. `musb_has_gadget` is an internal helper used to avoid starting sessions in OTG mode before a gadget is available.

## Control Flow

USB hub requests enter through `musb_hub_control`. Clear/set hub features are mostly NOPs; port feature requests drive suspend, reset, power, and test behavior; descriptor/status requests synthesize a one-port hub descriptor and return `musb->port1_status`. Setting port power may call `musb_start` after dropping the lock. Port reset asserts MUSB_POWER_RESET and schedules delayed deassertion; deassertion updates high-speed status, enable/change bits, and polls root hub status. Suspend sets SUSPENDM and updates OTG state; resume sets RESUME and schedules `musb_host_finish_resume`, which clears resume and reports status changes.

## State and Persistence Behavior

The file mutates `musb->port1_status`, `is_active`, OTG state, timers/delayed work, VBUS retry count, and gadget A-peripheral flags during HNP transitions. State is runtime-only but visible to usbcore through root hub status polling.

## Dependencies and Integration Points

It depends on usbcore HCD hub callbacks, MUSB power/devctl/testmode registers, delayed work, OTG state helpers, platform VBUS and root-reset hooks, and `usb_hcd_poll_rh_status`. Host setup in `musb_host.c` registers these functions through `hc_driver`.

## Risks and Edge Cases

Root hub state must match both USB hub semantics and OTG state transitions. Reset/resume timing is compliance-sensitive, and the code has platform hooks for root reset end. Host-only and OTG behavior differs around gadget availability, VBUS power, B-host/A-host transitions, and HNP. Incorrect change-bit clearing can make usbcore miss connect/reset/suspend events.

## Test Signals

Signals include hub descriptor/status queries, connect/disconnect notification, port power on/off, reset timing during enumeration, suspend/resume compliance, high-speed detection, OTG HNP paths, USB test-mode feature requests, and status-change polling through `usb_hcd_poll_rh_status`.
