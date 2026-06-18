# sources/distributed-fs/ceph-client/include/linux/rslib.h

## Purpose
`rslib.h` declares the kernel Reed-Solomon codec interface for 8-bit and 16-bit data streams.

## Important APIs, types, and functions
Core types are `struct rs_codec` and `struct rs_control`. APIs include optional `encode_rs8()`, `decode_rs8()`, `encode_rs16()`, `decode_rs16()`, `init_rs_gfp()`, inline `init_rs()`, `init_rs_non_canonical()`, `free_rs()`, and inline `rs_modnn()`.

## Control flow, state, and persistence
Callers initialize a codec by symbol size, primitive polynomial or generator function, first consecutive root, primitive element, and root count. The shared `rs_codec` holds Galois field tables, generator polynomial, users count, and list linkage; each `rs_control` carries codec pointer plus scratch buffers for decode. Encode/decode operations use caller data/parity buffers and optional erasure/correction arrays. State persists in allocated codec/control objects until `free_rs()`.

## Dependencies and integration points
It depends on kernel allocation flags and basic types, with encode/decode availability controlled by Reed-Solomon Kconfig symbols. Integration points include storage ECC, NAND/MTD, optical/media protocols, and other drivers needing systematic RS parity or correction.

## Risks and test signals
Risks include invalid primitive polynomials, symbol sizes beyond supported range, parity length mismatches, scratch-buffer lifetime errors, and using `rs_modnn()` outside its expected field range. Test signals include known-vector encode/decode tests, erasure correction, uncorrectable error reporting, non-canonical field initialization, refcounted codec reuse/free, and Kconfig combinations where only encode or decode is enabled.
