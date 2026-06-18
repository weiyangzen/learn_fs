# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/psy.c

Purpose: Exposes each UCSI connector as a USB power_supply device reporting charge state, USB type, online state, voltage/current limits, instantaneous negotiated values, scope, and status.

Important APIs/types/functions: helper getters include `ucsi_psy_get_scope`, `ucsi_psy_get_status`, `ucsi_psy_get_online`, voltage/current getters, `ucsi_psy_get_usb_type`, and `ucsi_psy_get_charge_type`. Public functions are `ucsi_register_port_psy`, `ucsi_unregister_port_psy`, and `ucsi_port_psy_changed`.

Control flow and state: registration builds a name `ucsi-source-psy-<dev><connector>`, sets USB/PD/PPS supported types, and registers with `power_supply_register`. Properties are computed live from cached connector status bitmaps, `rdo`, `src_pdos`, `num_pdos`, and UCSI capability attributes.

Persistence behavior: no persistent storage. Values reflect cached UCSI connector state and are updated through `power_supply_changed` from core event paths.

Dependencies/integration points: compiled when `CONFIG_POWER_SUPPLY` is enabled. Uses USB PD PDO/RDO helpers, UCSI bitfield helpers, device `scope` property, and Type-C/UCSI power-role semantics.

Risks: PD voltage/current calculations only use fixed PDOs; PPS/APDO details are not deeply modeled despite advertising PD_PPS in usb types. If `src_pdos` are not available yet, PD values may be zero. UCSI cannot distinguish all BC charger types, so default-current fallbacks are approximate. Status depends on UCSI 2.0 sink-path status when available.

Test signals: power_supply sysfs values across disconnected, default USB, 1.5A, 3A, BC, and PD contracts; PDO refresh after `ucsi_get_src_pdos`; charge type in sink/source roles; scope override through firmware property; and unregister cleanup on driver removal.
