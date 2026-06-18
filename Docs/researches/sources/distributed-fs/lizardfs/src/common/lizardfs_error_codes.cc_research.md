<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_error_codes.cc -->
# sources/distributed-fs/lizardfs/src/common/lizardfs_error_codes.cc

## Purpose
Maps LizardFS protocol/status error codes to stable human-readable strings. The source was read completely for this report.

## Important APIs, Types, And Functions
`lizardfs_error_string(uint8_t status)` indexes a static string table sized by `LIZARDFS_ERROR_MAX + 1` and clamps unknown codes to the max/unknown slot.

## Control Flow
The function is pure table lookup: normalize status, return `const char*`.

## State And Persistence Behavior
State is a static const string array; no persistence.

## Dependencies And Integration Points
Must stay synchronized with `lizardfs_error_codes.h`; used by read executors and other protocol error reporting paths.

## Risks And Edge Cases
Enum/table drift yields wrong messages. The max enum currently maps to an unknown string, so adding codes requires table and max updates together.

## Test Signals
Needs tests checking selected enum-to-string pairs and out-of-range clamping; no dedicated test in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_error_codes.cc -->
