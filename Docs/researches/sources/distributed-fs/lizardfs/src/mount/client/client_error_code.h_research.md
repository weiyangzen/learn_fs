# sources/distributed-fs/lizardfs/src/mount/client/client_error_code.h

## Purpose
`client_error_code.h` declares the LizardFS C++ error enum and integrates it with `<system_error>`.

## Important APIs, Types, And Functions
- `enum class lizardfs::error` enumerates success and LizardFS-specific failures in protocol/status order.
- `detail::lizardfs_error_category` derives from `std::error_category`.
- `make_error_condition(error)`, `make_error_code(error)`, and `make_error_code(int)` construct category-bound condition/code values.
- `std::is_error_code_enum` and `std::is_error_condition_enum` specializations enable implicit system_error integration.

## Control Flow
Consumers convert integer status codes or enum values to `std::error_code` using the inline factories. Equivalence/message behavior is implemented in the `.cc`.

## State And Persistence
No runtime state beyond the category singleton declared in implementation.

## Dependencies And Integration Points
It is included by C++ client code and any external C++ consumer wanting typed LizardFS error handling.

## Risks
- The integer enum order must stay synchronized with common LizardFS error codes; inserting or reordering values can break ABI/behavior.
- Typos in public enumerator names are API-visible and hard to fix without compatibility impact.

## Test Signals
Compile-time tests should validate `std::is_error_code_enum<lizardfs::error>`, and runtime tests should compare integer status conversions against known LizardFS constants.
