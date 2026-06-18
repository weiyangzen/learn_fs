# sources/distributed-fs/lizardfs/src/mount/client/client_error_code.cc

## Purpose
`client_error_code.cc` implements the LizardFS `std::error_category`, including human-readable messages and equivalence with standard `std::errc` conditions.

## Important APIs, Types, And Functions
- `lizardfs_error_category::instance_` is the singleton category instance.
- `message(int)` delegates to `lizardfs_error_string`.
- `equivalent(int,const std::error_condition&)` maps LizardFS error enum values to standard conditions.
- `equivalent(const std::error_code&,int)` maps standard codes back to LizardFS conditions.

## Control Flow
Both equivalence functions first check exact/default equivalence, then switch over selected `lizardfs::error` values and compare with `std::errc` codes or conditions. Platform-specific mappings are used for `attribute_not_found` and `no_message` on Apple/FreeBSD versus other systems.

## State And Persistence
Only the static error category singleton is stored. No filesystem state is changed.

## Dependencies And Integration Points
It depends on `common/mfserr.h` for `lizardfs_error_string` and on `client_error_code.h` enum values. `client.cc` and C API wrappers use `make_error_code`.

## Risks
- Only selected LizardFS errors are mapped to standard conditions; callers comparing unmapped errors to `std::errc` will not match.
- Enum spelling mistakes in the header (`incorrecet_password`, `wating_for_completion`) become stable API names.

## Test Signals
Unit tests should check message text for representative codes and equivalence in both directions for each mapped `std::errc`, including platform-conditional `no_message` behavior.
