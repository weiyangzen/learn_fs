# sources/distributed-fs/ceph-client/drivers/parport/multiface.h

## Purpose
`multiface.h` provides address constants for Amiga SerialMaster and Multiface II/III expansion-card register blocks. In this subset it is used by `parport_mfc3.c` to locate the PIA parallel-port block relative to a Zorro card base.

## Important APIs, Types, and Functions
The header defines `PIA_REG_PADWIDTH`, `DUARTBASE`, `PITBASE`, `ROMBASE`, and `PIABASE`. It has only include guards and no functions or types.

## Control Flow
There is no runtime control flow. Consumers include the header and add offsets such as `PIABASE` to bus resources.

## State and Persistence
The constants encode hardware layout. No mutable or persistent state exists.

## Dependencies and Integration Points
`parport_mfc3.c` uses `PIABASE` to request and map the MC6821 PIA registers for the Multiface III parallel port. Other card functions may use the remaining offsets.

## Risks
Incorrect offsets would make low-level drivers touch the wrong card registers. `PIA_REG_PADWIDTH` is a hardware access-spacing constant and must stay aligned with MC6821/Zorro register layout expectations.

## Test Signals
Compile-time inclusion should succeed, and MFC3 probing should request memory at `zorro_resource.start + PIABASE`. Hardware tests should confirm PIA register access at that offset.
