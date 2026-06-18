# sources/distributed-fs/eos/namespace/utils/Descriptor.cc

## Purpose
`Descriptor.cc` implements low-level file descriptor and IPv4 socket helpers declared in `Descriptor.hh`. It provides blocking/full-length read and write loops, offset reads, socket setup, DNS resolution, and socket option wrappers.

## Important APIs, Types, and Functions
Static `resolve()` resolves a hostname into `sockaddr_in`, using `gethostbyname()` on Apple and `gethostbyname_r()` with a dynamically resized buffer elsewhere. Implemented methods include `Socket::init()`, `connect()`, `bind()`, `listen()`, `accept()`, `Descriptor::close()`, `readBlocking()`, `readNonBlocking()`, `offsetReadNonBlocking()`, `tryRead()`, `write()`, `Socket::setsockopt()`, and `Socket::getsockopt()`.

## Control Flow
Socket methods lazily initialize TCP sockets when needed, resolve addresses, configure IPv4 `sockaddr_in`, and throw `DescriptorException` on syscall failures. Descriptor read/write methods loop until the requested byte count is satisfied. Blocking reads treat EOF as an error. Non-blocking file-style reads optionally sleep and retry on EOF when a nonzero poll interval is supplied. `tryRead()` returns the number of bytes available before EOF. `accept()` wraps the accepted descriptor in a heap-allocated `Socket`.

## State and Persistence Behavior
The classes wrap integer file descriptors and mutate `pFD` on initialization and close. They do not own descriptors through RAII destructors in this implementation; callers must call `close()` or manage wrapper lifetime carefully. Socket operations affect OS network state.

## Dependencies and Integration Points
The implementation uses POSIX sockets, `read`, `write`, `pread`, `lseek`, DNS APIs, and errno strings. It is a legacy utility layer for code needing simple descriptor/socket abstractions.

## Risks and Edge Cases
`Socket::listen(unsigned queue)` ignores its `queue` argument and always passes 20. On `connect()` and `bind()` failures, descriptors are closed but `pFD` is not reset to -1. `readBlocking()` reports `strerror(errno)` on EOF even though errno may be stale. The helper supports IPv4 only and uses obsolete hostname APIs. `DescriptorException` does not derive from `std::exception`, so normal catch patterns may miss it. `Socket::accept()` transfers ownership through a raw pointer.

## Test Signals
Tests should cover full and partial reads/writes, EOF handling with and without polling, offset reads, try-read byte counts, socket connect/bind/listen failures, queue argument behavior, and descriptor state after errors.
