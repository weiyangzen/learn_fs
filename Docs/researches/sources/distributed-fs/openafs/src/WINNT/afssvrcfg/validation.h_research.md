<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/validation.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/validation.h

## Purpose
Declares validation categories and the validation entry point.

## Important APIs, Types, And Functions
`VALIDATION_TYPE` covers AFS partition, cell, password, UID, server name, filename, and path. `Validation_IsValid` validates a `TCHAR*` input and can show an error.

## Control Flow
No runtime flow in the header.

## State And Persistence
No state declared.

## Dependencies And Integration Points
Used by configuration pages; implemented by `validation.cpp`.

## Risks And Edge Cases
The parameter name `bShowErorr` is misspelled. `VALID_FILENAME` and `VALID_PATH` lack implementation support.

## Test Signals
Compile/static-analysis enum coverage and call-site checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/validation.h -->
