# sources/distributed-fs/ceph-client/include/linux/usb/typec_mux.h

## Purpose
This header defines Type-C orientation switches and mode muxes. It abstracts devices that flip connector orientation or route pins between USB, accessory, USB4, and alternate-mode states.

## Important APIs, types, and functions
Important types are `typec_switch_desc`, `typec_switch_set_fn_t`, `typec_mux_state`, `typec_mux_desc`, and `typec_mux_set_fn_t`. APIs include fwnode and device lookup helpers, `typec_switch_set()`, `typec_switch_register()`, `typec_mux_set()`, `typec_mux_register()`, drvdata accessors, and unregister/put helpers. Disabled `CONFIG_TYPEC` stubs return success for no-op sets and `-EOPNOTSUPP` for registration.

## Control flow, state, and persistence
Provider drivers register switch or mux devices with firmware-node identity and set callbacks. Type-C policy obtains handles from the connector fwnode, sends orientation or mode state updates, and releases references on disconnect or teardown. Mux state carries the active altmode pointer, numeric mode, and mode-specific data. State is hardware runtime state only.

## Dependencies and integration points
It depends on firmware property APIs, error pointers, and Type-C core types. It integrates with board firmware descriptions, retimers, PHYs, DP/TBT/USB4 altmode drivers, and controller drivers that need routing updates.

## Risks and test signals
Risks include missing fwnode links, ignoring error-pointer drvdata stubs, stale altmode pointers in mux state, and ordering orientation before mode changes incorrectly. Tests should cover provider registration, consumer lookup, orientation flips, mode transitions, disabled-config stubs, and cleanup on disconnect.
