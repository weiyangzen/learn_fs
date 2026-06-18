<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/macro-test.sh -->
# sources/compression/zstd/contrib/linux-kernel/test/macro-test.sh

## Purpose
This shell script validates macro hygiene for the linux-kernel zstd shim by compiling the imported module sources under multiple `ZSTD_DEPS_*` macro configurations.

## Important APIs, Types, And Functions
The script is organized around compiler invocations rather than exported functions. It builds preprocessor test cases for the dependency shim, include paths, and kernel-style replacement headers.

## Control Flow
It sets strict shell behavior, prepares compiler flags for the test include tree, and runs a sequence of compile/preprocess checks. A failing compiler command stops the script, making it suitable for make/CI use.

## State And Persistence
The only state is temporary compiler output or object/preprocessed files created by the commands. It does not persist runtime data.

## Dependencies And Integration Points
It depends on a POSIX shell, a C compiler, the linux-kernel test headers, and the zstd kernel-contrib source files. It integrates with the test Makefile lane for catching macro namespace regressions.

## Risks
The script is sensitive to compiler availability and exact include-path layout. It mostly verifies compilation, so semantic bugs can still pass.

## Test Signals
A zero exit status confirms that the selected macro combinations compile cleanly and that dependency feature gates in `zstd_deps.h` can be included without missing definitions.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/macro-test.sh -->
