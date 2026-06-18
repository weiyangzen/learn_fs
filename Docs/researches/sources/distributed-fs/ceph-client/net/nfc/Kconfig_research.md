# sources/distributed-fs/ceph-client/net/nfc/Kconfig

## Purpose

This Kconfig file defines the top-level NFC subsystem options. It enables the core NFC module, the optional digital protocol stack, and includes NCI, HCI, and driver-specific NFC configuration trees.

## Important APIs, Types, and Functions

The options are `NFC` and `NFC_DIGITAL`. `NFC` is a tristate menu option depending on `RFKILL || !RFKILL` and builds the core module named `nfc`. `NFC_DIGITAL` depends on `NFC`, selects `CRC_CCITT` and `CRC_ITU_T`, and builds the `nfc_digital` module. The file sources `net/nfc/nci/Kconfig`, `net/nfc/hci/Kconfig`, and `drivers/nfc/Kconfig`.

## Control Flow

Kconfig selection controls which Makefile objects are built. Enabling `NFC` exposes the subsystem and lower-level protocol stacks. Enabling `NFC_DIGITAL` pulls CRC helpers needed by `digital_core.c`, `digital_dep.c`, and `digital_technology.c`.

## State and Persistence Behavior

There is no runtime state. Configuration state persists in the kernel build configuration and determines module availability and compile-time dependencies.

## Dependencies and Integration Points

This file integrates NFC core with RFKILL, the digital stack, NCI, HCI, and NFC device drivers. The selected CRC libraries are required by the digital stack's CRC-A, CRC-B, and CRC-F helpers.

## Risks and Edge Cases

Missing CRC selects would break the digital stack at link time. Driver Kconfig entries are sourced only through this menu, so disabling `NFC` hides downstream NFC drivers and protocol stacks.

## Test Signals

Build matrix coverage should include `CONFIG_NFC=m/y`, `CONFIG_NFC_DIGITAL=m/y`, RFKILL enabled and disabled, plus NCI/HCI driver combinations.
