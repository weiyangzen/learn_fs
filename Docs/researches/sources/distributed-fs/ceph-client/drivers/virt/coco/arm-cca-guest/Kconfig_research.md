# sources/distributed-fs/ceph-client/drivers/virt/coco/arm-cca-guest/Kconfig

## Purpose
Declares Arm CCA guest attestation support.

## APIs, Types, and Functions
`ARM_CCA_GUEST` is a tristate depending on `ARM64` and selecting `TSM_REPORTS`.

## Control Flow and State
Build-time only. Enables `arm-cca-guest.o` as module or built-in and makes the shared configfs report frontend available.

## Dependencies and Integration
Runtime code depends on Arm RSI support and TSM report registration.

## Risks and Test Signals
The help text has a minor grammar issue but the functional risk is ensuring this symbol is not enabled on non-Realm systems; the module itself returns `-ENODEV` when not in Realm world. Build-test arm64 with `CONFIG_TSM_REPORTS`.
