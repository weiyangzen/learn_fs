# sources/distributed-fs/ceph/src/osdc/error_code.h

## Purpose

`error_code.h` declares the Objecter/OSDC error domain for Boost.System. It allows `osdc_errc` enum values to be used directly as error codes and conditions by Objecter callers and asynchronous completions.

## Important APIs, types, and functions

The header declares `osdc_category()`, enum class `osdc_errc`, Boost.System traits `is_error_code_enum` and `is_error_condition_enum`, and inline `make_error_code()` / `make_error_condition()` conversions. Enum values cover pool existence, precondition, unsupported operation, snapshot existence, timeout, pool EIO, and handler failure cases.

## Control flow

When code returns or passes an `osdc_errc`, Boost.System finds the specialized trait and constructs a `boost::system::error_code` using `osdc_category()`. Objecter APIs with Asio completion signatures can therefore report objecter-specific failures without exposing negative errno as the primary typed interface.

## State and persistence behavior

No state is declared here. Runtime category state is provided by `error_code.cc`.

## Dependencies and integration points

The header depends only on Boost.System. It is included by Objecter code and any consumers that compare or construct OSDC-specific errors. `Objecter.h` includes it indirectly through error handling and completion interfaces.

## Risks and edge cases

The enum starts at 1 so zero remains success in the category implementation. Adding enum values requires updating `error_code.cc`; otherwise messages and conversions fall through to unknown handling. The header marks `is_error_condition_enum` false but still provides an explicit `make_error_condition()`, so generic comparison behavior relies on category methods rather than implicit condition conversion.

## Test signals

Compile-time tests should verify implicit conversion to `boost::system::error_code`. Runtime tests should check success remains zero, category identity is stable, and every enum value has the expected message/default condition/errno mapping.
