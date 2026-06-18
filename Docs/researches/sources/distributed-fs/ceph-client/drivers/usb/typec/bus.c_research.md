<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/bus.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/bus.c

## Purpose

`bus.c` implements the USB Type-C alternate-mode bus. It binds partner alternate-mode devices to alternate-mode drivers, creates sysfs cross-links between port and partner altmodes, forwards Enter/Exit/Attention/VDM/cable VDM operations, and coordinates mux/retimer state changes for negotiated alternate-mode configurations.

## Important APIs, Types, and Functions

Exported APIs include `typec_altmode_notify()`, `typec_altmode_enter()`, `typec_altmode_exit()`, `typec_altmode_attention()`, `typec_altmode_vdm()`, cable variants, `typec_altmode_get_partner()`, `typec_altmode_get_plug()`, `typec_altmode_put_plug()`, `__typec_altmode_register_driver()`, `typec_altmode_unregister_driver()`, and `typec_match_altmode()`. Internal helpers convert `struct altmode` to `struct typec_mux_state` and `struct typec_retimer_state` before calling `typec_mux_set()` and `typec_retimer_set()`.

## Control Flow

Alternate-mode entry first moves the associated port mux/retimer to safe state, checks that the paired port altmode supports `enter`, and blocks partner entry when the port mode is inactive. Exit similarly moves to safe state before invoking the peer `exit`. Notifications configure retimer/mux state and optionally call the peer `notify`. Cable helpers dispatch to registered `cable_ops` on either plug or partner endpoints. Bus matching only binds drivers to partner altmode devices by SVID. Probe creates reciprocal sysfs links and calls the altmode driver's `probe`; remove removes links, calls driver `remove`, forces safe state for active modes, clears active state, and clears ops/description.

## State and Persistence Behavior

Persistent storage is limited to in-memory `struct altmode` relationships: `partner`, `plug[]`, cached mux/retimer references, ops, active flag, and sysfs links. No file-backed persistence exists. Device references and module references are maintained by the core class and bus registration paths.

## Dependencies and Integration Points

The bus depends on `bus.h`, `class.h`, `mux.h`, retimer helpers, Linux driver core bus registration, sysfs links, uevents, and USB PD VDO definitions. It is used by DisplayPort, Thunderbolt, USB4, and vendor altmode drivers to communicate with Type-C port controllers and mux/retimer hardware.

## Risks and Test Signals

Risks include incorrect partner linkage, safe-state failures leaving muxes active, cable SOP index handling, module lifetime when active altmode drivers are removed, and a duplicated `if (!adev)` line in `typec_altmode_vdm()` in this source snapshot. Test signals include driver modalias `typec:id%04X`, sysfs `port`/`partner` links, enter/exit ordering with mux safe state, notify propagation into mux/retimer callbacks, cable plug VDM dispatch, and removal of an active altmode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/bus.c -->
