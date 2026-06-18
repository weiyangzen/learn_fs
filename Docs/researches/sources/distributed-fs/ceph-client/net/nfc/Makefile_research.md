# sources/distributed-fs/ceph-client/net/nfc/Makefile

## Purpose

This Makefile maps NFC Kconfig symbols to built objects and module composition. It builds the NFC core module, optional NCI and HCI subdirectories, and the digital protocol stack module.

## Important APIs, Types, and Functions

`obj-$(CONFIG_NFC) += nfc.o` builds the core NFC module. `nfc-objs` includes `core.o`, `netlink.o`, `af_nfc.o`, `rawsock.o`, and LLCP implementation files. `obj-$(CONFIG_NFC_DIGITAL) += nfc_digital.o` builds `digital_core.o`, `digital_technology.o`, and `digital_dep.o`. `obj-$(CONFIG_NFC_NCI)` and `obj-$(CONFIG_NFC_HCI)` descend into subdirectories.

## Control Flow

The build system links object lists into modules based on configuration. Core NFC initialization in `core.c` expects raw socket, LLCP, netlink, and PF_NFC pieces to be present in the same `nfc` module.

## State and Persistence Behavior

There is no runtime state. Build state is the selected module composition.

## Dependencies and Integration Points

The object grouping ties `af_nfc.c` socket family registration, `core.c` device lifecycle, NFC generic netlink, raw sockets, and LLCP into one module. The digital module depends on exported NFC core APIs and CRC helpers selected by Kconfig.

## Risks and Edge Cases

Moving objects between modules would require checking exported symbols and initialization order. Omitting `af_nfc.o`, `rawsock.o`, or LLCP files from `nfc-objs` would break public PF_NFC socket functionality or LLCP support.

## Test Signals

Build `CONFIG_NFC=m`, verify `nfc.ko` contains core, netlink, PF_NFC, raw socket, and LLCP symbols, and build `CONFIG_NFC_DIGITAL=m` to verify `nfc_digital.ko` links against exported NFC core APIs.
