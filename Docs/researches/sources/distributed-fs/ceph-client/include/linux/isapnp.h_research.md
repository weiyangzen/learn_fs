# sources/distributed-fs/ceph-client/include/linux/isapnp.h

## Purpose
`isapnp.h` defines ISA Plug and Play ID encoding macros, card/device ID table structures, low-level configuration accessors, procfs hooks, and compatibility lookup helpers.

## Important APIs, types, and functions
Key macros include `ISAPNP_VENDOR`, `ISAPNP_DEVICE`, `ISAPNP_FUNCTION`, card/device ID initializers, and single-device initializers. `struct isapnp_card_id` describes card and logical devices. APIs include `isapnp_present`, `isapnp_cfg_begin`, `isapnp_cfg_end`, byte read/write, proc init/done, and `pnp_find_dev`, with stubs when ISAPNP is disabled.

## Control flow
Drivers or PnP core encode vendor/device IDs, detect ISA PnP presence, enter configuration mode for a card select number and logical device, read/write config registers, and optionally expose procfs data.

## State and persistence
State is ISA PnP hardware configuration and PnP core device/card objects. Header stubs hold no state.

## Dependencies and integration points
It depends on PnP core and mod_devicetable definitions, and integrates legacy ISA PnP devices with Linux driver matching.

## Risks and test signals
Risks include ID byte-order mistakes, disabled-config fallbacks, config-mode sequencing errors, and procfs coverage. Tests should cover ID macro values, probing with/without ISAPNP, logical device lookup, config read/write, and module ID table matching.
