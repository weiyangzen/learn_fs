# sources/distributed-fs/moosefs/mfsmaster/iptosesid.h

## Purpose
`iptosesid.h` declares the transient IP-to-session-id compatibility cache used by the MooseFS master client service. It gives callers a minimal add/check/get API without exposing list storage or timeout behavior.

## Important APIs
`iptosesid_add(uint32_t ip, uint32_t sessionid)` records a short-lived mapping. `iptosesid_check(uint32_t ip)` reports whether a currently valid mapping exists. `iptosesid_get(uint32_t ip)` returns and consumes a valid session id for that IP, or returns `0` when no valid mapping exists.

The header includes only `<inttypes.h>`, so the public contract is pure fixed-width integer values.

## Control Flow And State
The implementation keeps all state internally. Callers use `check` when they need to know whether an old-client patch path is available, and `get` when they want to consume the mapping.

There is no init, reload, store/load, or cleanup API. The cache is expected to be process-local and self-cleaning on access.

## Dependencies And Integration Points
`matoclserv.c` is the known consumer, using the functions for pre-3.0 client compatibility during session handling. The API assumes the caller already has the peer IP in the same 32-bit representation used by the master network layer.

## Risks
Since `0` is the miss value for `iptosesid_get`, session id `0` cannot be distinguished from a miss at this interface. That is acceptable only if real session ids are never zero.

The absence of a cleanup API is fine for event-loop usage but can complicate deterministic unit testing unless tests expose or reset module state by process isolation.

## Test Signals
Tests should compile consumers against the header, verify that `get` consumes entries while `check` does not, and assert that the old-client compatibility path handles a zero return as a miss.
