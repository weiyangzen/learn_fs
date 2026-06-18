# sources/distributed-fs/ceph-client/drivers/net/phy/stubs.c

## Purpose
`stubs.c` exports the global `phylib_stubs` pointer used by built-in networking code when `CONFIG_PHYLIB` can be a module. It provides an indirection point so core code can call PHY-library functionality without directly depending on module-only symbols.

## Important APIs, Types, And Functions
The only symbol is `const struct phylib_stubs *phylib_stubs`, exported with `EXPORT_SYMBOL_GPL()`. The struct type is declared in `<linux/phylib_stubs.h>`.

## Control Flow
There is no executable control flow in this file. Initialization and assignment of the pointer occur elsewhere; this compilation unit only defines storage and exports it.

## State And Persistence
The pointer is global kernel state. It is initially null and remains whatever the PHY library registration code sets it to. Consumers must handle the possibility that phylib is not loaded or has not populated the table.

## Dependencies And Integration Points
The file depends on the phylib stubs header and module export machinery. It integrates built-in network stack code with a modular phylib provider.

## Risks And Edge Cases
The primary risk is lifetime and null-pointer misuse by consumers. Since the pointer is exported global state, changes to the underlying `struct phylib_stubs` contract must remain synchronized across providers and callers.

## Test Signals
Build both built-in and modular PHYLIB configurations, verify exported symbol availability with module loading, and exercise callers when `phylib_stubs` is null and after it is populated.
