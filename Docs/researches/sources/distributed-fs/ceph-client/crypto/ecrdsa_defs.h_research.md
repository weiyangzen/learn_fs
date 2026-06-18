# sources/distributed-fs/ceph-client/crypto/ecrdsa_defs.h

## Purpose
`ecrdsa_defs.h` defines the EC-RDSA/GOST curve parameters used by `ecrdsa.c`. It covers 256-bit CryptoPro and TC26 parameter sets and 512-bit TC26 parameter sets.

## Important APIs, Types, And Functions
- Constants define generator x/y, prime `p`, order `n`, coefficient `a`, and coefficient `b` arrays for `gost_cp256a`, `gost_cp256b`, `gost_cp256c`, `gost_tc512a`, and `gost_tc512b`.
- Some primes include comments indicating special forms such as `2^256 - 617`, `2^255 + 3225`, `2^512 - 569`, and `2^511 + 111`.
- `cp256c_p` includes precomputed Barrett reduction data appended after the normal modulus limbs.

## Control Flow
There is no executable control flow. `ecrdsa.c` includes this header and maps OIDs to these static `struct ecc_curve` definitions.

## State And Persistence
All data is static curve metadata. Like `ecc_curve_defs.h`, arrays are mutable by type but treated as immutable constants.

## Dependencies And Integration Points
The file depends on `struct ecc_curve` from `<crypto/internal/ecc.h>`. The shared ECC reducer detects non-NIST special-prime shapes and Barrett parameters, so these constants interact directly with `vli_mmod_fast()` behavior in `ecc.c`.

## Risks And Edge Cases
Correct limb order and appended Barrett data are critical. Unsupported GOST OIDs in `ecrdsa.c` deliberately have no curve here. Any accidental mutation of non-const arrays would compromise signature verification. The 512-bit curves use 8 limbs and must stay within `ECRDSA_MAX_DIGITS`.

## Test Signals
EC-RDSA known-answer vectors validate these constants indirectly. Additional checks include verifying each generator lies on the curve, `nG` is infinity, and OID-to-curve mappings in `ecrdsa.c` select the expected parameter set.
