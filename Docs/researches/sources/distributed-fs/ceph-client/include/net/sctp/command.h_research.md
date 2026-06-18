# sources/distributed-fs/ceph-client/include/net/sctp/command.h

## Purpose
This header defines the command-sequence abstraction emitted by SCTP state functions and consumed by the side-effect interpreter. It decouples pure state-machine decisions from actions such as timers, replies, SACK processing, transport changes, and ULP notifications.

## Important APIs, Types, And Functions
`enum sctp_verb` enumerates actions including new/delete association, state changes, TSN reporting, SACK generation/processing, packet/chunk replies, retransmission, ECN, timer management, heartbeat/probe handling, transport state changes, association failure, FWD-TSN, AUTH shared keys, stream reset, and ASCONF queue purge. `union sctp_arg` carries typed arguments. Constructor macros build typed args such as `SCTP_CHUNK()`, `SCTP_ASOC()`, `SCTP_TRANSPORT()`, and `SCTP_STATE()`. `struct sctp_cmd_seq` stores up to `SCTP_MAX_NUM_COMMANDS` commands, filled backward and iterated by `sctp_next_cmd()`.

## Control Flow
State functions append commands with `sctp_add_cmd_sf()`. The side-effect engine later walks commands in intended order via `sctp_next_cmd()`, applying transport, association, timer, and ULP actions.

## State And Persistence
Command sequences are transient per event. Persistent effects occur only when interpreted against associations, transports, queues, and sockets.

## Dependencies And Integration Points
It includes SCTP constants and structs, so it connects the state-machine tables to all main SCTP objects. It is central to `sm.h` state functions and primitive/chunk/timeout handling.

## Risks And Test Signals
Risks include command overflow causing `BUG_ON`, mismatched union member use, missing commands for new state transitions, and ordering-dependent behavior. Test signals include handshake, shutdown, retransmission, ECN, ASCONF, AUTH, and stream-reset state-machine coverage with command tracing.
