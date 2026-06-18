# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-hub.c

## Purpose

`ohci-hub.c` implements OHCI root-hub behavior: hub status bitmaps, hub-control requests, port reset sequencing, root-hub suspend/resume, polling/autostop decisions, and OTG port reset support.

## Important APIs, Types, and Functions

Exported functions are `ohci_hub_status_data()` and `ohci_hub_control()`. PM builds add `ohci_rh_suspend()`, `ohci_rh_resume()`, `ohci_bus_suspend()`, and `ohci_bus_resume()`. Supporting helpers include `ohci_root_hub_state_changes()`, `ohci_hub_descriptor()`, `root_port_reset()`, `find_head()`, and optional `ohci_start_port_reset()`.

## Control Flow

Status polling reads hub and per-port change bits, clears RHSC before scanning ports, builds the USB hub change bitmap, and decides whether to keep polling or re-enable RHSC interrupts. Hub control maps USB hub requests to OHCI root-hub register writes, including clearing change bits, returning descriptors/status, powering ports, suspending ports, and issuing port reset pulses. Suspend first quiesces schedules, processes done/unlink work, optionally suspends every enabled port for global-suspend quirk hardware, configures remote wakeup, and writes `OHCI_USB_SUSPEND`. Resume handles normal resume, autostop resume, lost-power restart, schedule-head restoration, interrupt reenabling, and schedule restart.

## State and Persistence Behavior

The file mutates `ohci->hc_control`, `ohci->rh_state`, `ohci->autostop`, `ohci->next_statechange`, ED schedule heads, interrupt enables, and root-hub registers. Port power, reset, suspend, overcurrent, and change bits live in OHCI hardware registers. No persistent storage is used.

## Dependencies and Integration Points

It depends on USB hub class request constants, OHCI root-hub bit definitions, HCD polling flags, PM configuration, and `ohci_work()`/`update_done_list()` from queue handling. It is wired into the generic `hc_driver` root-hub callbacks and into `ohci_irq()` RHSC/RD paths.

## Risks and Test Signals

Risks include controller-specific RHSC level/edge behavior, races between polling and interrupt reenabling, reset timing on slow ports, suspend while schedules still hold retiring TDs, and autostop decisions that depend on remote-wakeup capability. Test signals include `GetHubDescriptor`, `GetPortStatus`, port power/reset/suspend requests, connect/disconnect wakeups, remote-wakeup resume, global-suspend quirk systems, and controllers with more than seven root ports.
