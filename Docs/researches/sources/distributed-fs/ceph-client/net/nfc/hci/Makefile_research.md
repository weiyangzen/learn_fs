# sources/distributed-fs/ceph-client/net/nfc/hci/Makefile

## Purpose

This Makefile builds the NFC HCI layer module and conditionally includes the SHDLC link-layer object.

## Important APIs, Types, and Functions

`obj-$(CONFIG_NFC_HCI) += hci.o` creates the HCI module. `hci-y` includes `core.o`, `hcp.o`, `command.o`, `llc.o`, and `llc_nop.o`. `hci-$(CONFIG_NFC_SHDLC) += llc_shdlc.o` adds SHDLC support when configured.

## Control Flow

Kbuild links the listed objects into `hci.o` when HCI support is enabled. SHDLC is compiled into the same module only when `CONFIG_NFC_SHDLC` is selected.

## State and Persistence Behavior

The file has no runtime state. It defines module composition at build time.

## Dependencies and Integration Points

The object list combines HCI core, HCP frame handling, command handling, generic LLC support, a no-op LLC backend, and optional SHDLC. The resulting module plugs into the NFC core and HCI drivers.

## Risks and Edge Cases

Missing `llc_shdlc.o` with SHDLC-enabled drivers will cause unresolved behavior or symbols depending on driver linkage. Moving objects out of `hci.o` would require reevaluating module exports and initialization order.

## Test Signals

Build with `CONFIG_NFC_HCI=m` and `CONFIG_NFC_SHDLC=y`, inspect `hci.o` composition, and load HCI drivers that use both no-op LLC and SHDLC paths.
