# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_cypress.h

## Purpose

`unusual_cypress.h` lists Cypress-based devices that need the Cypress ATACB protocol path rather than fully generic usb-storage handling.

## Important APIs, Types, and Functions

The file contributes three `UNUSUAL_DEV()` entries using Cypress-related subclasses/transports, including entries that route to `USB_PR_CYP_ATACB` behavior in the broader usb-storage stack. The macro arguments provide device ID ranges, short inquiry strings, protocol override, transport override, optional initializer, and flags.

## Control Flow

The file is consumed through macro expansion by usb-storage tables. Generic usb-storage ignore logic uses the rows to avoid claiming devices intended for the Cypress subdriver, while the specialized path uses them to select the nonstandard command wrapper.

## State and Persistence Behavior

There is no runtime state in the header. It only controls probe-time matching. Device state is managed by the Cypress transport implementation and the SCSI/media layers.

## Dependencies and Integration Points

It depends on `UNUSUAL_DEV` being defined by the includer and on Cypress protocol constants and initializer symbols being available where used. It integrates with `usual-tables.c`, usb-storage device ID matching, and any Cypress-specific transport module.

## Risks and Edge Cases

The table is compatibility-sensitive: incorrect bcd ranges can either miss devices that need the Cypress path or force the path on compatible generic devices. Since these entries are small, stale firmware knowledge is the main maintenance risk.

## Test Signals

Compile the Cypress transport configuration, inspect generated USB modalias tables, attach each represented bridge revision, and validate command execution and media enumeration through the specialized protocol.
