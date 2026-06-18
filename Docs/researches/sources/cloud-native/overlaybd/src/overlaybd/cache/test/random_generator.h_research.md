<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/test/random_generator.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/test/random_generator.h

## Purpose
Defines small deterministic random generators used by cache tests.

## Important APIs, Types, And Functions
`RandomValueGen<T>` is the abstract base. `UniformInt32RandomGen` wraps `std::mt19937` and inclusive `uniform_int_distribution<uint32_t>`, with `seed`. `UniformCharRandomGen` generates unsigned-char values.

## Control Flow
Tests construct generators with fixed default seed `1213`, then call `next()` to fill source data and choose random offsets/sizes.

## State And Persistence
State is in-memory PRNG engine and distribution object only.

## Dependencies And Integration Points
Used by `cache_test.cpp`; depends on C++ `<random>` and `<algorithm>`.

## Risks And Test Signals
Deterministic default seed is good for reproducibility. `UniformCharRandomGen::next` does not use `override` despite inheriting from `RandomValueGen<unsigned char>`, but the signature matches. Source size reviewed: 58 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/test/random_generator.h -->
