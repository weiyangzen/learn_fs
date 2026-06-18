# sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/socket-collection.c

## Purpose

This file implements the portable poll-backed socket collection for `bmi_tcp`. It maintains dynamic arrays of `pollfd` entries and corresponding BMI method addresses, queues add/remove operations under a mutex, and returns sockets that are ready for read, write, or error handling.

## Important APIs, Types, And Functions

- `BMI_socket_collection_init(int new_server_socket)` allocates arrays, initializes add/remove queues, creates a wakeup pipe, optionally inserts the server socket, and always inserts the pipe read end.
- `BMI_socket_collection_queue(socket_collection_p scp, bmi_method_addr_p map, struct qlist_head *queue)` removes duplicate pending queue entries for the same address, then queues the address for add or remove.
- `BMI_socket_collection_finalize(socket_collection_p scp)` frees arrays and the collection object.
- `BMI_socket_collection_testglobal(...)` applies queued removals/additions, runs `poll`, drains the wakeup pipe, converts `revents` into collection status bits, and returns ready method addresses.

## Control Flow

Add and remove requests are not applied immediately by the public macros in the header. They enqueue a `tcp_addr` link and write one byte to `pipe_fd[1]`. `BMI_socket_collection_testglobal` drains those queues before polling: removals swap the last array entry into the removed slot and update the shifted address's `sc_index`; additions either update an existing entry's events or append a new poll entry, growing arrays by 32 when full.

The poll loop waits on the current array. The pipe fd is never returned as a ready address; when it fires, the code drains one byte and may repeat polling with the remaining timeout if no real sockets were ready. A `NULL` address entry marks the server socket and causes allocation of a temporary server-port method address for the accept path.

## State And Persistence Behavior

Persistent state includes the pollfd and address arrays, array sizes, queued add/remove lists, queue mutex, server socket, and wakeup pipe fds. Each `struct tcp_addr` stores its `sc_index` and `write_ref_count`, which are synchronized with array entries during queued updates.

## Dependencies And Integration Points

The implementation depends on `poll`, `pipe`, quicklist links embedded in `struct tcp_addr`, OrangeFS locking wrappers, gossip logging, and BMI method address allocation. It integrates with `bmi-tcp.c` through `BMI_socket_collection_testglobal` and the status-bit enum shared with the header.

## Risks And Edge Cases

- `BMI_socket_collection_finalize` frees memory but does not close `pipe_fd[0]` or `pipe_fd[1]`, so repeated initialize/finalize can leak fds.
- Array growth allocation failures are handled with `assert`, not propagated.
- Removal swaps the last address into the removed index and immediately dereferences `scp->addr_array[tcp_addr_data->sc_index]`. This assumes the swapped entry is never the pipe or server `NULL` slot in problematic positions.
- Wakeup pipe writes in macros do not handle `EAGAIN`, `EINTR`, or a full pipe.
- Only one byte is drained per pipe readiness event, so many queued changes can leave the pipe readable longer than necessary.
- `BMI_socket_collection_queue` reuses a single `sc_link` per address, so callers must not place the same address in unrelated quicklists through that link.

## Test Signals

Tests should cover add/remove before and during poll, duplicate queued operations, write reference changes, dynamic array growth, server socket readiness, pipe wakeups with no socket readiness, timeout accounting after wakeups, error/hangup readiness, removal of last and middle entries, and fd-leak checks on finalize.
