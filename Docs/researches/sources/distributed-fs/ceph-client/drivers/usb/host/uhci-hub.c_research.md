# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-hub.c

## Purpose
`uhci-hub.c` implements the virtual root-hub interface for UHCI controllers. It translates usbcore hub class requests into UHCI port status/control register operations, handles port reset/resume timing, detects root-hub status changes, and participates in the UHCI auto-stop state machine.

## Important APIs, Types, And Functions
`uhci_hub_status_data()` is the HCD root-hub change bitmap callback. It scans schedules, checks hardware accessibility, updates port reset/resume completion through `uhci_check_ports()`, computes change bits with `get_hub_status_data()`, and advances root-hub power states. `uhci_hub_control()` handles `GetHubStatus`, `GetPortStatus`, `GetHubDescriptor`, `SetPortFeature`, `ClearPortFeature`, and hub feature requests. Helper macros `CLR_RH_PORTSTAT()` and `SET_RH_PORTSTAT()` preserve write-zero and write-clear semantics. `uhci_finish_suspend()` ends resume signaling and updates change state. `any_ports_active()` feeds auto-stop decisions.

## Control Flow
Root-hub polling calls `uhci_hub_status_data()`. The function scans completed transfers first, then checks reset/resume timers and port change bits. In suspended state, a change asks usbcore to resume the root hub. In auto-stopped state, a change wakes the controller. In running state, absence of connected or changed ports transitions to `UHCI_RH_RUNNING_NODEVS`; after one second with no active ports, it auto-stops unless the HP reset quirk is active. Hub-control requests directly read or write `USBPORTSCn` registers under `uhci->lock`, converting UHCI-specific bits to USB hub status words.

## State And Persistence Behavior
Port state lives primarily in hardware `USBPORTSC` registers plus software bitmaps in `struct uhci_hcd`: `port_c_suspend`, `resuming_ports`, and `ports_timeout`. The code does not persist state across reset. Change bits are cleared by writing register values with UHCI R/WC rules or clearing software bitmaps.

## Dependencies And Integration Points
This file is included by `uhci-hcd.c` and depends on the shared register helpers, root-hub state functions (`suspend_rh()`, `wakeup_rh()`), `ignore_oc`, usbcore hub constants, and HCD polling APIs. It uses `uhci_scan_schedule()` from queue code because root-hub polling is also a convenient completion scan point.

## Risks And Edge Cases
UHCI has no explicit `C_RESET` reporting and no port power switching, so the code synthesizes standard hub behavior. Resume signaling must be stopped by software after USB-specified timeouts; delayed or disabled ports require special handling. Overcurrent polarity varies by vendor and may be ignored globally. The HP iLO2 quirk delays reset completion. Auto-stop depends on polling cadence and could miss wakeups if RD/EGSM behavior is broken, which core code handles by forcing polling.

## Test Signals
Test hub descriptor and status requests, port connect/disconnect changes, reset completion, suspend/resume completion, overcurrent-change behavior with `ignore_oc`, auto-stop after no devices, wake from auto-stop, and HP reset-delay systems. Lockdep and race testing should cover hub requests while URBs complete.
