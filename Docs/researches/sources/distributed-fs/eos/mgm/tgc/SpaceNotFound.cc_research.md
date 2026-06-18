# sources/distributed-fs/eos/mgm/tgc/SpaceNotFound.cc

## Purpose
`SpaceNotFound.cc` implements the typed exception thrown when an EOS space cannot be found in tape-GC MGM operations.

## Important APIs, Types, And Functions
It defines `SpaceNotFound::SpaceNotFound(const std::string&)`.

## Control Flow
Construction forwards the message to `std::runtime_error`.

## State And Persistence
The exception stores only its message.

## Dependencies And Integration Points
`RealTapeGcMgm::getFsIdToSpaceMap()` throws this type when FsView lacks a requested space or stores a null space pointer. Higher-level code can distinguish missing-space conditions from generic runtime errors.

## Risks And Edge Cases
Some production methods return defaults for missing spaces instead of throwing `SpaceNotFound`, so callers should not rely on this exception for every absent-space path.

## Test Signals
Tests should throw/catch the type and cover missing/null FsView space paths in `RealTapeGcMgm`.
