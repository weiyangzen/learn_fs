# sources/distributed-fs/ceph-client/drivers/comedi/drivers/das08_isa.c

## Purpose

This file is the ISA/PC-104 bus wrapper and board table for many DAS08-family boards. It does not implement I/O behavior directly; it validates and claims the configured I/O port range, allocates common private state, and delegates to `das08_common_attach()`.

## Important APIs, Types, and Functions

`das08_isa_boards[]` describes classic DAS08, PGM/PGH/PGL, AOH/AOL/AOM, JR-AO, JR-16-AO, PC104-DAS08, and DAS08JR/16 variants. Key fields include AI resolution, programmable gain type, AI encoding, AO resolution, digital channel counts, 8255/8254 offsets, JR flag, and I/O size. `das08_isa_attach()` uses `comedi_alloc_devpriv()` and `comedi_check_request_region()`, then calls `das08_common_attach()`. `das08_isa_driver` exposes a legacy Comedi attach interface and board-name table.

## Control Flow, State, and Persistence

The user supplies the base I/O address in option 0. Attach allocates `struct das08_private_struct`, requests the board's port window within ISA limits, and initializes the common subdevices. `comedi_legacy_detach()` releases resources. Board identity is selected by the Comedi board-name mechanism rather than hardware autoprobe.

## Dependencies and Integration Points

Dependencies are Comedi legacy ISA helpers and `das08.h`. Integration points are Comedi's `module_comedi_driver()` registration, user-space `comedi_config`, and the common DAS08 module. Optional 8255/8254 offsets in the table activate shared Comedi helper subdevices.

## Risks and Test Signals

Risks include stale or unchecked `.iosize` values, board-name descriptors not matching physical jumpers, unsupported base address windows, and wrong JR/non-JR register behavior. Test each named board by attach at configured base, verify expected subdevices, check AI encoding and ranges, verify AO where present, and exercise 8254/8255 subdevices for entries with offsets.
