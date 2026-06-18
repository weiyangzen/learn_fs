# sources/distributed-fs/ceph-client/include/linux/sfp.h

## Purpose

`sfp.h` defines SFP/SFP+ module EEPROM layouts, SFF-8024/SFF-8472 constants, diagnostics offsets, parsed module capabilities, and the bus API between an SFP socket driver and an upstream network device. It is a packed binary layout header plus a conditional API facade for `CONFIG_SFP`.

## Important APIs, Types, And Functions

Important binary layout types are `struct sfp_eeprom_base`, `struct sfp_eeprom_ext`, `struct sfp_eeprom_id`, and `struct sfp_diag`. They mirror module EEPROM fields, including transceiver compliance bits, connector, encoding, nominal bitrate, link lengths, vendor identity, wavelength or cable compliance, option bits, diagnostic monitor flags, enhanced options, SFF-8472 revision, alarm and warning thresholds, calibration coefficients, and live diagnostic values.

Constants cover SFF-8024 module IDs, encodings, connectors, extended compliance codes, base EEPROM offsets, option bits, diagnostic offsets, status bits, alarm/warn bits, extended status bits, and page selection. `struct sfp_module_caps` carries supported PHY interface bitmap, ethtool link-mode bitmap, possible PHY presence, and parsed port type. `struct sfp_upstream_ops` defines callbacks for upstream attach/detach, module insert/remove/start/stop, link up/down, and PHY connect/disconnect.

When `CONFIG_SFP` is enabled, APIs include `sfp_get_module_caps()`, `sfp_select_interface()`, `sfp_get_module_info()`, `sfp_get_module_eeprom()`, `sfp_get_module_eeprom_by_page()`, `sfp_upstream_start()`, `sfp_upstream_stop()`, `sfp_upstream_set_signal_rate()`, `sfp_bus_put()`, `sfp_bus_find_fwnode()`, `sfp_bus_add_upstream()`, `sfp_bus_del_upstream()`, and `sfp_get_name()`. Disabled stubs return neutral values or `-EOPNOTSUPP`.

## Control Flow

The typical flow is: an upstream network device locates an SFP bus by firmware node, adds itself with `sfp_bus_add_upstream()`, receives attach and module event callbacks, validates inserted module EEPROM through `module_insert()`, starts the module, selects a PHY interface using advertised link modes, handles link up/down, connects any module PHY, and tears down on removal or upstream unregister. EEPROM and diagnostic accessors serve ethtool requests.

## State And Persistence

This header stores no runtime state, but the packed structs define persistent EEPROM interpretation. The SFP bus object owns runtime state in implementation code. `sfp_module_caps` is parsed module state exposed through a const pointer. The endian-specific bitfields and `__packed` attributes are part of the persistent ABI with raw EEPROM bytes.

## Dependencies And Integration Points

Dependencies include PHY interface definitions, ethtool module EEPROM APIs, netlink extended acknowledgements, firmware nodes, and link-mode bitmaps. Integration points are SFP cage/socket drivers, MAC drivers, phylink, PHY devices on module I2C, ethtool EEPROM/dump commands, and network link management.

## Risks And Test Signals

Risks are broken packed layout, endian bitfield mistakes, invalid checksum or offset interpretation, treating `may_have_phy` as certainty, unsupported-module acceptance, and missing `CONFIG_SFP` behavior at call sites. Test signals include EEPROM fixture parsing for little and big endian builds, ethtool module-info and paged EEPROM reads, hot-insert/remove, PHY connect/disconnect, link-mode interface selection, high-power/rate-select options, and disabled-config builds verifying stub behavior.
