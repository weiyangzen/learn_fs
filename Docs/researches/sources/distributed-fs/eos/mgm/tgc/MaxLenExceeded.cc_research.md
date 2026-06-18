# sources/distributed-fs/eos/mgm/tgc/MaxLenExceeded.cc

## Purpose
`MaxLenExceeded.cc` implements the exception thrown when a JSON or command-output length limit is exceeded.

## Important APIs, Types, And Functions
It defines `MaxLenExceeded::MaxLenExceeded(const std::string&)`.

## Control Flow
Construction forwards the message to `std::runtime_error`.

## State And Persistence
The exception stores only the runtime-error message and has no external state.

## Dependencies And Integration Points
It is thrown by `Lru::toJson()` and `SpaceToTapeGcMap::toJson()`, and handled by `MultiSpaceTapeGc::handleFSCTL_PLUGIO_tgc()` to return `ERANGE`.

## Risks And Edge Cases
Length-limited writers can intentionally overshoot before throwing, so callers must not assume a partially written stream is bounded after catching. The class itself is straightforward.

## Test Signals
Tests should check message preservation and that JSON callers map this exception to the expected error path.
