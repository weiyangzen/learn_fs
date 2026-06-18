# sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/socket-collection.h

## Purpose

This header declares the poll-backed socket collection and defines the queueing macros used by `bmi-tcp.c` when epoll is not enabled.

## Important APIs, Types, And Macros

- `struct socket_collection` stores the `pollfd` array, parallel address array, array capacity/count, queue mutex, remove and add queues, server socket, and pipe fds.
- `SC_READ_BIT`, `SC_WRITE_BIT`, and `SC_ERROR_BIT` are backend-independent readiness flags.
- `BMI_socket_collection_add` queues an address for polling when its socket fd is valid and wakes `poll` through the pipe.
- `BMI_socket_collection_remove` queues removal and wakes the collection.
- `BMI_socket_collection_add_write_bit` increments `write_ref_count`, queues an update, and wakes the collection.
- `BMI_socket_collection_remove_write_bit` decrements `write_ref_count`, asserts it remains nonnegative, queues an update, and wakes the collection.
- Function prototypes expose init, queue, finalize, and `testglobal`.

## Control Flow

The macros lock `queue_mutex`, call `BMI_socket_collection_queue` with either the add or remove queue, unlock, and write to the wakeup pipe. Actual array mutation is deferred until `BMI_socket_collection_testglobal`, allowing changes to be staged while another thread may be sleeping in `poll`.

## State And Persistence Behavior

This header defines the in-memory collection layout and uses `struct tcp_addr::write_ref_count`, `sc_link`, and `sc_index` as per-address collection state. There is no persistent storage outside process memory and open fds.

## Dependencies And Integration Points

The header depends on BMI method support, TCP address metadata, quicklist, and generic locks. It must remain source-compatible with `socket-collection-epoll.h` because `bmi-tcp.c` includes one or the other based on `__PVFS2_USE_EPOLL__`.

## Risks And Edge Cases

- Pipe wakeup writes use an uninitialized `char c`; byte value is irrelevant, but static analysis may flag it.
- Macro writes ignore short writes and errors, which can leave a polling thread asleep if the wakeup fails.
- Reference counting is managed by call pairing; missing a remove-write call leaves `POLLOUT` enabled and can cause busy progress loops.
- The macros expose multi-statement behavior with side effects, so arguments should not have side effects.

## Test Signals

Tests should validate queued add/remove behavior, write-bit nesting, assertion on write-ref underflow, no-op add for socket `-1`, wakeup behavior from a blocked poll, and compatibility of status bits with the epoll header.
