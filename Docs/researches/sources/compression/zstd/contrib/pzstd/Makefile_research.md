<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Makefile -->
# sources/compression/zstd/contrib/pzstd/Makefile

## Purpose
The pzstd Makefile builds the deprecated parallel zstd CLI, its object files, and its unit/integration tests against the local zstd library.

## Important APIs, Types, And Functions
Targets include the pzstd binary, object directories, clean/install/test variants, and test binaries for options, pzstd round trips, and utility classes. Variables control compiler, flags, library paths, thread support, and platform-specific settings.

## Control Flow
The Makefile compiles C++ sources under pzstd, links against zstd/common threading pieces, builds GoogleTest-style unit tests when available, and offers test targets that execute binaries.

## State And Persistence
It writes build artifacts, dependency files, binaries, and test outputs under build directories. No runtime state is persisted by the Makefile itself.

## Dependencies And Integration Points
It depends on make, a C++ compiler, zstd lib/common sources, platform libraries, and optional test infrastructure. It is the build integration point for all pzstd files in this subset.

## Risks
Pzstd is deprecated and uses deprecated zstd APIs. Platform flags, pthread linkage, and local library path assumptions are common portability risks.

## Test Signals
`make test`/related targets provide the strongest signal by building and running options, round-trip, pzstd, and utility tests.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Makefile -->
