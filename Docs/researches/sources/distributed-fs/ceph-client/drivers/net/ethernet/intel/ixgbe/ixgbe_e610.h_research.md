# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_e610.h

## Purpose

`ixgbe_e610.h` is the internal public header for E610-specific ixgbe support. It exposes the E610 Admin Command Interface, capability discovery, link/PHY/flow-control management, NVM/flash access, reset, and firmware log hooks implemented in `ixgbe_e610.c` to the rest of the ixgbe driver. It includes `ixgbe_type.h`, so its declarations are built around `struct ixgbe_hw`, ACI descriptors, E610 link/PHY/NVM data structures, and ixgbe enums.

## Important APIs and exported contract

The header declares ACI transport functions, event pending/get helpers, descriptor initialization, resource ownership helpers, capability enumeration, PHY caps/config, link restart/status/event-mask functions, LED identification, media type, setup/check link, link capabilities, PHY flow control, RX disable, PHY ops init/identify/module/setup/power/LPLU, EEPROM params, netlist node lookup, NVM ownership, read/update/erase/activate/checksum, inactive image version readers, Shadow RAM and flat NVM reads, E610 EEPROM reads/checksum, reset, flash metadata discovery, PLDM-like package/component-table commands, and firmware logging.

These declarations mirror ixgbe operation-table slots and direct helper users. `ixgbe_check_link_e610()` and `ixgbe_get_link_capabilities_e610()` can be used through `hw->mac.ops`; `ixgbe_read_ee_aci_e610()` and `ixgbe_validate_eeprom_checksum_e610()` through `hw->eeprom.ops`; `ixgbe_aci_set_port_id_led()` through the E610 ethtool physical-ID path.

## Control flow represented by the header

The header describes a layered control-plane contract. Generic ixgbe code can send raw ACI commands, then build discovery, link, PHY, and NVM flows on top. Link callers can use direct ACI helpers or MAC/PHY operation callbacks that land in E610 functions. NVM callers must follow ownership, chunking, last-command, and activation sequencing unless a helper wraps those steps.

Initialization order is implied: ACI support comes first; firmware/capability/flash discovery is probe/start state; PHY/link setup depends on parsed PHY capabilities; EEPROM operations depend on initialized EEPROM params; fwlog initialization depends on adapter/debugfs state and E610 MAC type.

## State and persistence behavior

The header owns no storage, but its API mutates hardware and driver state. Declared functions can alter firmware/device settings such as PHY config, link restart, event masks, LEDs, RX enable state, NVM contents, NVM activation, EMPR, and low-power PHY behavior. They also populate cached driver state in `hw->link`, `hw->phy`, `hw->fc`, `hw->flash`, `hw->eeprom`, and capability structures.

## Dependencies and integration points

Consumers include E610 implementation users in ethtool support, generic ixgbe initialization, NVM update code, and fwlog paths. The header depends on type definitions in `ixgbe_type.h`: `struct libie_aq_desc`, `struct ixgbe_aci_event`, ACI command payloads, resource enums, link/media/flow-control enums, and flash version structures. Since this is a private driver header, compatibility is internal to ixgbe, but prototype drift can break operation-table and ethtool callers.

## Risks and maintenance notes

The header exposes low-level NVM write/erase/update primitives without encoding required sequencing in types. Several functions accept raw buffers and lengths, so callers must validate sizing carefully. Link/PHY helpers mix cached state updates with hardware commands, so callers should not assume they are read-only. E610-specific behavior appears through both generic ixgbe naming and `_e610` names, requiring MAC-type or operation-table guards.

## Test signals

Build coverage is the direct signal: prototypes must match definitions and callers without compiler or sparse warnings. Runtime signals come through users of the declared APIs: E610 probe/start, ethtool E610 helpers, EEPROM/NVM reads, link setup, LED identification, and fwlog initialization. Negative coverage should include pointer type mismatches, missing declarations, raw-buffer misuse, and endian-annotated structure handling.
