<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/main_options.cc -->
# sources/distributed-fs/lizardfs/src/common/main_options.cc

## Purpose
Implements storage and lookup for extra `-o` style command-line options. The source was read completely for this report.

## Important APIs, Types, And Functions
Defines `gExtraArguments`, `main_get_extra_arguments`, and `main_has_extra_argument`.

## Control Flow
`main_has_extra_argument` optionally transforms the searched name and each option to lowercase, then scans for equality.

## State And Persistence Behavior
Process-global vector stores options for the lifetime of the process.

## Dependencies And Integration Points
Depends on `main.h` and `<algorithm>`; used by daemon/mount option logic.

## Risks And Edge Cases
The implementation lowercases when `mode == CaseSensitivity::kSensitive`, which appears inverted relative to the enum name and should be verified against `case_sensitivity.h` callers. It also passes `char` directly to `tolower`.

## Test Signals
No local unit tests are in this subset; add tests for mixed-case options and both enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/main_options.cc -->
