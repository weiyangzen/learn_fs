# sources/distributed-fs/ceph-client/net/dns_resolver/internal.h

## Purpose
This private header shares DNS resolver payload slot definitions, credentials, and debug tracing macros between `dns_key.c` and `dns_query.c`.

## Important APIs, Types, And Functions
The enum defines `dns_key_data` and `dns_key_error` payload indexes. It declares `dns_resolver_cache` and `dns_resolver_debug`. `kdebug()`, `kenter()`, and `kleave()` provide conditional debug logging tagged with the current task name.

## Control Flow
The macros emit `KERN_DEBUG` messages only when the module debug parameter is nonzero. `dns_query.c` uses the credential declaration; `dns_key.c` defines it and the payload layout.

## State And Persistence
No state is allocated here. It describes shared global variables owned by the implementation files.

## Dependencies And Integration Points
It includes compiler, kernel, and scheduler headers for `unlikely()`, `printk()`, and `current->comm`. It is internal to `net/dns_resolver`.

## Risks And Edge Cases
The debug mask is treated as boolean by the macros; bitwise debug categories are not implemented despite the parameter being an unsigned integer. Payload indexes must remain consistent with the key type and query code.

## Test Signals
Compile coverage is the main signal. Runtime debug tests can toggle the module parameter and verify traces appear without affecting key behavior.
