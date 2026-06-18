# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/version.h

## Purpose

`version.h` centralizes the user-visible driver name/description and the firmware major/minor/micro version constants expected by the Chelsio T3 `cxgb3` driver. It is small, but it participates in module identity and firmware compatibility checks.

## Important APIs and Constants

- `DRV_DESC` is `"Chelsio T3 Network Driver"`.
- `DRV_NAME` is `"cxgb3"`.
- `FW_VERSION_MAJOR`, `FW_VERSION_MINOR`, and `FW_VERSION_MICRO` are `7`, `12`, and `0`.

## Control Flow and Usage

The header has no control flow. Consumers include module/driver registration code for naming and `t3_hw.c` firmware checks. `t3_check_fw_version()` compares the flash firmware type/major/minor against these constants and warns or rejects when the running firmware is too old or incompatible.

## State and Persistence Behavior

The constants are compile-time state. They do not change at runtime and do not persist independently, but they define what persistent firmware image the compiled driver considers compatible. `FW_VERSION_MICRO` is declared but the checked path in `t3_hw.c` primarily enforces major/minor semantics.

## Dependencies and Integration Points

`version.h` is part of the `cxgb3` driver source set and integrates with hardware initialization, firmware loading/version reporting, and module metadata. It must remain in sync with supported firmware images and with `firmware_exports.h` protocol expectations.

## Risks and Edge Cases

- Bumping firmware constants without matching firmware/protocol support can accept unsupported images or reject working cards.
- A too-strict check would block newer compatible firmware, while a too-loose check can allow missing firmware features.
- Driver name changes affect module aliases, logs, tooling, and user expectations.

## Test Signals

Signals include module metadata showing the expected name/description, `t3_check_fw_version()` accepting firmware 7.12.x-compatible images, warnings for newer compatible minor versions, rejection of older/incompatible firmware, and firmware upgrade tests that confirm the constants match shipped images.
