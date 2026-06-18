# sources/distributed-fs/ceph-client/include/net/sctp/sm.h

## Purpose
This header declares the SCTP state-machine interface: event dispositions, state-function signatures, timer function type, table entries, and the large set of state functions used for chunks, timers, primitives, and protocol validation.

## Important APIs, Types, And Functions
`enum sctp_disposition` describes state-function outcomes such as discard, consume, no-memory, delete TCB, abort, violation, not implemented, user error, and bug. `sctp_state_fn_t` is the uniform state-function signature taking net, endpoint, association, subtype, event arg, and command sequence. `struct sctp_sm_table_entry` pairs a function pointer with a debug name. Prototypes include generic `sctp_sf_not_impl`/`bug`, timer handlers, INIT/COOKIE/DATA/SACK/SHUTDOWN/ERROR handlers, primitive handlers, and validation helpers.

## Control Flow
The SCTP engine selects a state table by event type and current association state, invokes the matching `sctp_sf_*` function, then interprets the emitted `sctp_cmd_seq` if the disposition permits further side effects.

## State And Persistence
The header owns no state, but state functions mutate associations, transports, queues, and timers through commands rather than direct side effects where possible.

## Dependencies And Integration Points
It depends on `command.h`, `sctp.h`, core SCTP structures, and kernel allocation/types. It integrates with receive chunk classification, ULP primitives, timeout callbacks, and diagnostics through function names.

## Risks And Test Signals
Risks include missing table entries, wrong disposition semantics, command emission order bugs, and validation bypasses for malformed chunks. Test signals are protocol conformance tests for handshake, duplicate INIT, shutdown, abort, stale cookie, invalid stream, SACK/FWD-TSN, timeout, and primitive handling.
