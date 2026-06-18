<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/validation.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/validation.cpp

## Purpose
Centralizes validation for configuration input fields.

## Important APIs, Types, And Functions
`Validation_IsValid` dispatches by `VALIDATION_TYPE`. `CheckAfsPartitionName` prepends `/vicep` and calls `cfg_HostPartitionNameValid`; other validators currently return true. `ShowError` displays validation failure text.

## Control Flow
The public function switches by validation type, receives an error resource ID, optionally shows an error, and returns validity. Partition validation allocates an ANSI name buffer and calls the AFS config library.

## State And Persistence
No persistent state; only optional modal error reporting.

## Dependencies And Integration Points
Uses AFS config APIs, `S2A`, app resource IDs, and message formatting.

## Risks And Edge Cases
Uses `delete` instead of `delete []`; allocation failure returns valid. `VALID_FILENAME` and `VALID_PATH` are declared elsewhere but not handled. Several validators are permissive stubs.

## Test Signals
Partition-name valid/invalid cases, allocation/error instrumentation, and enum coverage checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/validation.cpp -->
