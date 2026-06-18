# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_nvm.h

## Purpose

`igc_nvm.h` declares the NVM helper interface implemented by `igc_nvm.c`. It exposes EEPROM read, MAC address read, checksum validate, and checksum update helpers to the igc hardware setup code.

## Important APIs, Types, and Functions

The header declares `igc_read_mac_addr`, `igc_read_nvm_eerd`, `igc_validate_nvm_checksum`, and `igc_update_nvm_checksum`. All operate on `struct igc_hw`; `igc_read_nvm_eerd` also accepts a word offset/count and output buffer. The prototypes use igc/kernel integer types such as `s32` and `u16`.

## Control Flow

There is no executable control flow. The file is protected by `_IGC_NVM_H_` include guards and makes the NVM routines available for direct calls or operation-table assignment.

## State and Persistence Behavior

The header owns no state. Persistence behavior belongs to the implementation and the NVM operation callbacks wired elsewhere.

## Dependencies and Integration Points

It is included by `igc_nvm.c` and hardware modules that need NVM helper prototypes. It intentionally keeps register details out of the header.

## Risks and Edge Cases

Include ordering must provide `struct igc_hw`, `s32`, and `u16`. Signature changes must stay synchronized with NVM/MAC operation tables and call sites.

## Test Signals

Compile coverage is the main signal. Runtime behavior is covered through `igc_nvm.c` probe-time NVM validation and MAC-read paths.
