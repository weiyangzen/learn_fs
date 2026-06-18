# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-rbsp.h

## Purpose

`nal-rbsp.h` declares the shared RBSP cursor, operation table, and public bit/Exp-Golomb helper API used by codec-specific NAL parsers/generators.

## Important APIs, Types, And Symbols

- `struct nal_rbsp_ops` abstracts bit, fixed-width, unsigned Exp-Golomb, and signed Exp-Golomb operations.
- `struct rbsp` stores the data pointer, buffer size, current bit position, consecutive-zero count, ops table, and error state.
- External ops tables `write` and `read` select generator or parser behavior.
- Public functions include `rbsp_init()`, `rbsp_unsupported()`, `rbsp_bit()`, `rbsp_bits()`, `rbsp_uev()`, `rbsp_sev()`, and `rbsp_trailing_bits()`.

## Control Flow

Codec syntax walkers receive a `struct rbsp *` and call the public helpers in specification order. The selected ops table determines whether those calls read from a source buffer or write to a destination buffer, allowing one syntax walker to serve both directions.

## State And Persistence

State is caller-owned in the `struct rbsp` instance. The header does not allocate or persist data.

## Dependencies And Integration Points

This header depends on kernel integer types. It is included by H.264 and HEVC NAL helper C files and underpins Allegro parameter-set generation.

## Risks

Because `write` and `read` are exported as mutable global objects, code could accidentally modify operation callbacks. `rbsp_bits()` accepts an `int *` while the ops callback uses `unsigned int *`, which works with current callers but is type-fragile. Callers must check `rbsp.error` after syntax traversal.

## Test Signals

Compile tests catch callback signature drift. Functional tests should exercise the same codec syntax walker with both `read` and `write` ops to ensure the abstraction remains symmetric.
