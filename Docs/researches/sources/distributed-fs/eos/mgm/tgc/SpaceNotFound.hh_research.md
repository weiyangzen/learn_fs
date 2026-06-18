# sources/distributed-fs/eos/mgm/tgc/SpaceNotFound.hh

## Purpose
`SpaceNotFound.hh` declares a typed runtime exception for missing EOS spaces in tape-GC code.

## Important APIs, Types, And Functions
The file declares `struct SpaceNotFound : std::runtime_error` with a string constructor.

## Control Flow
There is no behavior beyond exception construction.

## State And Persistence
No persistent state is owned beyond the inherited error message.

## Dependencies And Integration Points
It is used by `RealTapeGcMgm` and can be caught by callers handling configuration or FsView inconsistencies.

## Risks And Edge Cases
The file-level comment names `TapeAwareGcSpaceNotFound.hh`, which no longer matches the actual filename/type. The header itself does not include `mgm/Namespace.hh`, so it relies on namespace macros being visible from prior includes or build context; that can be fragile in isolation.

## Test Signals
Compile the header standalone where possible, and test missing-space throw/catch behavior in production adapter code.
