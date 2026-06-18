# sources/distributed-fs/eos/namespace/utils/Descriptor.hh

## Purpose
`Descriptor.hh` declares simple wrappers around file descriptors and sockets plus a stream-building exception type.

## Important APIs, Types, and Functions
`DescriptorException` stores an `std::ostringstream` and exposes `getMessage()`. `Descriptor` stores `int pFD` and declares descriptor assignment, lookup, `seek()`, `close()`, blocking/non-blocking reads, offset reads, `tryRead()`, and `write()`. `Socket` derives from `Descriptor`, defines `Protocol { TCP, UDP }`, and declares initialization, connect, bind, listen, accept, close, and socket option wrappers.

## Control Flow
The header itself has minimal inline behavior: constructors initialize or wrap file descriptors, `seek()` delegates to `lseek()`, and socket constructors delegate to `Descriptor`. The implementation supplies syscall loops and error handling.

## State and Persistence Behavior
`Descriptor` stores a raw descriptor value and does not declare a destructor that closes it. Ownership semantics are therefore manual. `Socket::accept()` returns an owning raw pointer by contract in comments.

## Dependencies and Integration Points
It depends on POSIX descriptor/socket headers and is used by legacy namespace code requiring direct system I/O wrappers. It intentionally avoids higher-level networking abstractions.

## Risks and Edge Cases
`DescriptorException` is not derived from `std::exception` despite including `<exception>`, which can surprise callers. No copy/move controls are declared for `Descriptor` or `Socket`, so accidental copying can duplicate wrapper objects around the same FD. Manual close requirements invite leaks.

## Test Signals
Header behavior should be validated through implementation tests for descriptor lifecycle, copy hazards, exception catching style, and accepted socket ownership.
