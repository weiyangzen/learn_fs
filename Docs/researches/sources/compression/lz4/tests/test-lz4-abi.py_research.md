# sources/compression/lz4/tests/test-lz4-abi.py

## Purpose
This Python harness verifies dynamic-library ABI compatibility between the current LZ4 tree and historical tagged `liblz4` releases from v1.7.5 onward. It builds libraries for `-m64` and `-m32`, then exercises mismatched compile-time and run-time library combinations with `tests/abiTest`.

## Important APIs and Control Flow
The helper functions `proc()`, `make()`, `git()`, `get_git_tags()`, and `sha1_of_file()` wrap subprocess execution, build invocation, tag discovery, and file hashing. Main flow clones the upstream repository into `tests/abiTests/lz4`, checks out release tags into per-tag directories, builds `liblz4`, builds the current `abiTest`, and runs it under `LD_LIBRARY_PATH` pointing at each tested library. It then rebuilds `abiTest` against older headers/libs and runs against the current shared library.

## State, Dependencies, and Integration
Persistent state lives under `tests/abiTests`, including cloned source and built libraries. The script depends on `git`, `make`, C compiler multilib support, `check_liblz4_version.sh`, and `abiTest`. It mutates cwd heavily and exits on first subprocess failure.

## Risks and Test Signals
The test is Linux-oriented because it assumes shared-library naming, `LD_LIBRARY_PATH`, and `-m32`/`-m64`; macOS is only warned about. It gives strong ABI regression signals for old/current interop and ASan-enabled out-of-bounds checks, but is slow, network-dependent on first clone, and brittle when tags or toolchains are unavailable.
