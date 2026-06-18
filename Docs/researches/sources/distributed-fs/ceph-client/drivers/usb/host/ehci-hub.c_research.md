<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hub.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hub.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hub.c` is included by `ehci-hcd.c` and implements EHCI root-hub behavior: hub status bitmaps, hub descriptors, hub control requests, port reset/resume/suspend/power handling, companion-controller handover, wakeup flag adjustment, and bus suspend/resume. The source was read as a complete 1222-line file.

## Important APIs, Types, and Functions

Important functions include `ehci_adjust_port_wakeup_flags()` exported to platform code, `ehci_bus_suspend()`, `ehci_bus_resume()`, `ehci_get_resuming_ports()`, `set_owner()`, `check_reset_complete()`, `ehci_hub_status_data()`, `ehci_hub_descriptor()`, `ehci_hub_control()`, `ehci_relinquish_port()`, `ehci_port_handed_over()`, and `ehci_port_power()`. PM helpers include `ehci_handover_companion_ports()` and `persist_enabled_on_companion()`.

## Control Flow

The USB hub core calls `ehci_hub_status_data()` to build a change bitmap from STS_PCD/per-port-change bits, port-change bits, reset timers, suspend-change flags, and controller quirks. `ehci_hub_control()` handles standard hub requests: clearing port features, getting hub descriptors/status, getting port status with reset/resume completion, setting suspend/power/reset/test features, and erroring with `-EPIPE` for invalid requests. Reset is two-phase: SetPortFeature RESET starts the reset and sets `reset_done`; later GetPortStatus clears reset, handoffs low/full-speed ports to companions if needed, and reports change bits.

Bus suspend manually suspends each enabled port, tracks `bus_suspended` and `owned_ports`, programs wake bits, optionally enters TDI PHY low-power mode, halts the controller, cancels timers, and enables wake-capable interrupts. Bus resume reprograms frame-list and async pointers, restarts command, clears PHY low-power mode, resumes suspended ports for `USB_RESUME_TIMEOUT`, clears resume bits, hands companion-owned ports back, and re-enables interrupts.

## State and Persistence Behavior

State is stored in EHCI bitmaps and arrays such as `bus_suspended`, `owned_ports`, `suspended_ports`, `resuming_ports`, `port_c_suspend`, and `reset_done[]`, plus hardware port-status and hostpc registers. No file-backed persistence exists. Across power loss, companion ports may need reset/handover and the root hub may be marked lost power by outer PM code.

## Dependencies and Integration Points

The file depends on the USB hub core request model, EHCI register definitions, HCD timers/root-hub polling, optional OTG HNP, optional USB HCD test mode, companion controller ownership conventions, and platform quirks exposed through fields in `struct ehci_hcd`.

## Risks and Edge Cases

Port-state transitions are timing-sensitive and depend on callers issuing GetPortStatus after reset. Wakeup bits can cause false wakeups on some controllers. Companion handover must preserve persistent USB 1.1 devices but avoid delaying resume unnecessarily. Overcurrent behavior varies and may require power cycling or ignoring spurious signals. TDI PHY low-power mode requires lock drops and sleeps. Test mode deliberately halts/quiesces the controller.

## Test Signals

Test root-hub descriptor/status requests, per-port power control, reset completion, low/full-speed handoff to companions, integrated-TT ports, selective suspend/resume, remote wakeup, bus suspend/resume with persistent USB 1.1 devices, overcurrent reporting, `USB_HCD_TEST_MODE`, OTG HNP suspend clear, and controller quirks such as FSL suspend/high-speed errata and TDI PHY LPM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hub.c -->
