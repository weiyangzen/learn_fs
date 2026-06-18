# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_typec.c

## Purpose
`cros_ec_typec.c` maps Chrome EC USB-C/USB-PD state into the Linux Type-C class. It registers Type-C ports from firmware-described child nodes, performs data/power role swaps through EC PD control commands, manages partner/cable/plug/altmode/PD capability objects, updates orientation/role-switch/mux/retimer state, handles EC Type-C status/discovery events, and refreshes ports on USB-PD notifications and resume.

## Important APIs, Types, and Functions
- Type-C operations: `cros_typec_enter_usb_mode()`, `cros_typec_dr_swap()`, and `cros_typec_pr_swap()`.
- Port setup helpers: `cros_typec_parse_port_props()`, `cros_typec_get_switch_handles()`, `cros_typec_register_port_altmodes()`, and `cros_typec_init_ports()`.
- Object lifecycle helpers: `cros_typec_add_partner()`, `cros_typec_remove_partner()`, `cros_typec_remove_cable()`, `cros_unregister_ports()`, and `cros_typec_unregister_altmodes()`.
- Mux/mode helpers: `cros_typec_usb_disconnect_state()`, `cros_typec_usb_safe_state()`, `cros_typec_enable_tbt()`, `cros_typec_enable_dp()`, `cros_typec_enable_usb4()`, and `cros_typec_configure_mux()`.
- Discovery/status helpers: `cros_typec_handle_sop_disc()`, `cros_typec_handle_sop_prime_disc()`, `cros_typec_register_partner_pdos()`, `cros_typec_handle_status()`, and `cros_typec_port_update()`.
- Probe/remove/PM and notifier glue: `cros_typec_probe()`, `cros_ec_typec_event()`, suspend/resume callbacks.

## Control Flow
Probe allocates `struct cros_typec_data`, finds the parent EC, queries supported `EC_CMD_USB_PD_CONTROL` version, checks EC features for Type-C status commands, mux acknowledgments, and AP-driven altmode entry, reads EC PD port count, initializes Type-C ports from child firmware nodes, performs an initial update for every port, then registers a USB-PD notifier. Notifications flush and schedule work that updates every port. Each port update queries `EC_CMD_USB_PD_CONTROL`, configures mux/retimer/role/orientation based on `EC_CMD_USB_PD_MUX_INFO`, updates Type-C role/orientation/partner state according to PD control version, and optionally handles Type-C status events from `EC_CMD_TYPEC_STATUS`.

## State and Persistence
`struct cros_typec_data` stores global driver state: EC pointer, number of ports, PD control version, feature flags, notifier, work item, and per-port pointers. Each `struct cros_typec_port` stores Type-C class objects, switch/mux/retimer/role-switch handles, current mux flags and PD role, mux state, registered port altmodes, partner/cable identities, discovery completion flags, discovery response buffer, altmode lists, and partner PD capability objects. State persists until disconnect, hard reset, driver removal, or suspend cancellation/resume refresh.

## Dependencies and Integration Points
The driver depends on ACPI/OF child port descriptions, Linux Type-C class, USB role switch, typec mux/switch/retimer APIs, USB PD VDO helpers, Chrome EC command helpers, `cros_usbpd_notify`, and local helpers in `cros_typec_vdm.h` and `cros_typec_altmode.h`. It binds to ACPI `"GOOG0014"` and OF `"google,cros-ec-typec"`.

## Risks and Edge Cases
The code must keep EC state and Type-C class objects synchronized through asynchronous notifications. Missing mux/switch/retimer/role-switch handles are logged, with `-EPROBE_DEFER` causing probe retry; later paths still call these handles when ports exist, so null/error cleanup correctness matters. Hard reset removes partner and cable state and clears the event. Discovery events are ignored once the corresponding done flag is set. Mux state updates are skipped when flags and role are unchanged. Mode setup for DP/TBT requires PD control v2 data; older ECs return `-ENOTSUPP`. Mux acknowledgment failures are warning-only.

## Test Signals
No local KUnit tests are present. Runtime signals include successful Type-C port registration, role swap behavior, partner/cable/altmode objects under sysfs, mux/retimer state changes for USB/DP/TBT/USB4, PD capability registration, and correct refresh after USB-PD notifications or resume.
