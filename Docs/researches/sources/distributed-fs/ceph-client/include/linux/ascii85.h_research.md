# sources/distributed-fs/ceph-client/include/linux/ascii85.h

## Purpose
Provides small inline helpers for ASCII85 length calculation and encoding of 32-bit words.

## Important APIs, Types, And Functions
`ASCII85_BUFSZ` is 6 bytes for five encoded characters plus terminator. `ascii85_encode_len(long len)` returns the number of 4-byte chunks rounded up. `ascii85_encode(u32 in, char *out)` returns `"z"` for a zero word or writes a five-character base-85 encoding plus NUL terminator into `out`.

## Control Flow, State, And Persistence
Encoding is stateless. For nonzero input, the loop fills output backward using modulo/divide by 85 and adds the ASCII offset `'!'`.

## Dependencies And Integration Points
Depends on `linux/math.h` for `DIV_ROUND_UP` and `linux/types.h` for `u32`. Used by kernel code that needs compact ASCII85 serialization.

## Risks And Test Signals
Callers must supply at least `ASCII85_BUFSZ` bytes for nonzero values and handle the zero special case returning a string literal rather than `out`. Tests should cover zero, maximum `u32`, round chunk length for unaligned byte counts, and buffer termination.
