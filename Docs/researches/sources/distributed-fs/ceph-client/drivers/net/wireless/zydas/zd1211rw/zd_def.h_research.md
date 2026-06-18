# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_def.h

## Purpose
Provides small shared definitions for the ZD1211RW driver: the `zd_addr_t` register-address type, debug logging helpers, debug assertions, and debug-only memory poisoning.

## Important APIs, Types, And Functions
Defines `typedef u16 zd_addr_t`, `dev_printk_f()`, `dev_dbg_f()`, `dev_dbg_f_limit()`, `dev_dbg_f_cond()`, `ZD_ASSERT()`, and `ZD_MEMCLEAR()`. In non-DEBUG builds, debug helpers compile to no-op forms that preserve argument type checking minimally and avoid side effects except `(void)(dev)`.

## Control Flow
No runtime flow beyond conditional debug logging/assertion. In DEBUG builds, failed assertions print file/line/expression and dump the stack; `ZD_MEMCLEAR()` fills memory with `0xff` after teardown.

## State And Persistence
No persistent state. The file influences teardown diagnostics by optionally poisoning structs after clear functions.

## Dependencies And Integration Points
Depends on Linux kernel, stringify, and device logging headers. Included by the ZD1211RW C and header files as the baseline local utility header.

## Risks
Debug-only behavior can hide bugs in production builds, especially assertions around locking. `ZD_MEMCLEAR()` is intentionally a no-op outside DEBUG, so clear paths must explicitly release resources before invoking it.

## Test Signals
Compile with and without `DEBUG` to confirm both macro sets. DEBUG runs should surface lock contract violations during register IO, RF operations, USB async command batching, and teardown.
