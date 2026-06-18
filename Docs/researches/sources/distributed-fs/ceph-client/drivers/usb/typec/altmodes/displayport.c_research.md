# sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/displayport.c

## Purpose

`displayport.c` implements the USB Type-C DisplayPort Alternate Mode driver. It negotiates DP mode entry, status update, cable plug configuration, pin assignment, HPD/IRQ_HPD reporting, sysfs controls, DRM out-of-band hotplug notification, and optional active-cable SOP' handling.

## Important APIs, Types, and Functions

`struct dp_altmode` stores port/partner/cable data, current and cable-prime DP status/configuration VDOs, state machine state, HPD flags/counters, mutex/work item, typec altmode pointers, connector fwnode, and optional SOP' plug. Core functions include `dp_altmode_configure()`, `dp_altmode_status_update()`, `dp_altmode_configure_vdm()`, `dp_altmode_configure_vdm_cable()`, `dp_altmode_work()`, `dp_altmode_attention()`, `dp_altmode_vdm()`, `dp_cable_altmode_vdm()`, `dp_altmode_activate()`, `dp_altmode_probe()`, and `dp_altmode_remove()`. Sysfs attributes are `displayport/configuration`, `pin_assignment`, `hpd`, and `irq_hpd`.

## Control Flow

Probe requires the local Type-C data role to be host/DFP_U and verifies compatible pin assignments between port and partner. It gets an optional SOP' plug, installs Type-C altmode/cable ops, resolves the connector firmware node, and auto-enters either SOP' then SOP or SOP directly when mode selection is automatic. The work item serializes entry, status update, configure, and exit states.

VDM ACKs advance the state machine: ENTER_MODE triggers status update, STATUS_UPDATE records the partner status and may choose a configuration, CONFIGURE notifies that configuration is active, and EXIT_MODE clears active state and HPD. ATTENTION updates status and can schedule configure/exit work. Configuration selection intersects port, partner, and cable signaling/pin capabilities, honors multi-function preference, defaults to pin C when available for DP-only assignments, and sends the connector to safe mode before reconfiguring. Sysfs stores allow userspace to request source/sink/USB mode or a specific pin assignment when supported.

## State and Persistence Behavior

State is in-memory per altmode: DP status VDOs, configuration VDOs, state enum, HPD state, pending HPD/IRQ flags, IRQ counter, plug reference, and connector fwnode reference. The driver emits Type-C modal-state notifications, sysfs notifications, and DRM hotplug events; it does not persist settings to disk or firmware.

## Dependencies and Integration Points

The driver depends on Type-C altmode bus APIs, USB PD VDO helpers, DisplayPort altmode definitions, DRM connector hotplug notification, firmware-node properties, mutexes, and workqueues. It exports `dp_altmode_probe()` and `dp_altmode_remove()` for the NVIDIA VirtualLink wrapper.

## Risks and Edge Cases

The state machine returns `-EBUSY` while another VDM transaction is active, so callers must retry rather than overlap operations. Cable SOP' support can be dropped on entry/configuration failure, then the driver retries without the plug. HPD can arrive before configuration and is deferred until configuration completes. Pin assignment logic depends on correctly intersecting DFP/UFP and active-cable capabilities; a bad choice can break display connectivity or USB lane sharing. The sysfs `pin_assignment_store()` has a TODO for manual SOP' cable configure.

## Test Signals

Test automatic and manual mode selection, SOP' active cable entry/configuration failure fallback, source and sink configurations, multi-function preference, all supported pin assignments, status update NAK leading to exit, configure NAK fallback, ATTENTION during non-idle state, HPD and IRQ_HPD sysfs notifications, DRM hotplug fwnode resolution, sysfs invalid values, and remove cleanup/disconnect notification.
