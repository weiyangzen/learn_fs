# sources/distributed-fs/ceph-client/drivers/crypto/ccp/dbc.h

## Purpose

`dbc.h` defines the private Dynamic Boost Control device state shared between the DBC implementation and PSP initialization code.

## Important APIs, Types, And Functions

`struct psp_dbc_device` records the owning `device`, `psp_device`, a page-sized `union dbc_buffer`, ioctl mutex, misc device, and transport abstraction pointers. `union dbc_buffer` overlays a `struct psp_request` for platform access with `struct psp_ext_request` for extended mailbox. It declares `dbc_dev_init()` and `dbc_dev_destroy()`.

## Control Flow

The header has no executable control flow. Its fields let `dbc.c` use one ioctl path while switching between platform-access and extended-mailbox command layouts during initialization.

## State And Persistence Behavior

The structure persists as `psp->dbc_data` until PSP teardown. Its payload and result pointers point into the selected union member and must remain consistent with `use_ext`.

## Dependencies And Integration Points

It includes DBC UAPI definitions, misc-device support, platform-access request definitions, and `psp-dev.h`. It is private to the CCP/PSP driver tree.

## Risks And Test Signals

Risks are layout and aliasing mistakes between the two mailbox formats. Compile coverage with both platform-access and extended DBC capability paths, plus ioctl tests that confirm payload size and status fields are written to the expected header.
