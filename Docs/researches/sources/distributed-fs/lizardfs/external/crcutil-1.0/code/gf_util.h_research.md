# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/gf_util.h

## Purpose

`gf_util.h` implements finite-field polynomial arithmetic and CRC helper operations that are independent of a specific byte-processing algorithm. It is the mathematical foundation for table generation, CRC concatenation, zero-block CRCs, rolling-window correction tables, and storing CRC complements.

## Important APIs and functions

`GfUtil<Crc>` is parameterized by CRC value type. `Init(generating_polynomial, degree, canonical)` sets polynomial metadata, canonicalization mask, powers of x, normalization values, `crc_of_crc_`, and the inverse-like factor `x_pow_minus_W_`. Query methods include `GeneratingPolynomial()`, `Degree()`, `Canonize()`, and `One()`.

Core helpers include `ChangeStartValue()`, `Concatenate()`, `CrcOfZeroes()`, `StoreComplementaryCrc()`, `StoreCrc()`, `CrcOfCrc()`, `Multiply()`, `MultiplyUnnormalized()`, `XpowN()`, `Xpow8N()`, `Divide()`, and `FindLCD()`.

## Control flow, state, and persistence

State is per-instance and consists of canonicalization, powers table `x_pow_2n_`, polynomial, normalized one, inverse/correction values, and degree/byte counts. `Multiply()` performs carryless polynomial multiplication reduced by the configured generating polynomial. `XpowN()` exponentiates by square-and-multiply using precomputed `x_pow_2n_`. `FindLCD()` uses an extended Euclidean algorithm over GF(2) polynomials.

## Dependencies and integration points

It includes `base_types.h`, `crc_casts.h`, and `platform.h`. It is embedded inside `GenericCrc` and `Crc32cSSE4`, and is also used by rolling and protected CRC helpers. Its `MultiplyUnnormalized()` drives CRC table generation in both generic and SSE4 implementations.

## Risks and test signals

The code assumes valid degree and polynomial input; for example `degree - 1` is shifted during initialization. Incorrect polynomial metadata corrupts every derived table. `FindLCD()` and `Divide()` are subtle and should be validated with algebraic invariants. Test signals include CRC concatenation equivalence, `CrcOfZeroes` versus real zero buffers, `StoreComplementaryCrc` producing a requested final CRC, `StoreCrc` yielding `CrcOfCrc`, and randomized multiplication/distribution checks for supported CRC widths.
