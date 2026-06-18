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
