<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy.c -->
# sources/distributed-fs/ceph-client/crypto/jitterentropy.c

Purpose: Contains the standalone CPU jitter entropy collector core, using timing variation, optional memory access noise, SHA3-256 conditioning, and SP800-90B health tests to produce random bytes.

Important APIs/types/functions: `struct rand_data` stores SHA3 pool state, previous timing deltas, oversampling rate, optional memory buffer, RCT/APT counters, and health failure bits. `jent_measure_jitter()` performs memory access, samples time, computes deltas, runs stuck/RCT/APT tests, and conditions the data. `jent_gen_entropy()` collects enough non-stuck measurements. `jent_read_entropy()` returns conditioned bytes and handles health failures. `jent_entropy_collector_alloc/free()` manage collector memory. `jent_entropy_init()` performs startup timer and health tests.

Control flow: Allocation optionally allocates a configured memory area, initializes oversampling and APT cutoff values, and primes the entropy pool. Generation primes `prev_time`, then loops until `(DATA_SIZE_BITS + safety_factor) * osr` good measurements are collected or a FIPS health failure appears. Read requests repeatedly generate a 256-bit block, check health status, extract bytes through the SHA3 conditioner, and return transient/permanent errors when needed. Startup initialization runs 1024 test measurements after cache-clearing iterations and rejects unavailable, coarse, or non-monotonic timers.

State and persistence behavior: Collector state persists across reads and includes sensitive hash/timing data. APT/RCT health state is retained, with intermittent bits reset during reinitialization and permanent bits preserved. Optional memory noise storage persists for the collector lifetime and is freed sensitively.

Dependencies and integration points: This file intentionally avoids normal optimized compilation and relies on hooks from `jitterentropy-kcapi.c` for timing, allocation, hashing, and output extraction. It reads `fips_enabled` to enable runtime health-test enforcement and extra safety-factor collection.

Risks: The file must be compiled with optimizations disabled, as enforced by `#ifdef __OPTIMIZE__`. Entropy assumptions are hardware/timer dependent and validated only by startup and health tests. FIPS mode changes runtime behavior and can cause permanent failures. Off-by-one errors in RCT/APT cutoffs or masking would affect compliance. The collector is stateful and must be externally serialized.

Test signals: Startup return codes for missing/coarse/nonmonotonic timers, RCT/APT induced failure tests, FIPS vs non-FIPS health behavior, statistical/raw-data collection through the test interface, memory-access enabled/disabled configurations, oversampling values, and repeated reads of non-block-sized output lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/jitterentropy.c -->
