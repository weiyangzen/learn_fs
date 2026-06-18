# File Research: sources/block-storage/thin-provisioning-tools/src/random.rs

Implements deterministic test-data generation with a linear congruential generator. `Generator::fill_buffer` writes little-endian `u64` words seeded by caller and stepping with fixed `a`/`c` constants; `verify_buffer` replays the sequence and returns false on first mismatch.

Both methods require buffer length to be a multiple of eight. `Default` delegates to `new`.
