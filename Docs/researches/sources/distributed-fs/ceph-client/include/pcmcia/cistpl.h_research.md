# sources/distributed-fs/ceph-client/include/pcmcia/cistpl.h

## Purpose

`cistpl.h` defines PCMCIA/CardBus CIS tuple codes and parsed tuple data structures. It is the schema used by CIS parsers and drivers to interpret card memory/device geometry, identity, function type, function extensions, configuration tables, power/timing/IO/memory windows, and tuple iteration.

## Important APIs, types, and functions

The header defines tuple code constants `CISTPL_*`, `cisdata_t`, and parsed tuple structures including `cistpl_longlink_t`, `cistpl_checksum_t`, `cistpl_longlink_mfc_t`, `cistpl_altstr_t`, `cistpl_device_t`, `cistpl_vers_1_t`, `cistpl_jedec_t`, `cistpl_manfid_t`, `cistpl_funcid_t`, `cistpl_funce_t`, serial/modem extension types, LAN extension types, IDE extension types, `cistpl_bar_t`, `cistpl_config_t`, `cistpl_power_t`, `cistpl_timing_t`, `cistpl_io_t`, `cistpl_irq_t`, `cistpl_mem_t`, `cistpl_cftable_entry_t`, `cistpl_cftable_entry_cb_t`, `cistpl_device_geo_t`, `cistpl_vers_2_t`, `cistpl_org_t`, `cistpl_format_t`, `union cisparse_t`, and `tuple_t`.

## Control flow

CIS traversal code fills `tuple_t` from raw tuple storage, follows long links/multifunction links, then parses tuple payloads into `cisparse_t` members according to `TupleCode`. Drivers consume parsed manufacturer/function/configuration/facility data to pick resources, power settings, IO windows, IRQs, and quirks.

## State and persistence behavior

The header owns no runtime state. Parsed structures are transient parser outputs, while raw CIS content persists on the card. `tuple_t` fields such as link offset, CIS offset, tuple offset, and data length are parser iteration state.

## Dependencies and integration points

It is standalone aside from primitive typedef assumptions and integrates with PCMCIA CIS parsers, socket/card services, driver match logic, resource allocation, and fake CIS overrides.

## Risks and test signals

Risks include trusting tuple lengths into fixed arrays, confusing CardBus and 16-bit PCMCIA cftable forms, incorrect scaling for power/timing values, too many IO/memory windows, and malformed long-link loops. Tests should parse representative modem, LAN, IDE, memory, multifunction, and CardBus CIS images; fuzz tuple lengths; validate bounds against max arrays; and verify resource selection from cftable entries.
