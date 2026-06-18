# sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/store.cc

## Purpose
Implements the generic dbstore config-store factory, routing supported URIs to backend-specific `sal::ConfigStore` implementations.

## APIs, Flow, And State
`create_config_store(dpp, uri)` checks compile-time `SQLITE_ENABLED`, accepts only URIs starting with `file:`, and delegates to `config::create_sqlite_store()`. Any unsupported URI throws `std::runtime_error` with the rejected URI. It owns no persistent state.

## Dependencies And Integration
Depends on `store.h`, `fmt/format.h`, and conditionally `sqlite.h`. It is the integration point between RGW code that wants a `sal::ConfigStore` and the SQLite config implementation.

## Risks And Test Signals
URI support is intentionally narrow. If SQLite is not compiled in, even `file:` URIs throw at runtime. Because failure is an exception rather than a negative errno, callers must be exception-aware. Tests should cover SQLite-enabled file URI routing and unsupported URI failure.
