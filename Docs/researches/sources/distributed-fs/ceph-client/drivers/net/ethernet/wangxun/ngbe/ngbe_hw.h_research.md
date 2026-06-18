# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_hw.h

## Purpose
`ngbe_hw.h` declares the GbE PF hardware helper API used by probe, reset, and module power paths.

## Important APIs, Types, and Functions
It declares `ngbe_eeprom_chksum_hostif()`, `ngbe_sfp_modules_txrx_powerctl()`, and `ngbe_reset_hw()`.

## Control Flow
No executable flow exists. `ngbe_main.c` calls these routines during probe, resume, reset, and link/module transitions.

## State and Persistence Behavior
The header owns no state. Implemented functions manipulate `struct wx` and hardware registers.

## Dependencies and Integration Points
It requires `struct wx` from shared headers and binds `ngbe_main.c` to `ngbe_hw.c`.

## Risks and Edge Cases
Prototype drift breaks module linkage. Since power control uses a boolean with hardware-inverted semantics, callers must use the API consistently instead of writing GPIO directly.

## Test Signals
Build and run reset/probe paths that call all declarations.
