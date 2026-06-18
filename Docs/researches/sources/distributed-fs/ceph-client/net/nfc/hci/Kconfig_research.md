# sources/distributed-fs/ceph-client/net/nfc/hci/Kconfig

## Purpose

This Kconfig file defines the NFC HCI protocol implementation and optional SHDLC link layer support for HCI-based NFC drivers.

## Important APIs, Types, and Functions

`NFC_HCI` is a tristate option depending on `NFC` and builds the kernel NFC HCI implementation. `NFC_SHDLC` is a bool depending on `NFC_HCI`, selects `CRC_CCITT`, and enables the SHDLC link layer for HCI drivers that need it.

## Control Flow

Selecting `NFC_HCI` causes the HCI Makefile to build `hci.o`. Selecting `NFC_SHDLC` adds the SHDLC object to that module. The options are sourced from the top-level NFC Kconfig.

## State and Persistence Behavior

There is no runtime state in this file. Configuration persists in the kernel build and determines whether HCI and SHDLC code is compiled.

## Dependencies and Integration Points

HCI depends on the NFC core. SHDLC depends on HCI and CRC-CCITT. Device drivers such as PN544-style HCI frame processors rely on these symbols.

## Risks and Edge Cases

Drivers requiring SHDLC must select or depend on `NFC_SHDLC`; otherwise they can build without the needed link-layer implementation. Since `NFC_SHDLC` is bool, module/builtin combinations should be checked when HCI is modular.

## Test Signals

Build `CONFIG_NFC_HCI=m/y` with and without `CONFIG_NFC_SHDLC`, and build HCI drivers that require SHDLC to confirm dependency coverage.
