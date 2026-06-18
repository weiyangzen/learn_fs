# sources/distributed-fs/ceph/src/osdc/error_code.cc

## Purpose

`error_code.cc` implements the Boost.System error category for Objecter/OSDC-specific errors. It gives `osdc_errc` values names, human messages, default generic/Ceph conditions, equivalence rules, and conversion back to negative errno-style codes.

## Important APIs, types, and functions

`osdc_error_category` derives from `ceph::converting_category`. It implements `name()`, the char-buffer and string `message()` overloads, `default_error_condition()`, `equivalent()`, and `from_code()`. `osdc_category()` returns a function-local static category instance.

The handled errors are pool does-not-exist, pool exists, precondition violation, operation not supported, snapshot exists, snapshot does-not-exist, timeout, pool EIO, and handler failure.

## Control flow

Objecter code can return `make_error_code(osdc_errc::...)`. Boost.System dispatches category methods when code is formatted, compared to conditions, or converted by Ceph helpers. `default_error_condition()` maps objecter domain errors to `ceph::errc` or `boost::system::errc`, while `equivalent()` adds compatibility with standard conditions such as `no_such_file_or_directory` and `file_exists`. `from_code()` maps each category value to a negative errno used by legacy Ceph APIs.

## State and persistence behavior

The only state is the immutable singleton error category. No persistent state is involved.

## Dependencies and integration points

The file includes `common/error_code.h` and `osdc/error_code.h`. `Objecter.cc` uses these errors for pool DNE/EIO, pool/snapshot create/delete failures, operation precondition failures, timeouts, and reply handler failures. Callers using Boost.System can compare against both objecter-specific codes and generic conditions.

## Risks and edge cases

Every new `osdc_errc` must be added consistently to `message()`, `default_error_condition()`, `equivalent()` if needed, and `from_code()`. Unknown values return "Unknown error", a self condition, and `-EDOM`. The diagnostic pragmas suppress non-virtual destructor warnings around the category class; changing the base type may require revisiting them.

## Test signals

Tests should verify category name, messages, implicit `make_error_code()`, comparisons with generic conditions, `ceph::errc::not_in_map` equivalence for missing pools/snaps, errno conversion, and Objecter paths that surface `handler_failed` after callback exceptions.
