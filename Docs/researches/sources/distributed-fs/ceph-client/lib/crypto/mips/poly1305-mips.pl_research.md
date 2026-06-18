# sources/distributed-fs/ceph-client/lib/crypto/mips/poly1305-mips.pl

## Purpose
Perl generator for Cryptogams/OpenSSL-derived MIPS Poly1305 assembly. It emits 64-bit or 32-bit assembly variants for `poly1305_block_init`, `poly1305_blocks`, and `poly1305_emit`.

## Important APIs, Types, and Functions
- Input flavour argument selects `o32`, `n32`, `64`, `nubi32`, or `nubi64`; default is `64`.
- Under `__KERNEL__`, the generated `poly1305_init` symbol is renamed to `poly1305_block_init`.
- Generated functions implement block-state initialization, multi-block accumulation, and tag emission.
- The script emits MIPS R2/R6 differences, endian handling, aligned/unaligned load handling, saved-register masks, and ABI-specific register layouts.

## Control Flow and State
The script builds a `$code` string in two major branches: 64-bit for `64|n32` flavours and 32-bit otherwise. Both branches zero the hash state, clamp the key, precompute `s` multiples, loop over 16-byte blocks with modulo-scheduled reduction, store the accumulator, and emit final tags by reducing, selecting canonical residues, adding nonce, and serializing little-endian bytes. It writes to STDOUT or to a named output path.

## Dependencies and Integration Points
Integrated by the build system that runs the perl generator to create MIPS assembly used by `mips/poly1305.h` declarations and the generic Poly1305 dispatch. It depends on assembler support for MIPS32/MIPS64 R2/R6 variants and the expected kernel symbol names.

## Risks and Test Signals
Generator risks include ABI mismatches, endianness paths, R6 instruction substitutions, register save/restore errors, and divergence between generated symbol names and C declarations. Tests should include regenerating assembly for all intended flavours, building big- and little-endian MIPS configurations, RFC 8439 Poly1305 vectors, unaligned input/key tests, empty input, partial-final-block handling through the generic wrapper, and comparison to the C Donna backends.
