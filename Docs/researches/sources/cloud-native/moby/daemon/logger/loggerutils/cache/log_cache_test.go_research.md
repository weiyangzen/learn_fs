# sources/cloud-native/moby/daemon/logger/loggerutils/cache/log_cache_test.go

Purpose: tests local log cache wrapper behavior.

Important APIs/types/functions: defines a `fakeLogger` with `Log`, `Name`, and `Close`, and tests cache logging behavior.

Control flow/state/persistence: in-memory fake plus cache-backed files or logger internals depending on constructor path.

Dependencies/integration: validates interaction between cache wrapper and core `logger.Logger` ownership semantics.

Risks: fake logger is simpler than real remote drivers, so delivery-failure edge cases may need separate tests.

Test signals: direct signal that cached logging forwards messages and remains closeable.
