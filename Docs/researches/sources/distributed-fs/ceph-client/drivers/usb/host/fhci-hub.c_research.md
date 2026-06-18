# sources/distributed-fs/ceph-client/drivers/usb/host/fhci-hub.c

## Purpose
`fhci-hub.c` implements the FHCI virtual root hub and the physical single-port transceiver controls behind it. It translates USB core hub requests into virtual hub status changes, QE GPIO transceiver configuration, port reset signaling, SOF timer control, and FHCI port enable/disable behavior.

## Important APIs, Types, and Functions
- Root hub callbacks exported to `fhci_driver`: `fhci_hub_status_data()` and `fhci_hub_control()`.
- Port and transceiver operations: `fhci_config_transceiver()`, `fhci_port_disable()`, `fhci_port_enable()`, `fhci_io_port_generate_reset()`, and `fhci_port_reset()`.
- `root_hub_des` describes a one-port USB hub with individual port power switching and no over-current protection.

## Control Flow
Hub status checks inspect `vroot_hub->port.wPortChange` under the FHCI lock and report bit 1 for the single downstream port. Hub control handles standard USB hub requests. `GetHubDescriptor`, `GetHubStatus`, and `GetPortStatus` return virtual structures. `SetPortFeature(POWER)` powers the transceiver and enters waiting state. `SetPortFeature(RESET)` sets reset status, calls `fhci_port_reset()`, enables the port, and clears reset. `SetPortFeature(ENABLE)` calls `fhci_port_enable()`. Clear-feature paths clear virtual status/change bits and may disable port power, stop SOF, or disable the port.

Physical reset disables SOF and the USB controller, masks idle interrupts, drives USBOE/USBTP/USBTN GPIOs low for reset, restores them to dedicated QE pins, restores interrupts, re-enables the controller, and restarts SOF. Port disable stops SOF, flushes transmissions, masks interrupts, switches `port_status` to disabled, enables IDLE detection for future connect, updates virtual hub enable-change bits, and re-enables interrupts.

## State and Persistence Behavior
State is maintained in `fhci_usb->port_status`, `fhci->vroot_hub`, `saved_msk`, transceiver GPIO outputs, QE pin mux state, and USB mode/mask registers. The virtual root hub is volatile and reconstructed during HCD start. GPIO power/speed values may persist electrically until changed by remove or platform reset.

## Dependencies and Integration Points
This file integrates Linux USB hub request constants, GPIO descriptor operations, QE pin muxing, FHCI scheduler/TD flush functions, and FHCI SOF timer helpers. It depends on `fhci_ioports_check_bus_state()` and device connect/disconnect handling in `fhci-sched.c` for connection detection after IDLE/RESET events.

## Risks and Test Signals
Risks include sleeping `mdelay()` calls while called under the HCD spinlock from hub control, assumptions about one-port topology, subtle saved interrupt mask updates, GPIO polarity/ordering mistakes, and races between disable/reset and simultaneous connect events. Test signals include hub descriptor correctness, hub status bitmap on connect/enable/reset/suspend/power changes, reset timing with enumeration, optional speed/power GPIO absence, and disconnect/reconnect during port disable.
