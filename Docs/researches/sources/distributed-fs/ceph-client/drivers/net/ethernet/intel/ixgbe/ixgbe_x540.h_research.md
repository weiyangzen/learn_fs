# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x540.h

## Purpose
`ixgbe_x540.h` declares the X540 generation-specific entry points exported by `ixgbe_x540.c` to the rest of the ixgbe driver. It is the small public interface for X540 invariants, reset/start/link setup, media reporting, LED blink control, SW/FW synchronization, and EEPROM parameter initialization.

## Important APIs, Types, and Functions
- `ixgbe_get_invariants_X540(struct ixgbe_hw *hw)` fills X540 MAC/PHY invariant limits and callback defaults.
- `ixgbe_setup_mac_link_X540(struct ixgbe_hw *hw, ixgbe_link_speed speed, bool autoneg_wait_to_complete)` delegates MAC link setup to PHY link-speed setup.
- `ixgbe_reset_hw_X540(struct ixgbe_hw *hw)` performs X540 reset and post-reset address/filter initialization.
- `ixgbe_start_hw_X540(struct ixgbe_hw *hw)` runs generic hardware start plus generation-2 start logic.
- `ixgbe_get_media_type_X540(struct ixgbe_hw *hw)` reports copper media.
- `ixgbe_blink_led_start_X540` and `ixgbe_blink_led_stop_X540` expose X540 LED identification behavior.
- `ixgbe_acquire_swfw_sync_X540`, `ixgbe_release_swfw_sync_X540`, and `ixgbe_init_swfw_sync_X540` expose X540 semaphore management for shared NVM/PHY/I2C/management resources.
- `ixgbe_init_eeprom_params_X540(struct ixgbe_hw *hw)` initializes flash-backed EEPROM metadata.

## Control Flow
The header itself has only include-guard and declaration flow. Consumers include it when installing X540 callbacks into operation tables or reusing X540 helper behavior from neighboring generation files. At runtime, calls enter the implementations in `ixgbe_x540.c` through direct references or through `struct ixgbe_mac_operations` and `struct ixgbe_eeprom_operations`.

## State and Persistence Behavior
The header owns no state. Declared functions mutate `struct ixgbe_hw`, hardware MMIO registers, EEPROM/shadow RAM/flash state, LED control, and SW/FW semaphore registers in their implementation. The included `ixgbe_type.h` supplies the `struct ixgbe_hw` definition and related enums used by every prototype.

## Dependencies and Integration Points
The header includes `ixgbe_type.h`, so any file including `ixgbe_x540.h` receives the full ixgbe hardware type model and E610 supplemental types. It is included by `ixgbe_x540.c`, X550 implementation code, and E610 code that shares selected X540 reset or synchronization behavior. It connects generation-specific implementation to common probe, reset, EEPROM, LED, and link-management paths.

## Risks and Edge Cases
- `ixgbe_setup_mac_link_X540` is declared twice in the header. The duplicate prototype is harmless in C but is maintenance noise and can hide prototype drift if one copy is edited and the other is not.
- Because the header exposes synchronization and reset functions used by other generation code, signature or semantic changes can affect X550/E610 callers as well as X540.
- Including `ixgbe_type.h` makes this header broad; changes to shared types can force recompilation or expose E610 dependencies to every X540 consumer.

## Test Signals
- Compile tests should catch prototype drift between this header and `ixgbe_x540.c`.
- Include-order tests should verify consumers can include this header without missing `bool`, `u32`, `ixgbe_link_speed`, or `struct ixgbe_hw` definitions.
- Static checks should flag the duplicate `ixgbe_setup_mac_link_X540` declaration if the project enforces duplicate-prototype warnings.
