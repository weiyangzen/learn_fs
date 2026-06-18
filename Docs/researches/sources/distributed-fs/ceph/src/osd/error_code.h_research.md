# sources/distributed-fs/ceph/src/osd/error_code.h

## Purpose
`error_code.h` declares OSD-specific error codes and their Boost.System integration. It lets OSD code return typed errors while remaining compatible with Ceph’s mostly POSIX errno-based APIs.

## Important APIs, Types, And Functions
The header declares `osd_category()`, enum class `osd_errc`, Boost.System enum traits, and conversion helpers `make_error_code()` and `make_error_condition()`. `osd_errc` currently includes `old_snapc = 85`, `blocklisted = 108`, and `cmpext_mismatch = MAX_ERRNO`.

## Control Flow
Implicit conversion to `boost::system::error_code` is enabled by specializing `boost::system::is_error_code_enum`. `is_error_condition_enum` is false, so conditions are explicit through `make_error_condition()`. The inline conversion helpers attach the integer enum value to `osd_category()`.

## State And Persistence Behavior
There is no mutable state. The important persistence-like contract is numeric stability: these values may be visible in wire/API behavior and must remain compatible with existing error handling.

## Dependencies And Integration Points
The header depends on Boost.System, `include/rados.h`, and `include/err.h`. It is implemented by `error_code.cc` and consumed anywhere OSD-specific errors need typed Boost error codes.

## Risks And Test Signals
Risks include numeric collisions with POSIX/Ceph errno values, accidental condition conversion behavior, and changing values that external callers rely on. Tests should compile implicit `error_code` conversion, explicit condition conversion, and category/message/equivalence behavior through the implementation.
