# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-io-legacy.h

## Purpose
Declares the legacy I/O engine descriptor for the pluggable `gf_io` framework.

## APIs, Types, and Functions
Includes `gf-io.h` and exports `extern const gf_io_engine_t gf_io_engine_legacy`.

## Control Flow, State, and Persistence
The header has no state. At runtime engine selection can copy or reference `gf_io_engine_legacy` into the global `gf_io.engine` when legacy mode is chosen or when newer engines are unavailable.

## Dependencies and Integration
Depends entirely on `gf_io_engine_t` from `gf-io.h`. It integrates with engine selection, fallback behavior, and callback/async submission in the core I/O framework.

## Risks and Test Signals
Risks include legacy engine divergence from the common engine contract and fallback paths hiding io_uring initialization failures. Test signals include engine selection tests, legacy callback/async completion tests, shutdown/wait behavior, and parity checks against threaded/io_uring modes for supported operations.
