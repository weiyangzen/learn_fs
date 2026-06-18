# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x550.h

## Purpose
This header exposes the small public surface of the X550-specific ixgbe implementation to the rest of the driver. It intentionally hides the large internal operation-table and PHY/link helper set from `ixgbe_x550.c`.

## Important APIs and types
- Includes `ixgbe_type.h` for `struct ixgbe_hw`, `u32`, and common ixgbe type definitions.
- Declares exported model values: `ixgbe_mvals_x550em_a`.
- Declares firmware driver-version reporting: `ixgbe_set_fw_drv_ver_x550()`.
- Declares SR-IOV filtering controls: `ixgbe_set_source_address_pruning_x550()` and `ixgbe_set_ethertype_anti_spoofing_x550()`.
- Declares malicious-driver-detection controls: enable, disable, restore one VF, and collect malicious VF bitmap.

## Control flow and integration
Other ixgbe compilation units include this header when they need to call X550-specific helper functions without depending on the private implementation. The prototypes mirror functions exported from `ixgbe_x550.c` and are used by shared SR-IOV, mailbox, or PF management paths.

## State and persistence behavior
The header itself has no state. Its functions operate on `struct ixgbe_hw` and write hardware state: firmware-visible driver version, PF/VF spoofing registers, source address pruning bitmaps, MDD enablement, and queue block/restore state.

## Dependencies
It depends on `ixgbe_type.h` and compile-time agreement with the operation implementations in `ixgbe_x550.c`.

## Risks
Prototype drift would break cross-file calls or hide ABI changes inside the driver. The public functions mostly touch virtualization and firmware-facing hardware state, so callers must pass valid VF/pool indices and a properly initialized `struct ixgbe_hw`.

## Test signals
Build coverage with X550 support enabled is the main header test. Runtime validation comes from SR-IOV anti-spoofing/source-pruning tests, MDD interrupt handling, and firmware driver-version reporting.
