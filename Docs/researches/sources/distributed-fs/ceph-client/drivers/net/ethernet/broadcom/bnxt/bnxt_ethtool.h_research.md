# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ethtool.h

## Purpose

`bnxt_ethtool.h` is the shared declaration header for the BNXT ethtool implementation. It exposes the driver's `struct ethtool_ops`, public helper functions used by other BNXT modules, LED request layout helpers, firmware reset bit masks, register dump length, and flow-rule protocol constants.

## Important APIs, types, and macros

- `struct bnxt_led_cfg` mirrors the packed LED fields embedded in `struct hwrm_port_led_cfg_input`; `bnxt_set_phys_id()` casts the firmware request LED field area to this structure.
- `BNXT_LED_DFLT_ENA`, `BNXT_LED_DFLT_ENA_SHIFT`, and `BNXT_LED_DFLT_ENABLES(x)` build the per-LED `enables` bitmask for HWRM LED configuration.
- `BNXT_FW_RESET_AP` and `BNXT_FW_RESET_CHIP` define ethtool reset bitmasks shifted into `ETH_RESET_SHARED_SHIFT`.
- `BNXT_PXP_REG_LEN` defines the base PCIe/register dump region length before optional PCIe stats.
- `BNXT_IP_PROTO_FULL_MASK` and `BNXT_IP_PROTO_WILDCARD` define ethtool ntuple protocol-mask conventions used for IP_USER/IPV6_USER flow validation.
- Public exports include RSS indirection size, link-speed conversion helpers, NVM get/find/read/write helpers, firmware reset, firmware package flashing from an already-loaded firmware object, package info extraction, and ethtool init/free.

## Control flow role

The header itself has no executable control flow, but it forms the interface between `bnxt_ethtool.c` and the rest of the driver. Link-speed conversion helpers are reused outside ethtool for translating firmware speeds. NVM helpers are callable by other modules that need package or directory access without duplicating HWRM details. `bnxt_ethtool_init()` and `bnxt_ethtool_free()` are lifecycle hooks called from device setup/teardown.

## State and persistence behavior

No state is stored in this header. Its declarations operate on `struct bnxt`, `struct net_device`, firmware responses, and NVM data buffers owned by callers. The reset and NVM helpers declared here can trigger persistent firmware/NVM changes when implemented in `bnxt_ethtool.c`.

## Dependencies and integration points

- Requires BNXT core types such as `struct bnxt`, `struct net_device`, HWRM NVM response types, and kernel `struct firmware`.
- Includes firmware constants from HWRM headers indirectly through users.
- Integrated by BNXT core initialization for `bnxt_ethtool_ops` registration and by modules that need link/NVM helpers.

## Risks and edge cases

- The file declares `bnxt_find_nvram_item()` twice with identical signatures. This is harmless in C but is a maintenance smell and can hide future prototype drift.
- `struct bnxt_led_cfg` relies on matching the firmware request field layout exactly; packing or field-size changes in HWRM structures would break the cast in `bnxt_set_phys_id()`.
- Reset masks must remain aligned with Linux ethtool reset semantics and the driver's implementation in `bnxt_reset()`.

## Test signals

- Compile coverage for all translation units including this header.
- Ettool LED identification, reset, link-speed conversion, and NVM helper users should build without prototype mismatch.
- Static checks should flag duplicate declarations or endian field misuse if signatures change.
