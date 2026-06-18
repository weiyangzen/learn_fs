<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/bob_jenkins_rng.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/bob_jenkins_rng.h

## Purpose
Small deterministic pseudo-random generator used by crcutil tests to populate buffers and vary CRC inputs without external dependencies.

## Important APIs, Types, and Functions
Defines template specializations `crcutil::BobJenkinsRng<uint32>` and, when `HAVE_UINT64`, `crcutil::BobJenkinsRng<uint64>`. Each exposes `typedef value`, constructors, `Init(seed)`, and `Get()`. Non-MSVC builds define temporary `_rotl` and `_rotl64` rotation macros.

## Control Flow, State, and Persistence
`Init` seeds four internal words `a_`, `b_`, `c_`, and `d_` and discards 20 generated values to mix state. `Get` applies Bob Jenkins small PRNG rotations and additions, mutating all four state words and returning `d_`. State persists only inside each RNG object.

## Dependencies and Integration Points
Depends on crcutil `base_types.h` and platform feature macros. It is integrated by `unittest.h` for repeatable functionality and performance-test data generation.

## Risks and Test Signals
Risks are limited to deterministic test quality rather than cryptographic safety; rotation macros can evaluate arguments more than once if misused and 64-bit support is conditional. Test signals include stable sequences for fixed seeds, different sequences across seeds, 32-bit and 64-bit compilation paths, and no macro leakage after the header undefines non-MSVC rotation macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/bob_jenkins_rng.h -->
