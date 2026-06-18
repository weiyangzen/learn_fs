# sources/distributed-fs/ceph-client/drivers/greybus/interface.c

## Purpose

`interface.c` manages Greybus physical interfaces on modules. It powers interfaces on and off through SVC, reads UniPro DME identity/status attributes, creates routes, handles mode switching and mailbox events, exposes sysfs power/identity attributes, manages runtime PM, retrieves manifests through the control connection, and registers child bundles.

## Important APIs, Types, and Functions

- `gb_interface_create()`, `gb_interface_add()`, `gb_interface_del()`, and `gb_interface_put()` manage device lifetime.
- `gb_interface_activate()` powers VSYS/REFCLK/UniPro, runs SVC interface activation, reads DME attributes, and creates a route.
- `gb_interface_enable()` clears init status, creates/enables control, fetches and parses manifest, gets bundle versions, registers control, enables runtime PM, and adds bundles.
- `gb_interface_disable()` destroys bundles, sends deactivate prepare when appropriate, tears down control, and disables runtime PM.
- `gb_interface_deactivate()` destroys route, hibernates link, disables UniPro/REFCLK/VSYS, and clears active state.
- `gb_interface_mailbox_event()` and `gb_interface_request_mode_switch()` coordinate Greybus mode switching.
- Runtime PM callbacks suspend by preparing control, suspending control, hibernating the link, and disabling REFCLK; resume reenables REFCLK, sends SVC resume, and resumes control.

## Control Flow

Activation is layered: reject ejected/removed interfaces, enable VSYS, enable REFCLK, enable UniPro, ask SVC to activate and report type, read DME identity, allocate/set a device ID and route, then mark active. Enabling assumes the interface is active, checks init status, builds a control connection, fetches the manifest, creates bundles from the manifest, registers control, enables runtime PM, and adds bundle devices in reverse-safe order.

Disable and deactivate reverse those stages under the interface mutex. Mailbox mode switching takes an extra control reference, disables the interface, waits for completion signaled by a mailbox event, then re-enables if still active. Legacy bootrom quirks may force disable/re-enable without the normal completion protocol.

## State and Persistence Behavior

`struct gb_interface` persists as a module child device. Key mutable fields include `type`, `features`, DME IDs, GMP IDs, serial number, `quirks`, `device_id`, `active`, `enabled`, `disconnected`, `ejected`, `removed`, `mode_switch`, control pointer, manifest descriptor list, and bundle list. The interface mutex serializes activation, enable/disable, mailbox handling, and sysfs power changes.

## Dependencies and Integration Points

This file depends on SVC management operations, control protocol operations, manifest parsing, bundle lifecycle, Greybus bus/device types, runtime PM, Linux completion/workqueue primitives, and Toshiba ES2/ES3 DME quirks. It feeds bundle devices into the bus core so protocol drivers can bind.

## Risks and Edge Cases

- Many error paths perform best-effort power unwind; failures during unwind are logged by lower helpers but cannot fully restore hardware.
- ES2/ES3 bootrom quirks encode board-specific behavior in generic interface code.
- `gb_interface_type_string()` indexes a fixed array by `intf->type`; invalid out-of-range values would be unsafe if introduced.
- `gb_interface_disable()` calls `pm_runtime_get_sync()` without checking its return.
- Mode switch, disconnect, forced-disable, and remove flags interact; tests should cover concurrent mailbox and removal paths.

## Test Signals

Cover activation success and each staged failure, DME read caching, ES2 init-status behavior, route ID allocation/release, manifest fetch/parse failures, bundle add failures, sysfs `power_state`, pwrmon attributes, runtime PM suspend/resume, mailbox success/error/unexpected value, legacy mode switch, and module removal while mode switch work is queued.
