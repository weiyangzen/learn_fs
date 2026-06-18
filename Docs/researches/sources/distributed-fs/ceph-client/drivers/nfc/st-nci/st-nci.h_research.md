# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/st-nci.h

## Purpose
`st-nci.h` is the shared header for ST_NCI core, NDLC, secure-element support, and vendor commands.

## Important APIs, types, and constants
- Defines runtime flags `ST_NCI_RUNNING` and `ST_NCI_FACTORY_MODE`.
- Defines proprietary core command IDs `ST_NCI_CORE_PROP` and `ST_NCI_SET_NFC_MODE`.
- `struct st_nci_se_status` carries platform-provided UICC/eSE presence.
- `struct st_nci_se_info` stores ATR, completions, timers, callback state, and SE activity flags.
- `enum nfc_vendor_cmds` enumerates ST vendor subcommands for factory mode, HCI device-management operations, firmware update, loopback, measurement, comparison, and manufacturer info.
- `struct st_nci_info` combines NDLC pointer, flags, and SE info.
- Prototypes expose core probe/remove, SE hooks, HCI callbacks, and vendor init.

## Control flow and integration
The header ties `core.c`, `se.c`, `vendor_cmds.c`, `ndlc.c`, and physical transports together. NCI ops in the core refer to SE and vendor functions declared here, while transports pass `st_nci_se_status` into NDLC/core probe.

## State and persistence
The header describes in-memory driver state. SE presence comes from firmware properties, while HCI session identity is created at runtime by `se.c`.

## Dependencies and risks
It includes `ndlc.h`, creating a mutual conceptual dependency between core and transport definitions. The vendor command enum is ABI-relevant for userspace vendor command callers; reordering would break subcommand expectations.

## Test signals
Compile all ST_NCI objects together and run vendor-command ABI tests that validate subcommand numbers, SE callback prototypes, and factory-mode flag behavior.
