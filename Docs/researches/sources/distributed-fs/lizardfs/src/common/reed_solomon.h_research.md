<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/reed_solomon.h -->
# sources/distributed-fs/lizardfs/src/common/reed_solomon.h

## Purpose
Implements templated Reed-Solomon encoding/recovery over GF(2^8), using ISA-L when available or the project Galois fallback. The source was read completely for this report.

## Important APIs, Types, And Functions
`ReedSolomon<MAXK,MAXM>`, matrix/table typedefs, `encode`, `recover`, `createRSMatrix`, `createEncodingMatrix`, `createRecoveryMatrix`, `selectRows`, `selectColumns`, and `matrixMultiply` are the important APIs.

## Control Flow
Construction creates an RS/Cauchy matrix for k,m. Encode selects parity rows and non-zero data columns, initializes GF tables, and computes parity. Recover selects available rows, inverts a decode matrix when needed, builds a recovery matrix for missing data/parity, caches GF tables by erased/needed/non-zero sets, and calls `ec_encode_data`.

## State And Persistence Behavior
State is cached GF tables, RS matrix, cached erased/needed/non-zero bitsets, and current k/m. No persistence.

## Dependencies And Integration Points
Used by erasure-coded chunk read/write paths; depends on ISA-L or `galois_field.h` and slice traits/tests.

## Risks And Edge Cases
The `gf_invert_matrix` failure path constructs `std::runtime_error` but does not throw it, so inversion failure would continue with invalid data. Assertions enforce counts and non-zero inputs only in debug builds.

## Test Signals
`reed_solomon_unittest.cc` covers parity encode/recover, zero inputs, benchmarks, and matrix invertibility across supported k/m combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/reed_solomon.h -->
