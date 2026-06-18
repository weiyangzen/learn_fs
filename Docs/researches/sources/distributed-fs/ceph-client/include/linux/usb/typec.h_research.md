# sources/distributed-fs/ceph-client/include/linux/usb/typec.h

## Purpose
This header is the main USB Type-C class interface. It models ports, partners, cables, plugs, alternate modes, power/data/VCONN roles, orientation, USB modes, PD identity, and firmware-derived Type-C capabilities for port controller and connector-aware drivers.

## Important APIs, types, and functions
Important enums include `typec_port_type`, `typec_port_data`, `typec_role`, `typec_data_role`, `typec_pwr_opmode`, `typec_orientation`, `usb_mode`, and `usb_pd_svdm_ver`. Core types are `usb_pd_identity`, `typec_altmode_desc`, `typec_cable_desc`, `typec_partner_desc`, `typec_operations`, `typec_capability`, and `typec_connector`. APIs register/unregister ports, partners, cables, plugs, and alternate modes, update roles/orientation/mode, parse firmware capabilities, attach PD objects, and expose connector attach/deattach callbacks.

## Control flow, state, and persistence
Port drivers describe static capabilities, register a `typec_port`, then report cable/partner/plug discovery and live role changes through setter APIs. The Type-C core owns device-model objects and sysfs-visible state; callbacks in `typec_operations` route user or policy requests back to hardware drivers. Persistent state is limited to firmware/device-tree properties read through `typec_get_fw_cap()`; attachment, role, and altmode state is runtime only.

## Dependencies and integration points
It depends on Linux core types, the Type-C bus, firmware nodes, USB Power Delivery descriptors, and the device model. Integration points include TCPM/UCSI/EC port drivers, alternate-mode drivers, mux/switch/retimer users, USB/DisplayPort/Thunderbolt consumers, and sysfs userspace policy.

## Risks and test signals
Risks include stale partner/cable lifetimes, role/orientation updates racing with disconnect, wrong SVDM/PD revision propagation, and mismatched firmware capability parsing. Tests should cover port registration cleanup, role swap callbacks, altmode enumeration, active cable identity, Enter_USB mode changes, sysfs state, and disabled or missing callback behavior.
