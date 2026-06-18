# sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/bitsperlong.h

## Purpose
s390 UAPI word-size contract.

## Important APIs, Types, and Functions
Defines `__BITS_PER_LONG` as 64 and includes generic bits-per-long.

## Control Flow, State, and Persistence
No state or flow.

## Dependencies and Integration Points
Integrated by s390 UAPI/tools headers.

## Risks and Test Signals
Risk is minimal unless 31-bit compatibility headers are expected in this tools path. Test signals are s390 tools preprocessing/builds.
