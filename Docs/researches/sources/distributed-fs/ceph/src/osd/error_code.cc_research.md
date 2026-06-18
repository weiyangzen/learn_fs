# sources/distributed-fs/ceph/src/osd/error_code.cc

## Purpose
`error_code.cc` implements the Boost/Ceph error category for OSD-specific error codes. It gives custom OSD conditions human-readable messages, default conditions, POSIX-style equivalence, and conversion from negative Ceph return codes.

## Important APIs, Types, And Functions
The private `osd_error_category` derives from `ceph::converting_category`. It overrides `name()`, two `message()` overloads, `default_error_condition()`, `equivalent()`, and `from_code()`. Recognized `osd_errc` values are `old_snapc`, `blocklisted`, and `cmpext_mismatch`; unknown codes fall back to `cpp_strerror()`. `osd_category()` returns a function-local static category instance.

## Control Flow
When Boost asks for a message, the category maps known enum values to OSD-specific strings and otherwise formats the errno. `default_error_condition()` keeps known OSD values in the OSD category and maps everything else to `generic_category()`. `equivalent()` maps `old_snapc` to `invalid_argument`, `blocklisted` to `operation_not_permitted`, and `cmpext_mismatch` to `operation_canceled`; other values compare through the default condition. `from_code()` converts a positive category value to the negative return convention.

## State And Persistence Behavior
There is no persistence and only one static category object. Behavior must remain stable because error categories are used across APIs and tests that compare categories/conditions.

## Dependencies And Integration Points
The file depends on `common/error_code.h`, `common/errno.h`, and local `error_code.h`. It integrates OSD-specific errors with Boost.System and Ceph’s negative errno conventions.

## Risks And Test Signals
Risks include changing numeric equivalence, returning unstable message buffers, or misclassifying an OSD-specific error as generic. Tests should check `make_error_code()`, category name, messages for known/unknown values, default conditions, equivalence to Boost errc values, and negative conversion.
