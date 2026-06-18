# sources/distributed-fs/eos/mgm/tgc/MaxLenExceeded.hh

## Purpose
`MaxLenExceeded.hh` declares a typed runtime exception for tape-GC output-length violations.

## Important APIs, Types, And Functions
The file declares `struct MaxLenExceeded : std::runtime_error` with a string constructor.

## Control Flow
There is no behavior beyond typed exception construction.

## State And Persistence
No persistent state is owned beyond the inherited exception message.

## Dependencies And Integration Points
The type is shared by JSON-producing classes and FSCTL handling code so length failures can be distinguished from generic runtime errors.

## Risks And Edge Cases
Callers need to catch this specific type before broader `std::exception` when they want to return range-specific errors. The header includes EOS namespace macros and `<stdexcept>`.

## Test Signals
Compile tests and throw/catch tests are sufficient, plus integration tests for JSON maxLen paths.
