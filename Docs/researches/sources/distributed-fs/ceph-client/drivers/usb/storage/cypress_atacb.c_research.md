# sources/distributed-fs/ceph-client/drivers/usb/storage/cypress_atacb.c

## Purpose

`cypress_atacb.c` adds SAT-style ATA pass-through support for Cypress USB/ATA bridges that implement the vendor-specific ATACB protocol. Devices without usable ATACB fall back to normal transparent SCSI.

## Important APIs, Types, and Functions

The driver builds USB ID and unusual-device tables from `unusual_cypress.h`. `cypress_atacb_passthrough()` is the protocol handler: it intercepts SCSI `ATA_12` and `ATA_16`, validates supported ATA pass-through fields, rewrites the CDB to Cypress ATACB command `0x24`, forwards through `usb_stor_transparent_scsi_command()`, and optionally constructs ATA return descriptor sense data when CK_COND is requested. `cypress_probe()` selects either the ATACB protocol handler or transparent SCSI based on descriptor string-index heuristics for CY7C68300 A-revision devices.

## Control Flow

Probe initializes usb-storage state with the Cypress unusual-device entry. If the bridge is not the filtered A-revision descriptor layout, the transport protocol name and handler are changed to `Transparent SCSI with Cypress ATACB`; otherwise standard transparent SCSI is used. Runtime non-ATA commands pass through unchanged. ATA pass-through commands are saved, replaced with ATACB layout, executed, and then restored before return. Unsupported protocols, LBA48 high bytes, multiple count, and SET FEATURES transfer-mode commands return invalid-CDB sense.

## State and Persistence Behavior

The driver has no private persistent state beyond the selected `us->proto_handler` and protocol name. It temporarily rewrites `srb->cmnd` and `cmd_len`, preserving the original command in a stack buffer before restoring it.

## Dependencies and Integration Points

It depends on usb-storage core, SCSI error-handling command save/restore helpers, Linux ATA command constants, transparent SCSI transport, and Cypress unusual-device tables. It integrates ATA tools such as SMART/hdparm with selected USB/ATA bridges by translating SCSI ATA PASS THROUGH into the bridge vendor protocol.

## Risks and Test Signals

Risks include incomplete LBA48 support, hard-coded ATACB vendor signature defaults, descriptor-index filtering that may misclassify firmware revisions, temporary mutation of the SCSI CDB, and approximate ATA-to-SCSI sense mapping. Test signals include ATA_12 and ATA_16 pass-through, invalid field cases returning invalid CDB, CK_COND producing descriptor-format sense with ATA registers, fallback behavior for filtered revisions, and normal transparent SCSI for non-ATA commands.
