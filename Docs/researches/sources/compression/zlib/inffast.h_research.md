# sources/compression/zlib/inffast.h

## Purpose
`inffast.h` is the private declaration header for the fast inflate decoder.

## Important APIs, Types, and Functions
It declares `void ZLIB_INTERNAL inflate_fast(z_streamp strm, unsigned start);`. The warning comment explicitly states that applications must not include it; public consumers should use `zlib.h`.

## Control Flow, State, and Persistence
The header has no runtime state. Its contract is implicit in `inffast.c`: callers provide a valid inflate stream in `LEN` mode with enough input/output headroom and an initialized table/window state.

## Dependencies and Integration Points
It relies on prior inclusion of zlib internal types and the `ZLIB_INTERNAL` visibility macro. It is included by `inflate.c` and `infback.c`.

## Risks and Test Signals
Risk is limited but important: signature drift would break both inflater frontends or assembler replacements. Compile tests across normal C and `ASMINF` configurations are the primary signal.
