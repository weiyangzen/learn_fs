# sources/compression/zlib/gzclose.c

## Purpose
`gzclose.c` provides the generic `gzclose()` dispatcher for zlib gzip file handles, kept in a separate translation unit so linkers can avoid pulling unused read or write close paths.

## Important APIs, Types, and Functions
The only exported function is `gzclose(gzFile file)`. It casts the opaque handle to `gz_statep`, checks for `NULL`, and dispatches to `gzclose_r()` for read mode or `gzclose_w()` for write mode when compression support is enabled.

## Control Flow, State, and Persistence
The function does not own close mechanics itself. It inspects `state->mode` and delegates cleanup, stream finalization, descriptor close, and error return semantics to the mode-specific implementation. With `NO_GZCOMPRESS`, it always calls the read close implementation.

## Dependencies and Integration Points
It includes `gzguts.h`, which defines `gz_statep`, mode constants, and internal close declarations. It is part of the public `gzFile` API implementation.

## Risks and Test Signals
The main risk is dispatching an invalid or corrupted `gzFile` state to the wrong close routine; the mode-specific close functions provide additional validation. Tests should cover closing read handles, write handles with pending compressed output, `NULL` handles returning `Z_STREAM_ERROR`, and builds with `NO_GZCOMPRESS`.
