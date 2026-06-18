<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/adb_iop.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/adb_iop.h

## Purpose
This header describes the Apple Desktop Bus protocol messages exchanged with a Macintosh IOP channel. It supplies command, status, and message layout definitions for ADB-over-IOP drivers.

## Important APIs, Types, And Functions
- `ADB_IOP` and `ADB_CHAN` select the ISM IOP and channel 2.
- Command bits include `ADB_IOP_LISTEN`, `TALK`, `EXISTS`, `FLUSH`, `RESET`, `INT`, `POLL`, and `UNINT`.
- ADB immediate function codes include `AIF_RESET`, `AIF_FLUSH`, `AIF_LISTEN`, and `AIF_TALK`.
- `struct adb_iopmsg` defines flags, byte count, command byte, eight bytes of ADB payload, and spare padding.

## Control Flow
There is no executable control flow. IOP ADB code fills `struct adb_iopmsg`, sends it to the selected channel, then interprets returned flags such as explicit command completion, autopoll, SRQ, and timeout.

## State And Persistence Behavior
Message state is transient and owned by the caller/IOP transport. Persistent ADB state, such as autopoll enablement or device existence, is maintained by the IOP and ADB stack.

## Dependencies And Integration Points
The file depends on IOP numbering definitions such as `IOP_NUM_ISM` and on fixed-width kernel integer types. It integrates with Macintosh ADB input and IOP transport code.

## Risks And Edge Cases
The packed protocol is implicit rather than marked packed; layout assumptions depend on byte fields and natural alignment. Payload length must not exceed `data[8]`, and timeout/autopoll flags must be interpreted together to avoid stale input state.

## Test Signals
ADB keyboard/mouse detection on IOP-based Macs, command timeout handling, autopoll/SRQ behavior, and reset/flush/talk/listen transaction tests are direct validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/adb_iop.h -->
