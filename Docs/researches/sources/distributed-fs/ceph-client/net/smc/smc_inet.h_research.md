# sources/distributed-fs/ceph-client/net/smc/smc_inet.h

## Purpose
`smc_inet.h` declares the lifecycle hooks for registering SMC as `IPPROTO_SMC` in the inet protocol tables.

## Important APIs, Types, and Functions
The header exposes `smc_inet_init()` and `smc_inet_exit()`. It intentionally contains no state structures, keeping inet registration details private to `smc_inet.c`.

## Control Flow
SMC module initialization can call `smc_inet_init()` to publish IPv4 and optional IPv6 protocol-switch entries. Module exit calls `smc_inet_exit()` to unregister them in the reverse path.

## State and Persistence
The header owns no state. Registered protocol state lives in static objects in `smc_inet.c` and per-socket allocations in the networking stack.

## Dependencies and Integration Points
It is included by top-level SMC initialization code and implemented by `smc_inet.c`. It provides a narrow integration point so other SMC modules do not need inet registration internals.

## Risks
Because the header only declares lifecycle calls, risk is mostly ordering: callers must invoke init after dependencies such as common socket operations are ready, and exit before those operations are unavailable.

## Test Signals
Build coverage and module init/exit tests should confirm that callers can register and unregister `IPPROTO_SMC` cleanly in IPv4-only and IPv6-enabled configurations.
