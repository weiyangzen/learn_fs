# sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/thunderbolt.c

## Purpose

`thunderbolt.c` implements the USB Type-C Thunderbolt 3 Alternate Mode driver. It handles ordered entry and exit of cable plug altmodes and the port altmode, constructs the Thunderbolt Enter Mode VDO from device/cable capabilities, and notifies the Type-C subsystem when Thunderbolt mode becomes active.

## Important APIs, Types, and Functions

`enum tbt_state` models idle, SOP'/SOP'' enter, port enter, port exit, SOP'' exit, and SOP' exit. `struct tbt_altmode` stores state, cable reference, port altmode, two plug altmode references, computed enter VDO, work item, and mutex. Key functions are `tbt_ready()`, `tbt_enter_mode()`, `tbt_enter_modes_ordered()`, `tbt_altmode_work()`, `tbt_cable_altmode_vdm()`, `tbt_altmode_vdm()`, `tbt_altmode_activate()`, `tbt_altmode_probe()`, and `tbt_altmode_remove()`.

## Control Flow

Probe allocates state, sets ops, describes the altmode as Thunderbolt3, and auto-enters if mode selection is not manual and `tbt_ready()` succeeds. `tbt_ready()` requires an eMarker cable, discovers SOP' and SOP'' plug altmodes when present, installs cable ops, and computes the Enter Mode VDO from port VDO bits, cable speed, active/passive status, rounded/optical/retimer/link-training bits, or passive USB3 fallback.

Activation enters cable altmodes in USB Type-C order: SOP', then SOP'', then the port; exit runs in reverse after the port exits. VDM ACKs from cable plugs and the port advance the state and schedule work. If entering SOP' fails, the driver drops plug references and directly enters the port altmode. A port ENTER_MODE ACK sends `typec_altmode_notify()` with `struct typec_thunderbolt_data` including device mode, enter VDO, and optional cable mode.

## State and Persistence Behavior

State is in-memory per altmode: current state, cable/plug references, computed enter VDO, and work item. Runtime effects are Type-C altmode active/modal notifications and cable/port mode entry/exit commands. There is no persistent storage.

## Dependencies and Integration Points

The driver depends on Type-C altmode and cable APIs, USB PD VDO helpers, Thunderbolt Type-C VDO definitions, mutex/workqueue infrastructure, and the Type-C altmode bus. It registers for `USB_TYPEC_TBT_SID` with module name `typec-thunderbolt`.

## Risks and Edge Cases

Thunderbolt 3 requires an eMarker cable, but the driver accepts systems without visible SOP'/SOP'' plug altmodes and relies on port-level ordering in that case. State transitions reject overlapping VDM handling with `-EBUSY`. Remove releases plug and cable references but does not explicitly cancel the work item, so removal ordering must ensure no scheduled work uses freed devm state. Enter VDO construction depends on correct cable capability VDO parsing.

## Test Signals

Test active and passive cables, missing eMarker rejection, SOP' only, SOP' plus SOP'', no plug altmode fallback, automatic and manual activation, NAKed enter mode, cable entry failure fallback, ordered exit after port exit ACK, Type-C modal notification payload, and disconnect/remove while work is pending.
