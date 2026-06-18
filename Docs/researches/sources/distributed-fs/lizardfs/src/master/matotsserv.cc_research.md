# sources/distributed-fs/lizardfs/src/master/matotsserv.cc

## Purpose

`matotsserv.cc` implements the master-to-tapeserver service used for tape/archive copy tracking. It accepts tapeserver connections on `MATOTS_LISTEN_HOST`/`MATOTS_LISTEN_PORT`, registers named tapeservers, receives lists of tape-stored files, queues file keys for tapeserver transfer, and exposes connected tapeserver info. The source was read as a complete 535-line implementation.

## Important APIs, Types, and Functions

Private `matotsserventry` stores mode, socket, poll position, timers, protocol queues, server name/label/id/address/version, and whether initial files were registered. Static globals track the listening socket, connected tapeservers, and a queue of `TapeKey`s to send. Public functions are `matotsserv_init`, `matotsserv_can_enqueue_node`, `matotsserv_enqueue_node`, `matotsserv_get_tapeserver_info`, and `matotsserv_get_tapeservers`.

## Control Flow

Initialization binds the listener, registers event-loop hooks, and schedules periodic file flushing when master. Poll handling accepts only on master, reads `InputPacket`s, dispatches register/has-files/end-of-files messages, writes output packets, sends NOP keepalives, and kills timed-out connections. Periodic flow sends queued `TapeKey`s to the first connected tapeserver via `matots::putFiles::build` and clears the queue.

## State and Persistence Behavior

The module stores runtime connection state and an in-memory queue of file keys waiting to be sent. Persistent file-copy state is updated indirectly through `fs_add_tape_copy` when tapeservers report files, and by callers that enqueue tape copies after filesystem operations. Tapeserver IDs are hashes of server names and kept in a static set to reject duplicate active registrations.

## Dependencies and Integration Points

It depends on event-loop callbacks, socket wrappers, `InputPacket`/`OutputPacket`, `protocol/matots` and `protocol/tstoma`, media labels, network addresses, filesystem tape-copy APIs, and personality promotion hooks. `SetGoalTask` calls `matotsserv_can_enqueue_node` and `fsnodes_enqueue_tape_copies` when file goals change.

## Risks and Edge Cases

Server IDs are `std::hash<std::string>()` values, which are not a cryptographic identity and may vary by implementation or collide. `matotsserv_enqueue_node` asserts that a registered tapeserver exists after callers check availability; misuse can abort. The file queue is cleared after sending to the first tapeserver, so distribution/failover semantics are minimal. Registered server labels remain wildcard in this implementation. Malformed packets disconnect the tapeserver.

## Test Signals

Signals include register success/failure and duplicate-name rejection tests, has-files integration with filesystem tape-copy state, queue flush tests for `putFiles`, timeout/NOP/reload behavior, and status API checks for registered versus unregistered connections.
