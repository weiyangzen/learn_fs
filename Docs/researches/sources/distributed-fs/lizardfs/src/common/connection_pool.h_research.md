# sources/distributed-fs/lizardfs/src/common/connection_pool.h

Purpose: declares `ConnectionPool`, a small synchronized cache of reusable network file descriptors grouped by remote address.

Important APIs/types/functions: public methods are `getConnection(const NetworkAddress&)`, `putConnection(int, const NetworkAddress&, int timeout)`, and `cleanup()`. The private nested `Connection` stores `fd_` and a `Timeout validUntil_` and exposes `fd()` and `isValid()`.

Control flow: the header establishes the ownership model: callers insert open descriptors with a timeout, later retrieve one descriptor or `-1`, and periodically call cleanup to close expired entries.

State and persistence: state is the guarded map of address to FIFO connection lists. The timeout uses `common/time_utils.h`; there is no durable state.

Dependencies and integration: depends on `NetworkAddress` ordering for use as a `std::map` key, `std::mutex`, and `Timeout`. It is an integration utility for common networking code.

Risks: the API lacks RAII ownership for returned descriptors; callers must close descriptors they retrieve and do not use. The class is non-copyable by implication because of `std::mutex`, but copy/delete semantics are not explicitly stated.

Test signals: no direct test in the mapped files; source inspection shows simple API surface but edge cases around timeout and fd lifecycle need integration coverage.
