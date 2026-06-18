## sources/distributed-fs/eos/namespace/MDException.hh

Purpose: Defines exception and status primitives for EOS namespace metadata operations.

Important APIs and types: `MDException` stores errno and stream-built message, overrides `what`, supports copy construction, and offers `wrapAndRethrow`. Macros `throw_mdexception`, `make_mdexception`, and `SSTR` simplify throwing and folly exception wrappers. `MDStatus` stores errno/message and can throw if not ok.

Control flow: callers stream context into `getMessage()` and throw. `what()` materializes the stream into an owned C string each call. `MDStatus::throwIfNotOk` converts failed statuses into `MDException`.

State and persistence: exception state is transient errno plus message stream. There is no durable state, but errno values drive caller behavior and protocol return codes.

Dependencies and integration: used throughout namespace services, resolver, prefetcher callers, and MGM code. Depends on standard exceptions/streams/cerrno and folly `ExceptionWrapper`.

Risks: `what()` mutates a `mutable char*` even on a const exception, so concurrent calls on the same exception object are unsafe. Macros create local names and should be used carefully in nested scopes. `SSTR` relies on stream expression conversion patterns that can be compiler-sensitive.

Test signals: exception copy preserves message/errno, `what()` is stable enough for logging, `wrapAndRethrow` prefixes messages, folly wrapper construction works, and `MDStatus` ok/error paths throw as expected.
