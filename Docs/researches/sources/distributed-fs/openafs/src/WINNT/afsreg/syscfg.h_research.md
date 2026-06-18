# sources/distributed-fs/openafs/src/WINNT/afsreg/syscfg.h

## Purpose
Declares the Windows system-configuration function that returns network interface address information.

## Important APIs, Types, And Functions
The sole public function is `syscfg_GetIFInfo(int *count, int *addrs, int *masks, int *mtus, int *flags)`. It uses C linkage for C++ callers.

## Control Flow
Callers pass array capacity in `*count`; on return, `*count` is the number of elements filled and the function result is the total configured usable interface count or `-1` on error.

## State And Persistence
The header defines no state. The API exposes caller-provided arrays for IPv4 addresses, masks, MTUs, and flags.

## Dependencies And Integration Points
It pairs with `syscfg.c` and is included by the interface-info test utility and network initialization code.

## Risks And Test Signals
The API contract relies on callers sizing all arrays consistently and interpreting addresses in host byte order. Compile tests and `getifinfo` runtime output are the main signals.
