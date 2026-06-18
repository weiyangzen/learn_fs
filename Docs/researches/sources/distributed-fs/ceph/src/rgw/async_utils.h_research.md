# sources/distributed-fs/ceph/src/rgw/async_utils.h

## Purpose

`async_utils.h` provides RGW helpers for invoking Boost.Asio C++ coroutines from synchronous or stackful-coroutine code. The helpers co_spawn awaitables, optionally block the caller, capture exceptions, convert exceptions to negative Ceph return codes, and log failures with RGW debug-prefix context.

## Important APIs, types, and functions

All APIs are overloads of `rgw::run_coro()`. There are executor-based and execution-context-based overloads for awaitables returning `void`, a single value `T`, or `std::tuple<Ts...>`. The first family is intended for interactive/blocking frontends and writes exception text to `std::string* what`. The second family accepts `std::string_view name`, `optional_yield y`, and a log level; it runs through an existing stackful yield context when available or blocks otherwise.

The implementation uses Boost.Asio concepts, `asio::awaitable`, `asio::co_spawn`, Ceph async completion adapters `use_blocked` and `redirect_error`, `maybe_warn_about_blocking()`, `ceph::from_exception()`, and `ldpp_dout_fmt()`.

## Control flow

For blocking calls, `run_coro()` initializes `std::exception_ptr e`, warns about blocking, spawns the awaitable on the supplied executor with `async::use_blocked[e]`, optionally assigns the returned value(s), then returns `ceph::from_exception(e, what)`. For yield-aware calls, if `optional_yield` is present the coroutine is spawned on the yield executor with `async::redirect_error(yield, e)` so it cooperates with the stackful coroutine. If no yield is present, it falls back to the blocking path. After completion, it converts any exception and logs `name: failed: what` when an exception was captured.

Execution-context overloads forward to executor overloads through `get_executor()`. Template constraints require the supplied executor to be convertible to the awaitable executor, which catches mismatched coroutine/executor use at compile time.

## State and persistence behavior

The helpers keep only stack-local exception/value state. They do not persist data. They may block an RGW thread when called with null yield or from synchronous tools such as `radosgw-admin`.

## Dependencies and integration points

The header depends on Boost.Asio coroutine support, Ceph async concepts/adapters, Ceph error conversion, dout logging, and `rgw_asio_thread.h` for blocking warnings/yield types. Source references show `radosgw-admin.cc` and RGW REST log code use `rgw::run_coro()` to bridge coroutine implementations into command handlers and admin flows.

## Risks and edge cases

The helpers are marked `noexcept` only for the void blocking overloads; value and tuple overloads assume assignment from `co_spawn()` result does not throw. Blocking fallback can deadlock or harm latency if used on an executor that requires the current thread to make progress; `maybe_warn_about_blocking()` is the guard signal. Tuple overloads assign to `std::tuple<Ts&...>`; caller lifetimes and exact arity/types must match. The comments contain typos but not behavioral issues.

## Test signals

Tests should cover successful void/value/tuple coroutines, exception conversion and `what` population, yield-present versus null-yield execution, logging on failure, executor-convertibility compile checks, and integration in `radosgw-admin` commands that currently call `run_coro()`.
