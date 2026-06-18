# sources/distributed-fs/ceph/src/rgw/rgw_req_context.h

## Purpose

Defines a compact request context struct intended to carry frontend-created request metadata down to backend calls.

## Important APIs, Types, and Functions

`req_context` contains `const DoutPrefixProvider* dpp`, `optional_yield y`, and `const jspan* span`.

## Control Flow and Data Flow

Backend helpers can accept this struct instead of separate logging prefix, coroutine yield context, and tracing span parameters. The struct is a passive carrier with default null prefix and default yield state.

## State and Persistence Behavior

No owned or durable state is present. The pointers are borrowed and require external lifetime management.

## Dependencies and Integration Points

Depends on `common/async/yield_context.h` and forward declares `DoutPrefixProvider`. Integrates with tracing/logging-aware SAL/backend function calls.

## Risks and Edge Cases

`span` is not default-initialized in the declaration, unlike `dpp`; users must initialize it before reading. Borrowed pointers can dangle if contexts outlive the request.

## Test Signals

Build coverage for aggregate initialization, static analysis for uninitialized `span`, and API tests where backend helpers receive null and non-null logging/yield/span values.
