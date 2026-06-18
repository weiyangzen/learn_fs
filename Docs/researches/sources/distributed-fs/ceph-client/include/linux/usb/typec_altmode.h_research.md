# sources/distributed-fs/ceph-client/include/linux/usb/typec_altmode.h

## Purpose
This header defines USB Type-C Alternate Mode devices and drivers. It lets the Type-C core expose port, plug, and partner altmodes as device-model objects and lets SVID-specific drivers enter, exit, notify, and exchange VDMs.

## Important APIs, types, and functions
Key items are `typec_altmode`, `typec_altmode_ops`, `typec_cable_ops`, `typec_altmode_driver`, `typec_altmode_enter()`, `typec_altmode_exit()`, `typec_altmode_attention()`, `typec_altmode_vdm()`, cable altmode helpers, plug lookup helpers, `typec_match_altmode()`, and driver registration macros. It also defines modal connector states and special Type-C modes for USB2, USB3, USB4, audio, and debug accessories.

## Control flow, state, and persistence
Port discovery creates altmode devices with SVID/mode/VDO metadata. Matching altmode drivers bind through the Type-C bus, then invoke operation callbacks to send Enter/Exit/Attention/vendor VDMs and report asynchronous mode-selection results. Active state, priority, selected mode, and driver data are runtime device state; no persistent storage is defined.

## Dependencies and integration points
It depends on `mod_devicetable.h`, `device.h`, and `typec.h`. It integrates with DisplayPort, Thunderbolt, USB4 mode selection, Type-C muxes, cable plug SOP prime operations, and userspace-visible device binding.

## Risks and test signals
Risks are entering modes while not DFP, mixing partner and plug SVDM versions, missing async state updates, and dangling driver data after disconnect. Tests should bind/unbind a fake altmode driver, exercise enter/exit/attention/VDM callbacks, verify mode-selection timeout/reporting, and check plug altmode reference handling.
