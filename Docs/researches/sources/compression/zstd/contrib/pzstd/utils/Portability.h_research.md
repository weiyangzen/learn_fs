<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Portability.h -->
# sources/compression/zstd/contrib/pzstd/utils/Portability.h

## Purpose
`Portability.h` provides small cross-platform definitions needed by pzstd.

## Important APIs, Types, And Functions
The file centralizes platform-specific includes or macros used by other utilities, keeping source files less cluttered.

## Control Flow
Behavior is compile-time conditional on platform macros.

## State And Persistence
No state is owned and nothing is persisted.

## Dependencies And Integration Points
It is included by `Pzstd.cpp` and utility code to normalize platform details around files and binary mode handling.

## Risks
Because it is small and broad, any macro change can affect multiple translation units. Platform coverage depends on build/test availability.

## Test Signals
Successful pzstd compilation on POSIX and Windows-like configurations validates this header.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Portability.h -->
