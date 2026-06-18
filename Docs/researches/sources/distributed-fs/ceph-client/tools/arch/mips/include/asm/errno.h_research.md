# sources/distributed-fs/ceph-client/tools/arch/mips/include/asm/errno.h

## Purpose
Internal MIPS errno wrapper for tools.

## Important APIs, Types, and Functions
Includes `uapi/asm/errno.h` and defines `EMAXERRNO` as 1133, the largest MIPS errno value in this copied set.

## Control Flow, State, and Persistence
No flow or state; it makes the UAPI errno table and max-error constant visible.

## Dependencies and Integration Points
Integrated with tools code that needs kernel-style error-range tests on MIPS.

## Risks and Test Signals
Risk is `EMAXERRNO` drift if the UAPI table changes. Test signals are preprocessing and error-pointer range checks.
