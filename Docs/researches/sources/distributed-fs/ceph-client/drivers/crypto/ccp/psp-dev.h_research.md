# sources/distributed-fs/ceph-client/drivers/crypto/ccp/psp-dev.h

## Purpose

`psp-dev.h` defines the private PSP core structures, capability bit layout, mailbox command IDs, extended mailbox request format, and PSP core function prototypes.

## Important APIs, Types, And Functions

Key types are `union psp_cap_register`, `struct psp_device`, `enum psp_cmd`, `struct psp_ext_req_buffer_hdr`, `struct psp_ext_request`, and `enum psp_sub_cmd`. It declares master lookup, mailbox functions, and SEV IRQ handler registration helpers. `psp_device` holds MMIO base, mailbox mutex, subdevice pointers, interrupt callback, and capability state.

## Control Flow

The header has no executable flow, but its definitions shape all PSP subdevice command paths: standard mailbox commands use `enum psp_cmd`, while DBC/SFS use extended subcommands and `struct psp_ext_request`.

## State And Persistence Behavior

The `psp_device` object persists for the life of an SP device. Its subdevice pointers are nullable feature state and must be cleared during teardown.

## Dependencies And Integration Points

It depends on Linux PSP/platform-access headers and `sp-dev.h`. It is included across PSP subdrivers and the PCI glue.

## Risks And Test Signals

Risks include bitfield layout assumptions for the hardware capability register and packed request layout drift from firmware. Build and runtime tests across PSP generations, with feature bits decoded in sysfs and subdevices initialized conditionally, validate it.
