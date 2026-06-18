<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/main.h -->
# sources/distributed-fs/lizardfs/src/common/main.h

## Purpose
Declares global extra command-line option storage and lookup helpers shared by daemon entry points. The source was read completely for this report.

## Important APIs, Types, And Functions
`gExtraArguments`, `main_get_extra_arguments`, and `main_has_extra_argument` are the visible API.

## Control Flow
No implementation in the header; callers retrieve the vector or test membership with optional case-sensitivity mode.

## State And Persistence Behavior
State is the process-global `std::vector<std::string> gExtraArguments`; no persistence.

## Dependencies And Integration Points
Depends on `case_sensitivity.h`; populated by main option parsing code.

## Risks And Edge Cases
Global mutable state is not synchronized. Semantics depend on the implementation matching the `CaseSensitivity` enum.

## Test Signals
Needs tests for case-sensitive and insensitive lookups and parsing integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/main.h -->
