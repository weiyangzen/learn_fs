# subset-b-007852 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/bmi-tcp.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/bmi-tcp.c

## Purpose

This file implements the Unix TCP/IP BMI method for OrangeFS. It exports `bmi_tcp_ops`, translating the BMI method interface into nonblocking TCP sockets, BMI message headers, operation queues, completion queues, and socket readiness polling through either `socket-collection.c` or `socket-collection-epoll.c`.

It is the central transport state machine for `bmi_tcp`: initialization and finalization, address lookup, connect/accept, send and receive posting, progress during test calls, unexpected-message delivery, cancellation, address cleanup, socket buffer tuning, optional trusted-network checks, and PINT event instrumentation.

## Important APIs, Types, And Data

- `bmi_tcp_ops` wires BMI callbacks to `BMI_tcp_initialize`, `BMI_tcp_finalize`, `BMI_tcp_set_info`, `BMI_tcp_get_info`, memory helpers, send/recv post functions, test functions, address lookup, list variants, context open/close, cancel, reverse lookup, and address-range query.
- `struct tcp_msg_header` is the 24-byte wire envelope: magic, mode, tag, payload size, and encoded bytes. `BMI_TCP_ENC_HDR` and `BMI_TCP_DEC_HDR` convert the header using BMI byte-swap helpers.
- `struct tcp_op` is the TCP-private extension of `method_op_p`. It stores the header, TCP operation state, and stub list entries for single-buffer operations.
- `enum bmi_tcp_state` distinguishes `BMI_TCP_INPROGRESS`, `BMI_TCP_BUFFERING`, and `BMI_TCP_COMPLETE`.
- Operation lists are indexed by `IND_SEND`, `IND_RECV`, `IND_RECV_INFLIGHT`, `IND_RECV_EAGER_DONE_BUFFERING`, and `IND_COMPLETE_RECV_UNEXP`.
- `completion_array[BMI_MAX_CONTEXTS]` stores completed expected operations by BMI context. Unexpected receives use `IND_COMPLETE_RECV_UNEXP`.
- `tcp_socket_collection_p` is the readiness backend. The selected implementation is controlled by `__PVFS2_USE_EPOLL__`.
- `tcp_method_params` stores method flags, method id, listen address, and a zone/connect-test toggle.
- `forceful_cancel_mode`, `check_unexpected`, `tcp_buffer_size_receive`, and `tcp_buffer_size_send` are runtime knobs set through BMI info options.

## Control Flow

Initialization enters through `BMI_tcp_initialize`. Server mode validates a listen address, calls `tcp_server_init` to create/bind/listen on a nonblocking socket, allocates all operation lists, creates the socket collection with either the listening socket or `-1`, and registers PINT send/receive event types. Finalization deallocates the listen address, cleans operation lists, and finalizes the socket collection.

Address lookup is handled by `BMI_tcp_method_addr_lookup`. It extracts `tcp` address strings, parses host and port, optionally parses a network zone, allocates a BMI method address, and can run a first client connect test to establish the usable zone. Server-accepted addresses are allocated later by `handle_new_connection`.

Send posting starts in `BMI_tcp_post_send`, `BMI_tcp_post_sendunexpected`, or their list variants. These build a TCP header with mode `TCP_MODE_EAGER`, `TCP_MODE_REND`, or `TCP_MODE_UNEXP`, then call `tcp_post_send_generic`. That function encodes the header, preserves per-address send ordering by checking `IND_SEND`, initializes or advances the connection with `tcp_sock_init`, tries an immediate `payload_progress`, and either returns immediate completion or enqueues the remainder through `enqueue_operation`.

Receive posting starts in `BMI_tcp_post_recv` or `BMI_tcp_post_recv_list`, then calls `tcp_post_recv_generic`. It first checks for already buffered eager data in `IND_RECV_EAGER_DONE_BUFFERING`, then for a partially buffered in-flight operation. If a match exists, it copies buffered data into user buffers and may complete immediately. Otherwise it queues a posted receive in `IND_RECV` with an expected mode inferred from size.

Progress is driven by test calls. `BMI_tcp_test`, `BMI_tcp_testsome`, `BMI_tcp_testcontext`, and `BMI_tcp_testunexpected` take `interface_mutex`, call `tcp_do_work` when necessary, then pop completed operations from completion queues or the unexpected queue.

`tcp_do_work` serializes readiness scanning with `sc_test_busy`. It drops the interface mutex around `BMI_socket_collection_testglobal`, then handles each ready address. Error readiness goes to `tcp_do_work_error`; write readiness goes to `tcp_do_work_send`; read readiness goes to `tcp_do_work_recv`. If another thread is already polling, callers either return immediately for zero timeout or timed-wait on `interface_cond`.

`tcp_do_work_send` repeatedly finds the first queued send for an address and calls `work_on_send_op`. Send work ensures a nonblocking connect has completed, calls `payload_progress` with header bytes plus payload iovecs, removes the write bit when complete, and moves the op to the context completion queue.

`tcp_do_work_recv` accepts server connections, resumes in-flight receives, peeks for a complete header, enforces a short-header timeout, validates the magic number, and dispatches by mode. Unexpected messages allocate a temporary buffer and go to `IND_RECV_INFLIGHT` until complete, then to `IND_COMPLETE_RECV_UNEXP`. Expected eager or rendezvous messages match `IND_RECV` if possible; unmatched eager payloads are buffered, while unmatched rendezvous messages stay in buffering state until a receive post arrives.

`payload_progress` builds up to `BMI_TCP_IOV_COUNT + 1` iovecs using the static `stat_io_vector`, optionally prepends remaining header bytes on sends, calls `BMI_sockio_nbvector`, and updates list index, current segment offset, and header completion counters.

## State And Persistence Behavior

All transport state is process-local memory: operation lists, address objects, socket fds, context completion queues, and global method parameters. There is no durable persistence. Socket failures are persisted only in the lifetime of `struct tcp_addr` through `addr_error`, `dont_reconnect`, `not_connected`, `zero_read_limit`, and `short_header_timer`.

The method relies on BMI-layer ownership for method addresses. `tcp_forget_addr` removes a live fd from the socket collection, shuts it down, moves matching operations into error completion queues with `tcp_cleanse_addr`, records the error on the address, and either deallocates or asks the BMI control layer to forget it later. Server-accepted connections set `dont_reconnect` because they cannot be recreated by hostname/port.

Send ordering is serialized per address through `IND_SEND`. Receive ordering is maintained through matched posted receives, in-flight receives, and buffered eager queues. Unexpected messages are persisted in memory until `BMI_tcp_testunexpected` frees their method op and the caller later frees the payload with `BMI_tcp_unexpected_free`.

## Dependencies And Integration Points

This file depends on OrangeFS BMI support (`bmi-method-support.h`, callbacks, address allocation, op ids), operation lists (`op-list.h`), socket utilities (`sockio.h`), TCP address metadata (`bmi-tcp-addressing.h`), byte swapping, gossip logging, locks/condition variables, PINT hints, and PINT events. It integrates with build-time socket collection selection through `__PVFS2_USE_EPOLL__`.

Runtime integration with the BMI layer happens through method registration (`bmi_tcp_ops`), address registration/forget/drop callbacks, context ids, BMI error codes, and method info options such as `BMI_TCP_BUFFER_SEND_SIZE`, `BMI_TCP_BUFFER_RECEIVE_SIZE`, `BMI_DROP_ADDR`, `BMI_FORCEFUL_CANCEL_MODE`, `BMI_TCP_CHECK_UNEXPECTED`, and trusted-connection configuration.

Optional `USE_TRUSTED` code reads server configuration, converts trusted networks/netmasks, binds client sockets to privileged local ports, and filters accepted server connections by peer network and source port.

## Risks And Edge Cases

- `BMI_tcp_method_addr_lookup` allocates `zone_len + 1` bytes but writes `zone[zone_len + 1] = '\0'`, which is one byte past the allocation. This is under `BMI_TCP_ZONE`.
- The first call to `bmi_set_sock_buffers(tcp_addr_data->socket)` in `tcp_sock_init` occurs before a new socket is created, so it can query/set fd `-1` during the no-socket path.
- In `tcp_post_send_generic`, the `#if PINT_EVENT_ENABLED` block accumulates `total_size`, but `total_size` is not a parameter or local in that function. If that preprocessor symbol is enabled without another macro side effect, this is a compile-time risk.
- `stat_io_vector` is static global state. The file comments rely on BMI serialization; misuse outside the `interface_mutex` discipline would corrupt vector progress.
- `BMI_tcp_test` assumes `id_gen_fast_lookup(id)` returns a valid operation and asserts. Invalid ids can crash in debug/assert builds.
- Unmatched eager messages allocate full payload buffers up to the eager limit. A peer can pressure memory by delivering many unmatched eager messages.
- Partial headers are handled by peeking until the full header is available and closing after `BMI_TCP_HEADER_WAIT_SECONDS`. Slow peers or scheduler stalls can become disconnects.
- Some socket collection paths assert on allocation failures instead of returning graceful BMI errors.
- Cancellation after any header/payload progress closes the socket and can error unrelated operations sharing the address.

## Test Signals

Useful tests should cover immediate and queued sends, send-list/recv-list iovec progress across buffer boundaries, eager receive posted before data, eager data buffered before receive post, rendezvous data before and after receive post, unexpected send/test/free, invalid magic/header timeout, remote close/error readiness, cancellation before and after progress, reconnect after client address failure, server accept and reverse lookup, context-specific completions, and both poll and epoll socket-collection builds. Trusted-mode builds should test accepted/rejected networks and source ports. Build coverage should include `PINT_EVENT_ENABLED`, `BMI_TCP_ZONE`, `USE_TRUSTED`, server, and client configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/bmi-tcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/module.mk.in -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/module.mk.in

## Purpose

This makefile fragment adds the Unix `bmi_tcp` transport sources to OrangeFS build source variables when `BUILD_BMI_TCP` is enabled. It also selects the epoll or poll socket collection backend.

## Important APIs, Types, And Functions

The file does not define C APIs. It manipulates build variables:

- `BUILD_BMI_TCP` gates the whole fragment.
- `BUILD_EPOLL = @BUILD_EPOLL@` receives configure-time substitution.
- `DIR := src/io/bmi/bmi_tcp` scopes paths.
- `LIBSRC`, `SERVERSRC`, and `LIBBMISRC` always receive `bmi-tcp.c` and `sockio.c`.
- When `BUILD_EPOLL` is set, all three source lists receive `socket-collection-epoll.c`, and `MODCFLAGS_$(DIR)/bmi-tcp.c` defines `__PVFS2_USE_EPOLL__`.
- Otherwise all three lists receive `socket-collection.c`.

## Control Flow

The conditional nesting is simple: if TCP BMI is not requested, no sources or flags are added. If TCP BMI is requested, common transport and socket I/O sources are added, then the socket collection backend is selected by `BUILD_EPOLL`.

## State And Persistence Behavior

The fragment only contributes make variables during the build. It has no runtime state and no generated persistent outputs of its own.

## Dependencies And Integration Points

It depends on the configure system replacing `@BUILD_EPOLL@` and the surrounding OrangeFS build using `LIBSRC`, `SERVERSRC`, `LIBBMISRC`, and per-file `MODCFLAGS_*`. It is the build-time integration point that keeps `bmi-tcp.c` synchronized with the correct socket collection header through `__PVFS2_USE_EPOLL__`.

## Risks And Edge Cases

- If `BUILD_EPOLL` substitution is non-empty when the platform cannot compile epoll headers or calls, the build selects the Linux epoll backend incorrectly.
- If the make dialect treats `ifdef BUILD_EPOLL` as true for an unexpected placeholder value, the epoll path may be selected accidentally.
- `MODCFLAGS_$(DIR)/bmi-tcp.c` only defines the switch for `bmi-tcp.c`; any other source that needs the same compile-time branch would need its own flag.

## Test Signals

Build tests should verify `BUILD_BMI_TCP` disabled, TCP with poll backend, and TCP with epoll backend. The generated compile command for `bmi-tcp.c` should include `-D__PVFS2_USE_EPOLL__` only for the epoll build, and link inputs should contain exactly one socket collection implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/socket-collection-epoll.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/socket-collection-epoll.c

## Purpose

This file implements the epoll-backed socket collection used by `bmi-tcp.c` when `__PVFS2_USE_EPOLL__` is enabled. It tracks a server listening socket and connected address sockets in a Linux epoll fd and reports ready BMI method addresses plus read/write/error status bits.

## Important APIs, Types, And Functions

- `BMI_socket_collection_init(int new_server_socket)` allocates `struct socket_collection`, creates `epfd` with `epoll_create`, and optionally registers the listening socket with `event.data.ptr = NULL`.
- `BMI_socket_collection_finalize(socket_collection_p scp)` frees the collection object.
- `BMI_socket_collection_testglobal(...)` calls `epoll_wait`, converts epoll events into `SC_READ_BIT`, `SC_WRITE_BIT`, and `SC_ERROR_BIT`, and returns either a temporary server-port method address or the registered normal method address.
- The companion header supplies the add/remove/write-bit macros that call `epoll_ctl`.

## Control Flow

Initialization creates one epoll instance and optionally registers the server socket for read, error, and hangup events. Test calls clear caller output arrays, cap the wait batch at `BMI_EPOLL_MAX_PER_CYCLE`, wait for events, and translate each result. A `NULL` event pointer identifies the server socket; this causes allocation of a temporary method address marked `server_port = 1` so `bmi-tcp.c` can accept a connection. Non-NULL event pointers are returned directly as method addresses.

## State And Persistence Behavior

The only persistent state is `epfd`, `event_array`, and `server_socket` inside the collection object. Per-address registration state lives in the kernel epoll set and in each `struct tcp_addr`'s socket and write reference count, mutated by header macros.

## Dependencies And Integration Points

The file depends on Linux `<sys/epoll.h>`, OrangeFS BMI method address allocation (`alloc_tcp_method_addr`), TCP address metadata, gossip logging, and the shared socket collection status-bit contract. `bmi-tcp.c` consumes returned server-port pseudo-addresses in `handle_new_connection` and normal addresses in send/receive/error progress handlers.

## Risks And Edge Cases

- `BMI_socket_collection_finalize` frees the collection but does not close `epfd`, so ownership must be verified at a higher level or this leaks an fd.
- If registering the server socket fails after `epoll_create`, the error path frees `tmp_scp` but also does not close `epfd`.
- `epoll_wait` returns raw `-errno` rather than converting through `bmi_tcp_errno_to_pvfs`, unlike the poll implementation.
- The code tests `scp->event_array[i].events & POLLIN/POLLOUT`; on Linux these values match epoll event bits, but the source includes `<sys/poll.h>` to make that implicit dependency work.
- Server pseudo-address allocation uses `assert`, so allocation failure can abort.

## Test Signals

Tests should exercise server socket readiness, normal read/write readiness, EPOLLERR/EPOLLHUP conversion, empty waits, interrupted `epoll_wait`, more ready fds than `BMI_EPOLL_MAX_PER_CYCLE`, duplicate add handling from the header macros, write-bit add/remove transitions, and finalize under fd-leak checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/socket-collection-epoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/socket-collection-epoll.h -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/socket-collection-epoll.h

## Purpose

This header declares the epoll socket collection interface and implements registration macros used by `bmi-tcp.c`. It is the compile-time replacement for `socket-collection.h` when the epoll backend is selected.

## Important APIs, Types, And Macros

- `BMI_EPOLL_MAX_PER_CYCLE` caps the number of events consumed per `epoll_wait` cycle at 16.
- `struct socket_collection` contains `epfd`, a fixed `struct epoll_event event_array`, and the server socket.
- `SC_READ_BIT`, `SC_WRITE_BIT`, and `SC_ERROR_BIT` are the backend-independent readiness flags consumed by `bmi-tcp.c`.
- `BMI_socket_collection_add` registers a connected socket for read/error/hangup if the socket fd is valid.
- `BMI_socket_collection_remove` clears `write_ref_count` and removes a socket from epoll, tolerating `ENOENT`.
- `BMI_socket_collection_add_write_bit` increments `write_ref_count` and modifies interest to include `EPOLLOUT`.
- `BMI_socket_collection_remove_write_bit` decrements `write_ref_count` and removes `EPOLLOUT` when the count reaches zero.
- Function prototypes expose init, finalize, and `testglobal`.

## Control Flow

The macros perform direct `epoll_ctl` operations at the call site. Add uses `EPOLL_CTL_ADD`, remove uses `EPOLL_CTL_DEL`, and write-interest changes use `EPOLL_CTL_MOD`. `event.data.ptr` is the `bmi_method_addr_p`, allowing `socket-collection-epoll.c` to return the method address without a side table.

## State And Persistence Behavior

State is split between the kernel epoll interest list and `struct tcp_addr::write_ref_count`. There is no mutex in this backend header, so correctness relies on the caller's higher-level serialization through `interface_mutex`.

## Dependencies And Integration Points

The header depends on `<sys/epoll.h>`, `bmi-method-support.h`, `bmi-tcp-addressing.h`, quicklist and lock headers for shared type compatibility, and gossip logging. It must stay API-compatible with the poll header because `bmi-tcp.c` uses the same macro and function names for both backends.

## Risks And Edge Cases

- `BMI_socket_collection_add_write_bit` assumes the fd is already in epoll. If a nonblocking connect path tries to add write interest before `BMI_socket_collection_add`, `EPOLL_CTL_MOD` can fail.
- Error handling logs but does not propagate macro failures, so the caller may believe readiness interest was updated when it was not.
- `remove_write_bit` only issues `EPOLL_CTL_MOD` when the count reaches zero; incorrect reference counting can leave sockets permanently write-watched.
- The fixed event batch size can throttle large ready sets.

## Test Signals

Tests should validate macro behavior for invalid sockets, duplicate adds, removing absent fds, write reference nesting, write reference underflow assertion, and parity with the poll backend status-bit contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/socket-collection-epoll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/socket-collection.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/socket-collection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/socket-collection.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/socket-collection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/sockio.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/sockio.c

## Purpose

This file is a small socket utility layer for the TCP BMI method. It wraps IPv4 socket creation, bind, connect, address initialization, nonblocking receive/send/vector I/O, optional sendfile, and socket option get/set helpers.

## Important APIs, Types, And Functions

- `BMI_sockio_new_sock()` creates an `AF_INET`, `SOCK_STREAM`, `IPPROTO_TCP` socket.
- `BMI_sockio_bind_sock()` binds a socket to `INADDR_ANY` and a service port, retrying on `EINTR`.
- `BMI_sockio_bind_sock_specific()` initializes a named address and binds to it, returning BMI/PVFS error codes.
- `BMI_sockio_connect_sock()` initializes a named address and connects, retrying on `EINTR`, returning BMI/PVFS error codes.
- `BMI_sockio_init_sock()` has either a `gethostbyname` implementation with host-error conversion or an `inet_aton` implementation.
- `BMI_sockio_nbrecv()` loops nonblocking `recv` until the requested length is read, an error occurs, or `EAGAIN/EWOULDBLOCK` returns partial progress.
- `BMI_sockio_nbpeek()` peeks without consuming bytes and maps closed sockets to `EPIPE`.
- `BMI_sockio_nbsend()` loops nonblocking `send` until complete, blocked, interrupted, or errored.
- `BMI_sockio_nbvector()` performs one `readv` or `writev` attempt after retrying `EINTR`.
- `BMI_sockio_get_sockopt`, `BMI_sockio_set_tcpopt`, and `BMI_sockio_set_sockopt` wrap socket options.

## Control Flow

The bind/connect helpers construct `sockaddr_in` values through `BMI_sockio_init_sock`, then perform the syscall with `EINTR` retry. Nonblocking scalar I/O helpers loop to maximize progress until they hit would-block. Vector I/O intentionally does only one `readv` or `writev` call so the BMI progress loop can bound work per readiness event.

## State And Persistence Behavior

This file stores no global mutable state except compile-time `DEFAULT_MSG_FLAGS`. It mutates kernel socket state through bind, connect, send/receive, and socket options. Hostname resolution output is copied into caller-provided sockaddr storage.

## Dependencies And Integration Points

It depends on POSIX sockets, fcntl nonblocking flags asserted by callers, optional `gethostbyname`, optional `arpa/inet`, optional `sendfile`, BMI error conversion, and gossip logging. `bmi-tcp.c` uses this layer for all socket creation, connection, payload progress, header peeking, TCP_NODELAY, SO_REUSEADDR, and buffer-size options.

## Risks And Edge Cases

- `BMI_sockio_nbrecv` asserts the socket is nonblocking; `BMI_sockio_nbsend` does not assert but is used as nonblocking.
- `BMI_sockio_nbpeek` treats `EWOULDBLOCK` specially but not `EAGAIN` unless they are the same value on the platform.
- The fallback `inet_aton` resolver only accepts numeric IPv4 addresses.
- `BMI_sockio_init_sock` with `gethostbyname` is not reentrant/thread-safe on many platforms.
- `BMI_sockio_connect_sock` converts negative errno through `bmi_errno_to_pvfs`; callers must not convert it a second time.
- `DEFAULT_MSG_FLAGS` uses `MSG_NOSIGNAL` when available, but vector I/O via `writev` does not use `MSG_NOSIGNAL`.

## Test Signals

Tests should cover interrupted bind/connect/send/recv, nonblocking partial read/write, zero-length peer close mapping to `EPIPE`, would-block behavior, hostname and numeric address initialization, socket option wrappers, vector I/O partial progress, and builds with and without `HAVE_GETHOSTBYNAME`, `MSG_NOSIGNAL`, and `__USE_SENDFILE__`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/sockio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/sockio.h -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/sockio.h

## Purpose

This header exposes the TCP socket utility API used by `bmi-tcp.c` and defines convenience macros for socket options and blocking-mode changes.

## Important APIs, Types, And Macros

- Function prototypes cover socket creation, bind, specific bind, connect, address initialization, nonblocking recv/send/peek/vector I/O, socket option access, and optional sendfile.
- `GET_RECVBUFSIZE`, `GET_SENDBUFSIZE`, `SET_RECVBUFSIZE`, and `SET_SENDBUFSIZE` wrap `SO_RCVBUF` and `SO_SNDBUF`.
- `GET_MINSENDSIZE`, `GET_MINRECVSIZE`, `SET_MINSENDSIZE`, and `SET_MINRECVSIZE` wrap low-watermark options.
- `BRAINDEADSOCKS` disables buffer-size setters for platforms where changing socket buffers is unsafe.
- `SET_NONBLOCK`, `SET_NONBLOCK_AND_SIGIO`, and `CLR_NONBLOCK` use `fcntl` to manipulate fd flags.

## Control Flow

The header itself has no runtime control flow beyond macros. The nonblocking macros read current flags and write modified flags. The socket option macros route calls through the implementation in `sockio.c`.

## State And Persistence Behavior

The macros mutate kernel fd flags and socket options. No process-local state is stored by the header.

## Dependencies And Integration Points

The header depends on socket and networking system headers plus `bmi-types.h`. It is included by `bmi-tcp.c` and `sockio.c`. Its macros provide the names used by `bmi_set_sock_buffers` and setup paths in the transport.

## Risks And Edge Cases

- `SET_NONBLOCK` and related macros do not check `fcntl` failures and call `fcntl(F_GETFL)` inside `F_SETFL` arguments.
- `CLR_NONBLOCK` can clobber flag updates made concurrently by other code on the same fd.
- Buffer-size setter macros become empty statements under `BRAINDEADSOCKS`, so callers expecting return values must not rely on them.
- The header declares `struct iovec` use but does not include `<sys/uio.h>` directly; it relies on include order from consumers.

## Test Signals

Tests should compile consumers with strict warnings, verify macro expansion under `BRAINDEADSOCKS`, exercise nonblocking flag transitions, and confirm socket buffer macros route to the implementation wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/sockio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_wintcp/bmi-tcp-addressing.h -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_wintcp/bmi-tcp-addressing.h

## Purpose

This header defines the TCP-specific address metadata for the `bmi_wintcp` transport. It mirrors the Unix TCP address shape closely enough for shared-style transport logic, but it is located under the Windows TCP method tree.

## Important APIs, Types, And Macros

- `BMI_TCP_ZERO_READ_LIMIT` caps sequential zero-read observations before the transport treats a connection as dead.
- `BMI_TCP_HEADER_WAIT_SECONDS` caps how long a partial BMI TCP header may remain incomplete after detection.
- `BMI_TCP_PEER_IP` and `BMI_TCP_PEER_HOSTNAME` classify the cached peer string.
- Under `USE_TRUSTED`, `struct tcp_allowed_connection_s` stores trusted port and network enforcement state, allowed port range, network count, and network/netmask arrays.
- `struct tcp_addr` stores the backpointer to the generic BMI method address, BMI address handle, address error, hostname, port, socket fd, server-port flag, write reference count, connection state, socket-collection link/index, zero-read and short-header counters, reconnect policy, and cached peer string/type.
- `bmi_tcp_errno_to_pvfs` aliases `bmi_errno_to_pvfs`.
- Prototypes expose `tcp_forget_addr` and `alloc_tcp_method_addr`.

## Control Flow

The header has no executable control flow. It defines the state consumed by the WinTCP implementation and socket collection code. Address instances are expected to be allocated by `alloc_tcp_method_addr`, filled during lookup/connect/accept, updated by socket collection macros, and cleaned by `tcp_forget_addr`.

## State And Persistence Behavior

`struct tcp_addr` is the per-address in-memory persistence object for the transport. It records whether the socket is connected, whether reconnect is allowed, the last address-level error, current socket-collection index, pending write-interest count, zero-read counter, partial-header timer, and peer identity cache. No durable persistence is involved.

## Dependencies And Integration Points

The header depends on `bmi-types.h`, and under trusted builds it expects `struct in_addr` to be visible from the including context. It also uses `bmi_method_addr_p` and `struct qlist_head` without including their defining headers directly, so it relies on include order in the WinTCP source tree. It integrates with WinTCP's socket collection and BMI method implementation through the same field names used by the Unix TCP code.

## Risks And Edge Cases

- The file comments out `<netinet/in.h>` but trusted mode uses `struct in_addr`; Windows or compatibility headers must provide it before this header is parsed.
- It does not include the quicklist header even though `struct tcp_addr` embeds `struct qlist_head sc_link`.
- The Unix `bmi_tcp` version includes a `zone` field under `BMI_TCP_ZONE`; this WinTCP header does not. Shared code assumptions about `tcp_addr->zone` would not compile here.
- Socket descriptors are stored as `int`, which may be problematic if mapped directly to native Windows `SOCKET` handles without an abstraction layer.

## Test Signals

Build tests should compile the WinTCP transport with and without `USE_TRUSTED`, with strict include-order checks. Runtime-oriented tests should validate address allocation defaults, socket collection add/remove index updates, reconnect/error state transitions, peer string caching, zero-read limit handling, and partial-header timeout behavior in the WinTCP implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_wintcp/bmi-tcp-addressing.h -->
