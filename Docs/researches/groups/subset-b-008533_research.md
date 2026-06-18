# subset-b-008533 Research

Grouped research report for the Pebble internal files assigned to `subset-b-008533`. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/uniform.go -->
# sources/storage-engines/pebble/internal/randvar/uniform.go

## Purpose
This file implements `randvar.Uniform`, a tiny random variable generator for inclusive uniform draws over a mutable integer range. It is used where Pebble tests or benchmarks need a distribution whose upper bound can grow over time without replacing the generator.

## Important APIs, Types, and Functions
`Uniform` stores an immutable `min uint64` and an atomically mutable `max`. `NewUniform(min, max)` initializes the generator and relies on the caller to preserve `min <= max`. `IncMax(delta)` atomically increases the upper bound. `Max()` reads the current bound. `Uint64(rng *rand.Rand)` returns `rng.Uint64N(Max()-min+1)+min`, so the range is inclusive at both ends.

## Control Flow and State
The control flow is direct: construction stores `max`, updates call `atomic.Uint64.Add`, and draws load `max` then call the supplied RNG. There is no persistence. The only shared state is `max`, made race-safe for concurrent increments and readers. The `rng` itself is supplied by the caller and is not protected by this type.

## Dependencies and Integration
The file depends on Go's `math/rand/v2` and `sync/atomic`. It follows the same `IncMax`, `Max`, and `Uint64` shape as `Zipf`, allowing test generators to switch between distributions.

## Risks and Edge Cases
The constructor does not validate `min <= max`; if violated, `Max()-min+1` underflows and produces an unintended wide range. `IncMax` can overflow `uint64` if abused. Passing a nil RNG will panic because this type does not call `ensureRand`, unlike `Weighted`.

## Test Signals
There is no direct test file for `Uniform` in this work item. Coverage is likely indirect through consumers. Useful missing tests would check inclusive endpoints, increasing `Max`, and invalid constructor behavior if the contract changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/uniform.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/weighted.go -->
# sources/storage-engines/pebble/internal/randvar/weighted.go

## Purpose
This file provides `randvar.Weighted`, a simple discrete weighted random generator over indexes `[0,len(weights)-1]`. It is intended for tests and workload generators that need categorical selection according to relative floating-point weights.

## Important APIs, Types, and Functions
`Weighted` holds an RNG, the precomputed sum of weights, and the original weight slice. `NewWeighted(rng, weights...)` computes the sum and replaces nil RNGs through package helper `ensureRand`. `Int()` draws a point `p` in `[0,sum)` and linearly scans weights until the cumulative bucket is found, returning the last index as a fallback for rounding.

## Control Flow and State
Construction is one pass over the weights. Every draw is another pass over the slice, subtracting each weight from `p`. The generator does not copy `weights`, so callers mutating the backing slice after construction can change draw behavior without updating `sum`. There is no persistence and no synchronization.

## Dependencies and Integration
The only direct external dependency is `math/rand/v2`; package-local `ensureRand` supplies a default RNG. It integrates with the rest of `internal/randvar` as a convenience distribution alongside Zipf, uniform, deck, and skewed-latest generators.

## Risks and Edge Cases
Zero and negative weights are not rejected. A zero weight can still be selected if `p <= weight` when `p` is exactly zero, although that is rare. Negative weights distort the subtraction logic. An empty `weights` slice causes `Int` to return `-1`. A zero total sum makes all draws use `p == 0` and typically returns the first non-negative bucket. None of these are guarded, so callers must provide sane weights.

## Test Signals
`weighted_test.go` creates a generator with weights `1,2,2,0,3` and draws 10,000 samples, only dumping output in verbose mode. It exercises construction and repeated draws but has no assertions about probabilities, zero-weight behavior, empty input, or invalid weights.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/weighted.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/weighted_test.go -->
# sources/storage-engines/pebble/internal/randvar/weighted_test.go

## Purpose
This test is a smoke test for the `Weighted` random variable generator. It ensures repeated calls to `Int` do not panic for a representative weight vector that includes a zero-weight index.

## Important APIs, Types, and Functions
`TestWeighted` calls `NewWeighted(nil, 1, 2, 2, 0, 3)`, draws 10,000 integers through `w.Int()`, and calls package test helper `dumpSamples` only when `testing.Verbose()` is true.

## Control Flow and State
The test relies on `NewWeighted` defaulting nil RNGs through `ensureRand`. It accumulates generated indexes into a local slice but does not inspect them unless verbose output is requested.

## Dependencies and Integration
It depends only on `testing` directly, plus package-local helpers. It is part of the broader `randvar` test suite and can be useful while manually inspecting distribution shape, but it is not a statistical validation.

## Risks and Gaps
Because there are no assertions, this test catches only panics and gross infinite-loop-style failures. It would not catch a biased distribution, zero-weight selection, empty input returning `-1`, or mutation of the weights slice after construction.

## Test Signals
The presence of the zero weight in the sample vector is a weak signal that zero weights are expected to be tolerated. There is no stable seed asserted in this file, so verbose output is diagnostic rather than golden.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/weighted_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/zipf.go -->
# sources/storage-engines/pebble/internal/randvar/zipf.go

## Purpose
This file implements an incrementally extensible Zipfian random variable generator derived from the YCSB-style "Incrementing Zipfian Random Number Generator." It supports `theta` values below 1, unlike Go's standard Zipf implementation, and can grow `max` without recomputing all hidden constants from scratch.

## Important APIs, Types, and Functions
`Zipf` stores immutable parameters `theta` and `min`, derived constants `alpha`, `zeta2`, and `halfPowTheta`, and mutable `max`, `eta`, and `zetaN` behind an embedded RW mutex. `NewDefaultZipf()` uses YCSB-like defaults. `NewZipf(min,max,theta)` validates `min <= max` and rejects `theta < 0` and `theta == 1`, computes zeta constants, and initializes `eta`. `IncMax(delta)` extends the support and updates `zetaN` incrementally. `Max()` reads the current max. `Uint64(rng)` samples the distribution using the cached constants. Helpers compute zeta from scratch or incrementally, including a precomputed default for the 10-billion-key default case.

## Control Flow and State
Construction computes `zeta2`, `halfPowTheta`, `zetaN`, `alpha`, and `eta` once. `IncMax` locks the mutable state, increments `max`, recomputes only the additional zeta terms, and refreshes `eta`. `Uint64` draws a uniform float, holds an RLock while reading mutable distribution constants, and maps the draw through the Zipf inversion formula. There is no disk persistence; the distribution state is memory resident and reproducible only through constructor parameters and mutation history.

## Dependencies and Integration
The file uses `math`, `math/rand/v2`, `sync`, and `github.com/cockroachdb/errors`. It integrates with Pebble workload/test random generators that need a growing key universe, especially YCSB-like workloads.

## Risks and Edge Cases
The error message says `0 < theta`, but the code allows `theta == 0`; that may be intentional for uniform-like behavior or a stale message. `Max()` uses an exclusive lock rather than an RLock, which is correct but less concurrent than necessary. `IncMax` does not guard overflow of `max`. `Uint64` requires non-nil RNG and trusts floating-point arithmetic; extreme parameters may be sensitive to precision. The default zeta shortcut is exact only for the known default tuple.

## Test Signals
`zipf_test.go` checks zeta values against known constants, verifies incremental `IncMax` matches constructor-computed state, accepts representative theta values below and above 1, and smoke-tests sampling. The tests do not assert sampled distribution frequencies, concurrency behavior, or boundary rejection for invalid parameters.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/zipf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/zipf_test.go -->
# sources/storage-engines/pebble/internal/randvar/zipf_test.go

## Purpose
This file tests the Zipf generator's zeta computations, incremental max extension, accepted parameter range, and basic sampling path.

## Important APIs, Types, and Functions
`TestZeta` verifies `computeZetaFromScratch` and `computeZetaIncrementally` against fixed expected values for theta `0.99`. `TestZetaIncMax` builds `[0,10]` by starting at `[0,0]` and calling `IncMax(1)` ten times, then compares `zetaN` and `eta` with a directly constructed `[0,10]` generator. `TestNewZipf` asserts construction succeeds for theta `0.99` and `1.01`. `TestZipf` draws 10,000 values and optionally dumps samples.

## Control Flow and State
The tests directly lock the generator internals for deterministic state comparison. Sampling is non-assertive and uses `NewRand`, a package helper outside this source list. No persistent state is involved.

## Dependencies and Integration
The file imports `math`, `testing`, and `testify/require`. It uses package-private functions and fields because it is in package `randvar`, making it able to validate internal cached constants.

## Risks and Gaps
The long zeta test for `n=100000000` is intentionally disabled because it is slow. Invalid parameter tests are missing for `min > max`, negative theta, and theta exactly one. Sampling tests do not check support bounds or statistical shape beyond avoiding panics.

## Test Signals
The strongest signal is that incremental zeta maintenance is intended to be exactly equivalent to recomputation for growing maxima. The accepted theta cases show sub-unity and super-unity theta values are supported.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/zipf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/rangedel/rangedel.go -->
# sources/storage-engines/pebble/internal/rangedel/rangedel.go

## Purpose
This file implements encoding, decoding, and point-iterator interleaving support for Pebble range deletion tombstones (`RANGEDEL`). Range deletions are represented as `keyspan.Span` values internally and as internal key/value pairs on disk.

## Important APIs, Types, and Functions
`Encode` emits one internal key/value pair per range deletion key in a span, requiring every key kind to be `InternalKeyKindRangeDelete`; it uses the span start as the internal user key and the span end as the value. `Decode` creates a span from one encoded key/value pair and appends to an optional key buffer. `DecodeIntoSpan` appends another key into an existing span after checking start and end consistency. `Interleave` wraps a point iterator and range deletion iterator in a pooled `keyspan.InterleavingIter`, returning both the iterator and a `TombstoneSpanGetter`; if no range deletion iterator exists, it returns the point iterator unchanged. `interleavingIter.Close` returns wrappers to a sync pool.

## Control Flow and State
Encoding loops over span keys and aborts on kind mismatch or emit error. Decoding is allocation-conscious through caller-provided key buffers. `DecodeIntoSpan` performs invariant-only start matching but always validates the end key because input can come from disk. Interleaving initializes a pooled wrapper with `InterleaveEndKeys: true`, making range deletion boundaries visible in the internal iteration stream. Persistent state is only the encoded key/value representation; runtime state is pooled and reset on close.

## Dependencies and Integration
The file depends on `base`, `invariants`, `keyspan`, and `sync`. It is an integration bridge between sstable/raw internal key encoding and the generic keyspan iterator machinery used by Pebble compactions and reads.

## Risks and Edge Cases
`Encode` rejects non-range-delete keys with a corruption error, protecting on-disk format generation. `Decode` aliases `ik.UserKey` and `v`, so callers must respect source buffer lifetimes. `DecodeIntoSpan` checks start only under invariants, so production builds rely on callers to group spans correctly. `Interleave` requires the returned iterator to be closed once to avoid pool misuse.

## Test Signals
No direct test file is included in this work item. Coverage likely comes from higher-level range deletion, sstable, and iterator tests. Useful targeted tests would validate corruption errors, buffer aliasing assumptions, and nil range-deletion iterator pass-through.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/rangedel/rangedel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/rangekey/coalesce.go -->
# sources/storage-engines/pebble/internal/rangekey/coalesce.go

## Purpose
This file resolves Pebble range-key semantics for a single fragmented span with common bounds. It removes range keys shadowed by newer sets, unsets, and deletes, optionally under a snapshot visibility cutoff, and supplies a specialized transformer for shared ingested sstables.

## Important APIs, Types, and Functions
`Coalesce(suffixCmp, keys, dst)` is the public wrapper that coalesces with all sequence numbers visible and sorts the result by internal trailer. `CoalesceInto(suffixCmp, dst, snapshot, keys)` performs the core work and returns keys sorted by suffix, with a trailing range-key delete appended if one is visible. `ForeignSSTTransformer` implements `keyspan.Transformer`, coalesces shared foreign sstable range keys, rewrites each key to a configured sequence number, and returns trailer-descending order.

## Control Flow and State
`CoalesceInto` first scans the trailer-descending input keys, skipping keys not visible at `snapshot` and stopping at the first visible `RANGEKEYDEL`, because it shadows lower sequence numbers. It appends visible set/unset keys before the delete into `dst`, stable-sorts them by suffix, and removes duplicate suffixes by keeping the first entry, which corresponds to the newest trailer due to the original ordering. If a delete was seen, it is appended after suffix coalescing. There is no persistent state; callers own buffers and key byte lifetimes. `ForeignSSTTransformer` reuses `sortBuf` to reduce allocations.

## Dependencies and Integration
The file depends on `base`, `invariants`, `keyspan`, `slices`, `math`, and Cockroach errors. It is central to range-key compactions, range-key user iteration, and ingestion of shared sstables. `rangekeystack.UserIteratorConfig.Transform` directly uses `CoalesceInto`.

## Risks and Edge Cases
The input must be sorted by trailer descending; invariant builds panic on disorder, production builds trust the caller. Comments describe sequence-number promotion, but a TODO notes the current implementation does not actually perform that promotion in `Coalesce`. Equal sequence numbers depend on Pebble's internal key-kind ordering: sets and unsets at the same sequence number do not shadow a delete at that same sequence number. The returned order differs between APIs, so callers must respect whether they receive suffix order or trailer order.

## Test Signals
`coalesce_test.go` is datadriven and compares parsed spans against `Coalesce` string output. It provides golden coverage for shadowing semantics but does not directly test `ForeignSSTTransformer` in this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/rangekey/coalesce.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/rangekey/coalesce_test.go -->
# sources/storage-engines/pebble/internal/rangekey/coalesce_test.go

## Purpose
This file provides datadriven tests for range-key coalescing, validating that range-key sets, unsets, and deletes resolve to the expected observable internal state.

## Important APIs, Types, and Functions
`TestCoalesce` runs `testdata/coalesce`. For each `coalesce` command, it parses a `keyspan.Span`, initializes an output span with the same bounds, calls `Coalesce(testkeys.Comparer.CompareRangeSuffixes, span.Keys, &coalesced.Keys)`, and returns the formatted span.

## Control Flow and State
Each datadriven command is independent. The test exercises parsing, coalescing, trailer sorting in the wrapper, and string formatting. It keeps no state between commands.

## Dependencies and Integration
The test depends on `datadriven`, `keyspan.ParseSpan`, and `testkeys.Comparer`. It ties coalescing semantics to Pebble's test range-suffix comparer.

## Risks and Gaps
The test only reaches the public `Coalesce` wrapper, so snapshot-filtered `CoalesceInto` behavior and `ForeignSSTTransformer` sequence rewriting need coverage elsewhere. The behavior under invariant panics for unsorted input is not directly asserted here.

## Test Signals
The datadriven fixture is the authoritative signal for expected shadowing behavior. Any coalescing change should update this fixture deliberately and consider user-iterator and compaction compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/rangekey/coalesce_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/rangekey/rangekey.go -->
# sources/storage-engines/pebble/internal/rangekey/rangekey.go

## Purpose
This file defines Pebble's physical encoding and decoding for range keys (`RANGEKEYSET`, `RANGEKEYUNSET`, and `RANGEKEYDEL`). It converts between `keyspan.Span` state and on-disk internal key/value tuples.

## Important APIs, Types, and Functions
`Encode` is a convenience wrapper around `Encoder`. `Encoder` stores an emit callback and reusable buffers for encoded values, set suffix/value tuples, and unset suffixes. `Encoder.Encode` groups span keys by sequence number and `flush` emits at most one physical set, unset, and delete key per sequence number. `Decode` decodes one physical internal key/value pair into a `keyspan.Span`. `DecodeIntoSpan` appends decoded logical keys into an existing span while checking span bounds. `SuffixValue` represents a logical suffix/value tuple. Encoding helpers compute and write value lengths for set and unset values. `DecodeEndKey` splits the range end key from the rest of a set/unset value and treats delete values as the end key directly. `IsRangeKey` classifies range-key kinds.

## Control Flow and State
`Encoder.Encode` walks the input keys in trailer-descending order, flushing accumulated sets/unsets/deletes whenever the sequence number changes. Sets encode a varstring end key followed by repeated varstring suffix and varstring value pairs. Unsets encode a varstring end key followed by repeated varstring suffixes. Deletes store the end key as the whole value and must have no trailing payload when decoded. The encoder reuses buffers but emits byte slices valid only until the callback returns. Decoding returns slices that alias the encoded value buffer. No state is persisted except the encoded internal keys in sstables.

## Dependencies and Integration
The file uses `encoding/binary`, `crencoding` for varint length sizing, and Pebble `base`, `invariants`, and `keyspan` packages. It is the on-disk contract consumed by sstable readers/writers, range-key merging, compactions, and user iteration.

## Risks and Edge Cases
`DecodeEndKey` requires set/unset values to contain both an end key and at least one byte of remaining payload; malformed or empty payloads return corruption errors. `decodeVarstring` does not explicitly bounds-check `n+int(l)` before slicing, so malformed length values can panic if caller code fails to guard; current tests focus on valid encodings. `DecodeIntoSpan` only checks start-key mismatch under invariants but always checks end-key mismatch. Encoder input is expected to be correctly ordered and contain only range-key kinds.

## Test Signals
`rangekey_test.go` round-trips set suffix/value encodings, set values, unset suffix encodings, unset values, and `IsRangeKey`. It does not exhaustively fuzz corrupt encodings or full `Encoder.Encode` grouping.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/rangekey/rangekey.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/rangekey/rangekey_test.go -->
# sources/storage-engines/pebble/internal/rangekey/rangekey_test.go

## Purpose
This file validates range-key encoding helpers for set and unset payloads and the range-key kind classifier.

## Important APIs, Types, and Functions
`TestSetSuffixValues_RoundTrip` round-trips raw repeated `SuffixValue` tuples. `TestSetValue_Roundtrip` verifies full `RANGEKEYSET` values including end-key prefixing. `TestUnsetSuffixes_RoundTrip` round-trips unset suffix lists. `TestUnsetValue_Roundtrip` verifies full `RANGEKEYUNSET` values. `TestIsRangeKey` checks classification for range key and point key kinds.

## Control Flow and State
The tests allocate or reuse a buffer sized by the corresponding encoded length helper, encode into it, decode by repeatedly consuming the rest slice, and compare against the original logical values. State is local to each test case.

## Dependencies and Integration
The file depends on Pebble `base` for key kinds and `testify/require` for assertions. It targets low-level encoding primitives that sstable range-key readers and writers depend on.

## Risks and Gaps
The tests cover valid round trips, not malformed varint lengths, corrupted end-key prefixes, delete payload validation, `Decode`/`DecodeIntoSpan`, or full sequence-number grouping in `Encoder.Encode`. `TestIsRangeKey` repeats `RangeKeyDelete` and omits `RangeKeySet` in the first three true cases, which weakens classifier coverage.

## Test Signals
The buffer reuse pattern confirms helpers are expected to write exactly the precomputed number of bytes. Empty suffixes and multiple suffix/value pairs are intentionally supported.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/rangekey/rangekey_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/rangekeystack/user_iterator.go -->
# sources/storage-engines/pebble/internal/rangekeystack/user_iterator.go

## Purpose
This file assembles and configures the range-key iterator stack used for Pebble user iteration. It merges range-key spans across LSM levels, applies range-key semantics and snapshot visibility, bounds iteration, defragments equivalent adjacent spans, and returns user-visible range-key state.

## Important APIs, Types, and Functions
`UserIteratorConfig` owns the iterator stack: `keyspanimpl.MergingIter`, `keyspan.BoundedIter`, `keyspan.DefragmentingIter`, reusable level iterators, snapshot and comparer state, and an `internalKeys` flag. `Buffers` exposes reusable merging, defragmenting, and sort buffers. `Init` wires together merging, bounding, and defragmentation over supplied fragment iterators. `AddLevel` appends another level to the merging iterator. `NewLevelIter` reuses a fixed array before allocating. `SetBounds` updates the bounded iterator. `Transform` implements `keyspan.Transformer`, coalescing by snapshot and either returning full internal keys or user-visible sets only. `ShouldDefragment` compares two transformed spans by suffix and value to determine whether they can be joined.

## Control Flow and State
`Init` sets configuration fields, initializes the merging iterator with `ui` as transformer, wraps it in a bounded iterator, and wraps that in a defragmenter. If `internalKeys` is true, defragmentation uses internal-key semantics and `Transform` preserves unsets/deletes sorted by trailer. Otherwise, `Transform` strips unsets and deletes after coalescing and sorts visible sets by suffix. `ShouldDefragment` assumes transformed suffix order and equal-length set lists, then compares suffixes with `CompareRangeSuffixes` and values with `bytes.Equal`. State is in-memory and designed for iterator reuse through `Buffers.PrepareForReuse`.

## Dependencies and Integration
The file depends on `base`, `invariants`, `keyspan`, `keyspanimpl`, `manifest`, and `rangekey`. It is the bridge between low-level LSM level iterators and Pebble's user-facing range-key iteration API, and shares coalescing semantics with compactions and ingestion.

## Risks and Edge Cases
Correctness depends on key ordering contracts: internal mode expects trailer-descending input; user mode expects suffix-sorted coalesced output. `Buffers` must be non-nil and suitable for reuse by one active stack at a time. The defragmenter ignores sequence numbers in user mode, which is correct for user-observable state but must not leak into internal-key use. Bounds and prefix pointers are passed through to `BoundedIter`, so caller-owned pointer lifetimes matter.

## Test Signals
`user_iterator_test.go` contains datadriven tests for merging/iteration and defragmentation, randomized equivalence tests between original and fragmented spans, and a transform benchmark. These tests exercise the stack under seek/next/prev operations and defragmentation behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/rangekeystack/user_iterator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/rangekeystack/user_iterator_test.go -->
# sources/storage-engines/pebble/internal/rangekeystack/user_iterator_test.go

## Purpose
This file tests the range-key user iterator stack, including merging semantics, defragmentation, randomized equivalence between fragmented and unfragmented inputs, and transform performance.

## Important APIs, Types, and Functions
`TestIter` uses datadriven `define` and `iter` commands over `keyspanimpl.MergingIter` with a coalescing transformer. `TestDefragmenting` drives `UserIteratorConfig.Init` against datadriven operations. `TestDefragmentingIter_Randomized` and `_FixedSeed` generate random range-key spans, fragment them, then compare iterator histories over random operations. Helpers include `fragment`, `debugContext`, and `runIterOp`. `BenchmarkTransform` measures `UserIteratorConfig.Transform` over varied key counts and suffix shadowing.

## Control Flow and State
Datadriven tests parse spans from text and execute explicit iteration commands. Randomized tests generate a keyspace, create original spans and deliberately fragmented equivalents, fragment both through `keyspan.Fragmenter`, initialize independent iterator stacks, run 100 random operations, and compare accumulated histories with diffs on failure. Benchmarks reuse `Buffers` and `UserIteratorConfig` between runs.

## Dependencies and Integration
The test imports `datadriven`, `keyspan`, `keyspanimpl`, `rangekey`, `testkeys`, `difflib`, and `testify/require`. It exercises integration between range-key coalescing, merging, bounds/defragmenting iteration, and test key comparers.

## Risks and Gaps
The randomized test uses time-based seeds for broad coverage and a fixed seed for reproducibility, but failures outside the fixed seed require captured logs. The benchmark uses internal-key mode for transform cost and does not assert allocations. Prefix-bound behavior is present in the config but not deeply highlighted in these tests.

## Test Signals
The core invariant is that a fragmented representation must iterate identically to the original after the stack merges and defragments it. The benchmark signals that transform performance under suffix shadowing is important.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/rangekeystack/user_iterator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/rate/rate.go -->
# sources/storage-engines/pebble/internal/rate/rate.go

## Purpose
This file wraps `github.com/cockroachdb/tokenbucket` to provide a thread-safe rate limiter for Pebble internal operations. It implements token-bucket waiting, debt, and dynamic rate updates.

## Important APIs, Types, and Functions
`Limiter` stores a token bucket, current rate, burst size, and optional sleep function under a mutex. `NewLimiter(r,b)` initializes a bucket with tokens per second and burst size. `NewLimiterWithCustomTime` also injects `nowFn` and `sleepFn` for deterministic testing. `Wait(n)` loops until `n` tokens can be fulfilled, sleeping for the token bucket's suggested delay. `Remove(n)` subtracts tokens without waiting and can create debt. `Rate()` returns the configured rate. `SetRate(r)` updates the token bucket rate while preserving burst.

## Control Flow and State
All token-bucket operations are protected by the mutex. `Wait` releases the lock before sleeping, then retries. The bucket starts full according to the external tokenbucket implementation. State is entirely in memory and not persisted.

## Dependencies and Integration
The file depends on `sync`, `time`, and CockroachDB's `tokenbucket` package. It is likely used by Pebble components that need internal throttling without exposing tokenbucket details.

## Risks and Edge Cases
`Wait` can sleep forever if the configured rate is zero or too low and the tokenbucket returns non-progressing delays. `SetRate` does not validate negative or zero inputs. `Remove` debt is intentional but can delay future operations substantially. The custom time path depends on caller-provided functions being coherent.

## Test Signals
No direct tests are included in this work item. The custom time constructor is a strong signal that deterministic tests exist or are intended elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/rate/rate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/rawalloc/rawalloc.go -->
# sources/storage-engines/pebble/internal/rawalloc/rawalloc.go

## Purpose
This file exposes `rawalloc.New`, a low-level byte slice allocator that returns uninitialized memory. It exists to avoid the zeroing cost of `make([]byte, len, cap)` where callers will overwrite the buffer before reading it.

## Important APIs, Types, and Functions
`New(len, cap int) []byte` calls runtime `mallocgc(uintptr(cap), nil, false)` and converts the returned pointer into a byte slice of capacity `cap` and length `len` using `unsafe.Slice`.

## Control Flow and State
Allocation is a single runtime call. There is no package state or persistence. The returned memory is managed by the Go runtime but is explicitly not zero-initialized.

## Dependencies and Integration
The file depends on `unsafe` and a platform/build-specific `mallocgc` declaration supplied by sibling files. It is an internal performance primitive and should only be used by callers that can guarantee full initialization before reads.

## Risks and Edge Cases
This is inherently unsafe. Reading unwritten bytes can expose stale heap contents and cause nondeterministic behavior. The function does not validate `len <= cap`; slicing `[:len]` will panic if violated. It relies on Go runtime internals whose signatures and linkability can change.

## Test Signals
`rawalloc_test.go` contains only benchmarks comparing this allocator with `make`, not correctness tests. The absence of functional tests reflects that correctness relies on careful caller discipline.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/rawalloc/rawalloc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/rawalloc/rawalloc_gccgo.go -->
# sources/storage-engines/pebble/internal/rawalloc/rawalloc_gccgo.go

## Purpose
This build-tagged file declares the runtime allocation hook for gccgo builds, allowing `rawalloc.New` to call `runtime.mallocgc`.

## Important APIs, Types, and Functions
Under `//go:build gccgo`, it declares `//extern runtime.mallocgc` and `func mallocgc(size uintptr, typ unsafe.Pointer, needzero bool) unsafe.Pointer`.

## Control Flow and State
There is no executable control flow in this file beyond the external symbol declaration. Runtime state is delegated to gccgo's runtime.

## Dependencies and Integration
It imports `unsafe` and is selected only for gccgo builds. It supplies the same `mallocgc` symbol expected by `rawalloc.go`, preserving source compatibility with the gc implementation.

## Risks and Edge Cases
This relies on gccgo runtime internals and the exact symbol/signature. If the runtime changes, builds or allocation semantics may break. The `needzero=false` argument is passed by callers through `rawalloc.New`, so the same uninitialized-memory risks apply.

## Test Signals
No direct tests target gccgo selection here. Build coverage under gccgo would be required to validate this path.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/rawalloc/rawalloc_gccgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/rawalloc/rawalloc_go1.9.go -->
# sources/storage-engines/pebble/internal/rawalloc/rawalloc_go1.9.go

## Purpose
This build-tagged file declares the runtime allocation hook for standard gc Go builds at Go 1.9 and later, allowing `rawalloc.New` to allocate unzeroed memory.

## Important APIs, Types, and Functions
Under `//go:build gc && go1.9`, it uses `//go:linkname mallocgc runtime.mallocgc` to bind a local `mallocgc(size uintptr, typ unsafe.Pointer, needzero bool) unsafe.Pointer` declaration to the private runtime function.

## Control Flow and State
There is no ordinary control flow. The file creates a link-time binding to a runtime implementation that `rawalloc.go` calls.

## Dependencies and Integration
It imports `unsafe` and uses the `go:linkname` compiler directive. It is tightly coupled to the Go runtime and selected for the usual gc toolchain.

## Risks and Edge Cases
`go:linkname` bypasses package encapsulation and is version-sensitive. The comment acknowledges that this is tied to Go release behavior. Runtime signature changes would produce build or runtime failures. It also participates in the uninitialized-memory risk of `rawalloc.New`.

## Test Signals
Only benchmark coverage appears in the listed tests. Build success under the configured Go toolchain is the primary signal that the linkname still resolves.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/rawalloc/rawalloc_go1.9.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/rawalloc/rawalloc_test.go -->
# sources/storage-engines/pebble/internal/rawalloc/rawalloc_test.go

## Purpose
This file benchmarks uninitialized allocation against ordinary zeroed `make` allocation across several buffer sizes.

## Important APIs, Types, and Functions
`sizes` lists buffer sizes from 16 bytes through 1 MiB. `BenchmarkRawalloc` calls `New(size,size)` in a loop. `BenchmarkMake` calls `make([]byte,size)` in a loop.

## Control Flow and State
Each benchmark iterates over sizes and creates a sub-benchmark per size. Allocated slices are discarded immediately, so the benchmark primarily measures allocation and zeroing overhead as seen by the compiler/runtime.

## Dependencies and Integration
The file uses `fmt` and `testing`. It provides performance evidence for the risky `rawalloc` implementation.

## Risks and Gaps
The benchmarks do not prevent compiler/runtime optimizations beyond assigning to blank identifier, so results should be interpreted carefully. There are no tests that verify length/capacity, GC safety, or expected non-zero contents.

## Test Signals
The size range signals that raw allocation is intended to help with medium-to-large scratch buffers, not only tiny allocations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/rawalloc/rawalloc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/sstableinternal/options.go -->
# sources/storage-engines/pebble/internal/sstableinternal/options.go

## Purpose
This file defines internal-only option structs shared with Pebble sstable readers and writers. It carries cache integration and test-only key-order-check disabling through package boundaries that external users cannot set directly.

## Important APIs, Types, and Functions
`CacheOptions` contains an optional `*cache.Handle` and the `base.DiskFileNum` needed for cache identity. `ReaderOptions` currently embeds `CacheOpts`. `WriterOptions` embeds `CacheOpts` and adds `DisableKeyOrderChecks`, intended only for constructing invalid test sstables.

## Control Flow and State
There is no control flow. The structs transport configuration into sstable internals. Cache state itself is owned by `cache.Handle`, not this package.

## Dependencies and Integration
The file depends on Pebble `base` and `cache`. It creates an internal extension point for the public `sstable.ReaderOptions` and `sstable.WriterOptions` without exposing fields outside Pebble.

## Risks and Edge Cases
When `CacheHandle` is non-nil, `FileNum` must be set consistently; the struct comments state this but the type does not enforce it. `DisableKeyOrderChecks` is dangerous outside controlled tests because it permits invalid table construction.

## Test Signals
No direct tests are included. Validation occurs through sstable reader/writer tests and test tooling that creates malformed sstables.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/sstableinternal/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/strparse/strparse.go -->
# sources/storage-engines/pebble/internal/strparse/strparse.go

## Purpose
This package implements a panic-on-error token parser for test and debug string formats. It is intended for parsers such as manifest debug parsing that recover panics and convert them to errors.

## Important APIs, Types, and Functions
`Parser` stores the original input, remaining tokens, and last token for diagnostics. `MakeParser(separators,input)` splits input by whitespace and caller-specified separator runes, preserving byte offsets. Basic methods include `Done`, `Offset`, `Peek`, `Next`, `ExpectAll`, `Remaining`, and `Expect`. Domain parsers include `TryLevel`, `Level`, `Int`, `Uint64`, `Uint32`, `SeqNum`, `HashSeqNum`, `SeqNumRange`, `BlobFileID`, `FileNum`, `DiskFileNum`, `InternalKey`, and `UserKeyBounds`. `BracketedRange` collects a bracketed interval string. `Errf` panics with an annotated Cockroach error.

## Control Flow and State
Tokenization scans the input string, skipping whitespace, emitting single-character separators, and emitting non-whitespace token runs up to the next whitespace or separator. Parser methods consume tokens by reslicing `p.tokens`; `Peek` updates `lastToken` even without consuming. Parse failures call `Errf`, so callers must recover if they want ordinary error returns. There is no persistence.

## Dependencies and Integration
The package uses `regexp`, `strconv`, `strings`, `unicode`, Cockroach errors, and Pebble `base` parsing types. It is used by datadriven tests and debug parsers, including `tombspan_test.go` in this work item.

## Risks and Edge Cases
Because methods panic, direct use in production paths would be risky unless recovered. `TryLevel` compiles its regexp on each call, which is fine for tests but inefficient. `BracketedRange` does not explicitly error if the closing bracket is absent; it returns the accumulated string. Offset tracking is byte-based, not rune-index-based, which is typical for Go strings but important for Unicode input.

## Test Signals
`strparse_test.go` validates token offsets, robust `HashSeqNum` diagnostics, and malformed sequence-number ranges. The tests specifically guard against out-of-bounds panics escaping from lower-level sequence parsing.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/strparse/strparse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/strparse/strparse_test.go -->
# sources/storage-engines/pebble/internal/strparse/strparse_test.go

## Purpose
This file tests tokenization offsets and error quality for sequence-number parsing helpers.

## Important APIs, Types, and Functions
`TestParserOffsets` checks `MakeParser` output tokens and offsets for whitespace and separator combinations. `TestHashSeqNum` verifies a valid `#42` parse and invalid cases for missing prefix, empty number, and wrong token. `TestSeqNumRangeMalformed` verifies malformed ranges produce `Errf`-formatted errors rather than low-level panics.

## Control Flow and State
The invalid tests use deferred `recover` and assert that the recovered value is an error containing expected context. Parser state is local to each subtest.

## Dependencies and Integration
The test imports `strings`, `testing`, Pebble `base`, and `testify/require`. It targets the parser's role as a debug/test utility that must produce clear errors for malformed datadriven input.

## Risks and Gaps
The tests do not cover `BracketedRange` missing-close behavior, level parsing variants, blob/file number parsing, or Unicode offset semantics. They focus on recently fragile error paths.

## Test Signals
The strongest signal is that parser panics should be recoverable `error` values with the original input embedded in the message.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/strparse/strparse_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/testkeys/strconv.go -->
# sources/storage-engines/pebble/internal/testkeys/strconv.go

## Purpose
This file provides an allocation-avoiding `[]byte` variant of `strconv.ParseUint` for the `testkeys` package. It is copied from go4.org/strconv and is used when parsing timestamp suffixes out of byte slices.

## Important APIs, Types, and Functions
`parseUintBytes(s, base, bitSize)` supports base validation, base auto-detection for `0`, `0x`, and leading-zero octal, digit scanning, overflow checks, and returns `*strconv.NumError` on failure. `cutoff64(base)` computes the overflow threshold for multiplication.

## Control Flow and State
The parser validates inputs, determines base, iterates over bytes, maps ASCII digits and letters to values, checks value range and overflow, and returns parsed `uint64`. It uses `goto Error` to share construction of `NumError`. There is no persistent state.

## Dependencies and Integration
It depends on `strconv` and Cockroach errors. `testkeys.Compare` and validation use it through timestamp suffix parsing to avoid converting suffix byte slices into strings in hot test paths.

## Risks and Edge Cases
The function intentionally mirrors older strconv behavior and must stay compatible with expected `NumError` semantics. It handles ASCII digits only. Overflow behavior sets `n` to max uint64 before returning range error, matching standard library style.

## Test Signals
There is no direct test for this file, but `testkeys_test.go` exercises suffix comparison and comparer validation, indirectly covering successful decimal parses and invalid-key validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/testkeys/strconv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/testkeys/testkeys.go -->
# sources/storage-engines/pebble/internal/testkeys/testkeys.go

## Purpose
This package provides deterministic, human-readable key generation and comparison utilities for Pebble tests and benchmarks. It models keys with optional MVCC-like timestamp suffixes (`@<integer>`) and offers finite keyspaces, slicing, striding, random prefix generation, and test KV metadata extraction.

## Important APIs, Types, and Functions
`Comparer` is a Pebble `base.Comparer` that compares unsuffixed prefixes lexicographically and timestamp suffixes in descending numeric order; it also supplies separator, successor, immediate successor, split, validation, and suffix comparison hooks. `Keyspace` abstracts finite key generators with `Count`, `MaxLen`, and `key`. Public helpers include `Alpha`, `Divvy`, `Slice`, `EveryN`, `Key`, `KeyAt`, `WriteKey`, `WriteKeyAt`, `Suffix`, `SuffixLen`, `ParseSuffix`, `WriteSuffix`, `RandomPrefixInRange`, and `ExtractKVMeta`. Internal helpers implement alphabet key enumeration and inverse indexing.

## Control Flow and State
The comparer splits keys at the last `@`. Prefixes compare bytewise; suffixes parse numeric timestamps and reverse the ordering so larger timestamps sort earlier. Point suffix comparison ignores the `_synthetic` suffix while range suffix comparison uses it as a tiebreaker. Alphabet keyspaces enumerate variable-length strings from `a` to `z` in a deterministic tree order. `RandomPrefixInRange` validates bounds, trims common prefixes, maps bounds into an alphabet index range, and samples a prefix with assertions that the result lies in `[a,b)`. State is mostly immutable; the package-level inverse alphabet map is populated in `init`.

## Dependencies and Integration
The package depends on `base`, `math/rand/v2`, `regexp`, `strconv`, `strings`, and Cockroach errors. It is widely integrated into Pebble internal tests, datadriven fixtures, range-key tests, and manifest parsing tests as a consistent comparer and key generator.

## Risks and Edge Cases
`keyCount` panics on overflow, and comments note `RandomPrefixInRange` uses max lengths below the overflow region. `ImmediateSuccessor` panics if called with a suffixed key. Invalid suffixes panic in compare paths, so tests must validate keys when needed. `Slice` rejects `i >= Count`, which means an empty slice at the end is not allowed. `_synthetic` suffix handling deliberately differs between point and range suffix comparison, so changes can violate comparer contracts.

## Test Signals
`testkeys_test.go` covers key generation, inverse indexing, counts, full keyspaces, slicing, suffix ordering, suffix length, divvying, random prefix generation including randomized insertion, overflow panic, comparer checks, synthetic suffix behavior, and tiering metadata extraction.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/testkeys/testkeys.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/testkeys/testkeys_test.go -->
# sources/storage-engines/pebble/internal/testkeys/testkeys_test.go

## Purpose
This file validates the `testkeys` package's deterministic keyspace generation, comparer behavior, suffix handling, random prefix generation, and KV metadata parsing.

## Important APIs, Types, and Functions
Tests include `TestGenerateAlphabetKey`, `TestKeyCount`, `TestFullKeyspaces`, `TestSlice`, `TestSuffix`, `TestSuffixLen`, `TestDivvy`, `TestRandomPrefixInRange`, `TestOverflowPanic`, `TestComparer`, `TestIgnorableSuffix`, and `TestExtractKVMeta`. `keyspaceToString` formats keyspaces for comparisons.

## Control Flow and State
Most tests are table-driven. `TestDivvy` uses datadriven fixtures. `TestRandomPrefixInRange` performs both fixed scenario sampling and a randomized insertion process that keeps a sorted key list and verifies each generated prefix fits between selected bounds. `TestOverflowPanic` intentionally recovers from a panic.

## Dependencies and Integration
The file depends on `datadriven`, Pebble `base`, `testify/require`, and `math/rand/v2`. It anchors test-key semantics used throughout many Pebble tests.

## Risks and Gaps
Randomized prefix generation is deterministic due to fixed PCG seed, but it is still sample-based. The tests do not cover every invalid key validation path or every comparer callback under all suffix/prefix combinations.

## Test Signals
The comparer is checked through `base.CheckComparer`, giving high confidence that testkeys obey Pebble comparer invariants. The `_synthetic` tests explicitly document point-vs-range suffix divergence.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/testkeys/testkeys_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/testutils/duration.go -->
# sources/storage-engines/pebble/internal/testutils/duration.go

## Purpose
This file provides a test assertion helper for durations while accounting for coarse Windows timer precision.

## Important APIs, Types, and Functions
`DurationIsAtLeast(t, d, minValue)` marks itself as a helper, skips strict checking on Windows when the minimum is below 10ms, and otherwise asserts `d >= minValue` with `require.GreaterOrEqual`.

## Control Flow and State
The function is stateless. It has one platform-specific early return and one assertion path.

## Dependencies and Integration
It depends on `runtime`, `testing`, `time`, and `testify/require`. It is meant for tests that measure sleeps, waits, or rate-limited operations.

## Risks and Edge Cases
The Windows special case can mask short-duration regressions on that platform, but avoids flakes from timer granularity. It does not check upper bounds.

## Test Signals
No direct tests are included. The helper's behavior is normally validated indirectly by tests that would otherwise be flaky.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/testutils/duration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/testutils/errors.go -->
# sources/storage-engines/pebble/internal/testutils/errors.go

## Purpose
This file provides generic helpers that simplify tests where returned errors are expected to be nil.

## Important APIs, Types, and Functions
`CheckErr[V](v, err)` returns `v` or panics on `err`. `CheckErr2[V,W](v,w,err)` returns two values or panics on `err`.

## Control Flow and State
Both helpers are stateless and branch only on whether `err` is nil. They panic rather than fail a `testing.T`, so they are most useful in setup expressions or where the caller wants panic-based simplification.

## Dependencies and Integration
There are no imports. The helpers are generic and can wrap arbitrary functions returning one or two values plus error.

## Risks and Edge Cases
Panics do not automatically mark helper stack frames or produce `require`-style test messages. They should not be used when a test needs precise failure attribution or error matching.

## Test Signals
No direct tests are included. The code is simple, and coverage is indirect through tests that use these helpers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/testutils/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/testutils/indenttree/indent_tree.go -->
# sources/storage-engines/pebble/internal/testutils/indenttree/indent_tree.go

## Purpose
This package parses indentation-based text into a forest of nodes for test inputs. It provides a compact way to express hierarchies in datadriven fixtures.

## Important APIs, Types, and Functions
`Parse(input)` returns `[]Node` or an error. It validates non-empty input, rejects empty lines and tab indentation, computes the distinct indentation levels, and recursively constructs nodes. `Node` stores a line value and children. `Value()` and `Children()` expose those fields.

## Control Flow and State
`Parse` trims one trailing newline, splits lines, records leading-space counts, sorts and compacts indentation levels, then recursively partitions ranges of lines into sibling and child regions. Indentation must be consistent with discovered levels, and skipped levels cause an error. There is no persistent state.

## Dependencies and Integration
It uses `slices`, `strings`, and Cockroach errors. The test file renders parsed nodes through `treeprinter`, so this parser integrates with Pebble's textual tree debugging tools.

## Risks and Edge Cases
The leading-space loop uses `line[level:]` while incrementing `level`; because it checks empty lines after the loop, all-space lines are handled as errors. Tabs anywhere at the first non-space indentation position are rejected. The parser treats all distinct indentation widths as levels, so accidental inconsistent sibling indentation fails during recursion.

## Test Signals
`indent_tree_test.go` uses datadriven fixtures to parse inputs and render the result, including error cases from invalid indentation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/testutils/indenttree/indent_tree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/testutils/indenttree/indent_tree_test.go -->
# sources/storage-engines/pebble/internal/testutils/indenttree/indent_tree_test.go

## Purpose
This file provides datadriven tests for the indentation tree parser, formatting successful parses as explicit trees and returning parser errors for invalid inputs.

## Important APIs, Types, and Functions
`TestIndentTree` runs over `testdata`. For `parse` commands, it calls `Parse`, then recursively walks returned nodes and renders them under a `<root>` node with `treeprinter.New`.

## Control Flow and State
Each datadriven command is independent. On parse error, the test returns an `error: ...` string for golden comparison. On success, it performs DFS over parsed nodes.

## Dependencies and Integration
The test imports `datadriven` and `treeprinter`. It validates both parser structure and its compatibility with the tree printer.

## Risks and Gaps
The test depends on fixture breadth. It does not expose internal indentation level arrays or offsets, only observable parse tree and error text.

## Test Signals
Golden tree output is the main signal that indentation nesting and sibling detection remain stable.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/testutils/indenttree/indent_tree_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/testutils/logger.go -->
# sources/storage-engines/pebble/internal/testutils/logger.go

## Purpose
This file adapts `testing.TB` to a logger-like interface for tests.

## Important APIs, Types, and Functions
`Logger` stores `T testing.TB`. `Infof` and `Errorf` forward to `T.Logf`. `Fatalf` marks itself as helper and forwards to `T.Fatalf`.

## Control Flow and State
All methods are direct delegation. The only state is the wrapped test handle.

## Dependencies and Integration
It depends on `testing`. It is useful for code under test that accepts a logger interface while tests want log output attached to the running test.

## Risks and Edge Cases
`Errorf` logs rather than failing the test, so callers expecting error-level logs to fail must use a different adapter. `Logger` assumes `T` is non-nil.

## Test Signals
No direct tests are included. Behavior is simple and normally validated by consumers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/testutils/logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/testutils/reflect.go -->
# sources/storage-engines/pebble/internal/testutils/reflect.go

## Purpose
This file provides a reflection helper to detect whether a Go type contains any pointers. It is useful in tests that verify memory layout or allocation-safety assumptions.

## Important APIs, Types, and Functions
`AnyPointers(typ reflect.Type)` returns true for pointer-containing kinds, false for scalar no-pointer kinds, and recursively examines struct fields and array elements. `kindPointers` maps `reflect.Kind` values to `kindNoPointer`, `kindHasPointer`, or `kindMaybeHasPointer`.

## Control Flow and State
The function first checks the kind lookup table. Structs recurse over all fields, arrays recurse over their element type, and unexpected maybe-kind values panic. The lookup table is package-level immutable state.

## Dependencies and Integration
It depends on `reflect` and Cockroach errors. It can support tests for cache/block layout, unsafe structures, or raw allocation assumptions.

## Risks and Edge Cases
The table must stay in sync with Go's `reflect.Kind` enumeration. If new kinds are added beyond the table length, indexing could panic. Struct recursion includes unexported fields because only types are examined. It treats strings, slices, maps, chans, funcs, interfaces, pointers, and unsafe pointers as pointer-containing.

## Test Signals
No direct tests are listed. Callers should add coverage if relying on it for critical layout gates.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/testutils/reflect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/testutils/rng.go -->
# sources/storage-engines/pebble/internal/testutils/rng.go

## Purpose
This file provides small random data helpers for tests.

## Important APIs, Types, and Functions
`RandIntInRange(r,min,max)` returns an integer in `[min,max)`. `RandBytes(r,size)` returns a byte slice of the requested length filled with random ASCII letters from `a-zA-Z`, or nil for non-positive sizes.

## Control Flow and State
`RandIntInRange` delegates to `r.IntN(max-min)`. `RandBytes` allocates a slice, fills each byte by sampling from `randLetters`, and returns it. `randLetters` is package-level constant data.

## Dependencies and Integration
It depends on `math/rand/v2`. These helpers are useful for randomized tests that need deterministic behavior through caller-supplied RNGs.

## Risks and Edge Cases
`RandIntInRange` panics if `max <= min` because `IntN` receives a non-positive argument. `RandBytes` returns nil rather than an empty non-nil slice for `size <= 0`, which callers should account for.

## Test Signals
No direct tests are included. Behavior is simple and likely covered by randomized test consumers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/testutils/rng.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/tombspan/tombspan.go -->
# sources/storage-engines/pebble/internal/tombspan/tombspan.go

## Purpose
This package tracks "wide" ranged tombstones so Pebble can schedule delete-only compactions that reclaim disk space faster than ordinary compactions. It handles both point-key range deletions and range-key deletions while respecting snapshot isolation.

## Important APIs, Types, and Functions
`WideTombstone` summarizes one or more tombstones with point and range sequence-number ranges, user-key bounds, originating level, and source table. `HighestSeqNum` and `String` expose summary data. `Make(comparer)` initializes a `Set` with a region tree keyed by user-key spans. `Set` stores pending tombstones awaiting snapshot safety and active `tombstonedSpans`. `tombstoneSeqNums.BoundsSeqNums` decides whether a table's point/range contents are older than applicable tombstones using `LargestSeqNumAbsolute`. `AddTombstones` appends and sorts pending tombstones. `UpdateWithEarliestSnapshot` promotes safe pending tombstones into the region tree. `PickCompaction` searches a manifest version for one eligible delete or excise compaction. `DeleteOnlyCompaction` describes the chosen table, level, bounds, and excise/delete mode. `canDeleteOrExciseTable` classifies bounds relationships.

## Control Flow and State
New tombstones enter `pending` sorted by highest sequence number. When the earliest snapshot advances beyond a tombstone's highest sequence number, `UpdateWithEarliestSnapshot` inserts its bounds into the region tree using the low sequence numbers, merging overlapping spans by keeping the maximum point and range tombstone sequence numbers. `PickCompaction` scans region spans, searches lower LSM levels from bottom to top, filters tables whose key kinds and absolute sequence numbers are covered, skips compacting tables while preserving the span, and returns the first complete delete or allowed excise candidate. Spans with no useful future candidates are cleared after iteration. The entire `Set` is in-memory only and intentionally rebuilt from table stats after restart.

## Dependencies and Integration
The package depends on `axisds/regiontree`, Pebble `base` and `manifest`, and standard formatting/sorting packages. It integrates with the table stats collector, LSM version metadata, compaction picker, and delete-only compaction machinery.

## Risks and Edge Cases
Snapshot gating is critical: promoting too early can violate open snapshots. `LargestSeqNumAbsolute` must be used because ordinary compactions can zero sequence numbers. The set is not concurrency-safe; callers must serialize access. If excise is disabled, structurally excisable-only spans are deliberately forgotten, falling back to ordinary compactions. Region tree updates rely on correct comparer ordering and exclusive end bounds.

## Test Signals
`tombspan_test.go` uses datadriven scenarios for adding tombstones, advancing snapshots, marking tables compacting, and picking compactions. It exercises pending promotion, partial promotion, delete/excise choices, and string output.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/tombspan/tombspan.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/tombspan/tombspan_test.go -->
# sources/storage-engines/pebble/internal/tombspan/tombspan_test.go

## Purpose
This file provides datadriven tests for wide tombstone tracking and delete-only compaction picking.

## Important APIs, Types, and Functions
`TestSet` runs `testdata/set`; `TestPartialPromotion` runs `testdata/partial_promotion`. `runSetTest` maintains table metadata, a `tombspan.Set`, and parsed manifest versions. `parseWideTombstone` parses lines such as `L1.1 [a,b) seqnums{point=[1-2], range=[3-4]}` using `strparse`. Datadriven commands include `define-version`, `add`, `update-with-earliest-snapshot`, `pick-compaction`, and `mark-as-compacting`.

## Control Flow and State
Versions are parsed from debug strings and table pointers are indexed by disk file number. Added tombstones reference those table objects. Snapshot update and compaction-pick commands mutate the shared set. Marking a table compacting mutates table metadata so subsequent picks can exercise skip/preserve behavior.

## Dependencies and Integration
The test depends on `datadriven`, `manifest.ParseVersionDebug`, `strparse`, `testkeys.Comparer`, and Pebble base types. It tests integration between tombstone tracking and manifest version metadata rather than only isolated helpers.

## Risks and Gaps
The parser is tailored to fixture syntax and may panic/fail on small format deviations. The tests are scenario-based and do not fuzz arbitrary overlapping tombstone regions or concurrent picker interactions.

## Test Signals
The fixtures are the strongest executable documentation for when a tombstone remains pending, when it promotes, and whether a table is deleted, excised, skipped, or forgotten.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/tombspan/tombspan_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/treeprinter/tree_printer.go -->
# sources/storage-engines/pebble/internal/treeprinter/tree_printer.go

## Purpose
This package builds formatted text trees from depth-first node creation calls. It is used by Pebble debugging and tests to render hierarchical structures.

## Important APIs, Types, and Functions
`Node` is a handle at a specific tree level. `New` and `NewWithStyle` create a root sentinel for `DefaultStyle`, `CompactStyle`, or `BulletStyle`. `Childf`, `Child`, `AddLine`, `AddEmptyLine`, `DotDotDot`, `FormattedRows`, and `String` are the public operations. Internal `tree` stores formatted rows, the current bottom-most path stack, and style-specific edge rune sequences. `set`, `addRow`, and `childLine` update rows and edge connectors.

## Control Flow and State
Callers must add nodes in display order, depth-first pre-order. When a new sibling is added, `childLine` rewrites prior rows to change last-child connectors into mid-child connectors and fill vertical links. Multi-line child text creates a first child line plus additional lines. `AddLine` may shift where future child edges connect. `DotDotDot` appends a hidden-children marker. State is in the mutable `tree` referenced by all `Node` handles; it is not concurrency-safe.

## Dependencies and Integration
The file uses `bytes`, `fmt`, `strings`, and Cockroach errors. It is used by `indenttree` tests and `treesteps` rendering in this work item, and likely by other Pebble debug formatters.

## Risks and Edge Cases
Misordered or stale `Node` use can panic with "misuse of node" or "multiple root nodes". `String` and `FormattedRows` may only be called on the root sentinel. Unicode display width is not measured; runes are counted as columns, which is acceptable for many monospace cases but not all terminals. The output uses Unicode box-drawing characters.

## Test Signals
`tree_printer_test.go` covers default, compact, and bullet styles, UTF text, nesting one tree inside another, and the hidden-children marker.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/treeprinter/tree_printer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/treeprinter/tree_printer_test.go -->
# sources/storage-engines/pebble/internal/treeprinter/tree_printer_test.go

## Purpose
This file validates treeprinter formatting across styles, multiline nodes, Unicode text, nested trees, and omitted-child markers.

## Important APIs, Types, and Functions
`TestTreePrinter` builds a representative tree and compares output under default, compact, and bullet styles. `TestTreePrinterUTF` verifies multiline Japanese text formatting. `TestTreePrinterNested` embeds the formatted output of two treeprinters as child nodes in a third. `TestTreePrinterDotDotDot` validates `DotDotDot` output and connector updates.

## Control Flow and State
Tests build trees through the public `Node` API in depth-first order and compare exact strings after trimming leading fixture newlines. There is no shared state between tests.

## Dependencies and Integration
The file imports `strings` and `testing`. It provides golden coverage for a utility used by other debug/test packages.

## Risks and Gaps
Golden strings are sensitive to whitespace and Unicode box-drawing changes, which is appropriate for this package. Tests do not exercise misuse panics or concurrent calls.

## Test Signals
The exact expected strings define the stable rendering contract. The nested-tree test confirms multiline child strings are a supported integration pattern.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/treeprinter/tree_printer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/treesteps/data.go -->
# sources/storage-engines/pebble/internal/treesteps/data.go

## Purpose
This file defines serializable data structures and rendering/export helpers for treesteps recordings. A recording consists of named steps, each with a tree of nodes, properties, active operations, and hidden-child markers.

## Important APIs, Types, and Functions
`Steps` contains a recording name and a slice of `Step`. `Step` contains a step name and root `TreeNode`. `TreeNode` contains node name, properties, operation labels, children, and `HasHiddenChildren`. `Steps.String` renders one or multiple steps using `treeprinter`. `TreeNode.String` and `print` render a single tree. `Steps.URL` JSON-encodes step names and ASCII tree strings, compresses with zlib, base64 URL-encodes, and embeds the result in a visualization URL.

## Control Flow and State
String rendering walks each step and recursively prints nodes. Node operation labels are appended to names with a left-arrow marker. Properties are rendered as additional lines. URL generation serializes a compact output structure, compresses it, and returns a new `url.URL`; there is no persistent local state.

## Dependencies and Integration
The file depends on `treeprinter`, `crstrings`, `bytes`, `compress/zlib`, `encoding/base64`, `encoding/json`, `fmt`, `net/url`, and `strings`. It is used by invariants-enabled treesteps recording and tests.

## Risks and Edge Cases
`URL` panics on unexpected JSON, compression, or write errors, appropriate for debug instrumentation but not user-facing code. The URL embeds rendered ASCII trees rather than full structured node data, as noted by a TODO. Output includes Unicode arrows and treeprinter characters.

## Test Signals
`tree_steps_test.go` calls `Steps.String` and optional `Steps.URL` through datadriven commands when invariants are enabled. There are no direct serialization round-trip tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/treesteps/data.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/treesteps/doc.go -->
# sources/storage-engines/pebble/internal/treesteps/doc.go

## Purpose
This package documentation explains the treesteps instrumentation framework: recording step-by-step operations over hierarchical data structures for debugging and visualization.

## Important APIs, Types, and Functions
The documentation introduces the `Node` interface, `TreeStepsNode`, `NodeInfo`, `StartRecording`, `StartOpf`, `Finishf`, `NodeUpdated`, recording options `MaxTreeDepth` and `MaxOpDepth`, `Steps.String`, and `Steps.URL`.

## Control Flow and State
The described flow is: start a recording on a root node, wrap operations with start/finish calls, notify significant node updates, and finish to obtain steps. It also explains that non-invariants builds compile these calls into no-ops.

## Dependencies and Integration
The doc ties the package to the `invariants` build tag and to hierarchical data structures in Pebble that want optional debugging instrumentation without production overhead.

## Risks and Edge Cases
The sample code contains a visible typo in `func (t *SumTree) recomputeSum() {)` that should be considered documentation-only. Users must guard expensive formatting with `Enabled && IsRecording` to avoid allocations in normal paths.

## Test Signals
The executable behavior described here is represented in `tree_steps_on.go`, `tree_steps_off.go`, and `tree_steps_test.go`. This doc file itself is not tested.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/treesteps/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/treesteps/tree_steps_off.go -->
# sources/storage-engines/pebble/internal/treesteps/tree_steps_off.go

## Purpose
This file provides the no-op implementation of treesteps for builds without the `invariants` tag. It allows instrumentation calls to remain in production code with minimal overhead.

## Important APIs, Types, and Functions
It defines `Enabled = false`, stub `RecordingOption`, `MaxTreeDepth`, `MaxOpDepth`, `StartRecording`, `NodeUpdated`, `Node`, `NodeInfo`, `NodeInfof`, `AddPropf`, `AddChildren`, `Recording.Finish`, `IsRecording`, `Op`, `StartOpf`, `Updatef`, `UpdateLastOpf`, `Finishf`, and `TreeToString`. Most return zero values, nil, or no-op.

## Control Flow and State
There is no real recording state. `StartRecording` returns nil, operation methods tolerate nil receivers by doing nothing, and `TreeToString` returns a fixed unsupported message.

## Dependencies and Integration
It is selected by `//go:build !invariants` and imports Cockroach errors anonymously, likely to keep package dependencies aligned or satisfy build constraints. It must mirror the public API of the invariants implementation.

## Risks and Edge Cases
Callers must tolerate nil recordings and nil operations in non-invariants builds. Any API added to the on implementation must be mirrored here to avoid build breaks. `Recording.Finish` on a nil recording is not used; `StartRecording` returns nil, so callers normally guard or assign only in tests.

## Test Signals
`tree_steps_test.go` skips when `Enabled` is false, so this file is mainly validated by ordinary non-invariants builds compiling successfully.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/treesteps/tree_steps_off.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/treesteps/tree_steps_on.go -->
# sources/storage-engines/pebble/internal/treesteps/tree_steps_on.go

## Purpose
This invariants-only file implements live treesteps recording. It captures snapshots of a tree before, during, and after operations on nodes, including node properties, children, hidden children, and active operation annotations.

## Important APIs, Types, and Functions
`Enabled = true`. `StartRecording(root,name,opts...)` creates a `Recording` with default max depths and records the initial tree. `MaxTreeDepth` and `MaxOpDepth` adjust recording limits. `NodeUpdated` emits update steps for nodes in active recordings. `NodeInfof`, `AddPropf`, and `AddChildren` describe nodes. `Recording.Finish` clears node ownership and returns `Steps`. `IsRecording` checks active node participation. `StartOpf`, `Op.Updatef`, `UpdateLastOpf`, and `Op.Finishf` manage operation annotations and steps. `TreeToString` renders current state without recording. Internals include global mutex state, `nodeState`, `buildTree`, and `nodeStateLocked`.

## Control Flow and State
A global mutex and atomic flag coordinate all recordings. Starting a recording initializes or reuses the global node map and immediately builds an initial tree. `buildTree` calls each node's `TreeStepsNode`, records node state ownership, captures active ops, and recurses until `maxTreeDepth`, marking hidden children if truncated. Operations are tracked per node; starts and updates emit intermediate steps unless at the max op depth, and finish always emits a final step then removes the op. `Finish` removes all node states for the recording and clears the global active flag if no recordings remain. No disk persistence exists.

## Dependencies and Integration
It uses `fmt`, `reflect`, `slices`, `strings`, `sync`, `sync/atomic`, `unicode`, and Cockroach errors. It integrates with `data.go` for output and with any Pebble data structure implementing `TreeStepsNode`.

## Risks and Edge Cases
The global node map prevents the same node from participating in multiple recordings and panics if violated. Calls into `TreeStepsNode` happen while holding the global mutex, so implementations must avoid reentrant treesteps calls or blocking work. The package is for debug builds; production builds get no-ops. Nil pointer child handling is explicit in `AddChildren`, but passthrough nodes can remap identity through `NodeInfo.node`.

## Test Signals
`tree_steps_test.go` validates segment tree recordings, depth limits, operation updates, URL output, and passthrough node behavior when built with invariants.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/treesteps/tree_steps_on.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/treesteps/tree_steps_test.go -->
# sources/storage-engines/pebble/internal/treesteps/tree_steps_test.go

## Purpose
This file tests treesteps recording through a concrete segment tree example and verifies passthrough node behavior. Tests run only when treesteps are enabled under the `invariants` build tag.

## Important APIs, Types, and Functions
`SegmentTree` and `SegmentNode` implement a simple range-sum segment tree. `NewSegmentTree`, `Root`, `Add`, `add`, `Sum`, and `sum` provide operations instrumented with treesteps calls. `SegmentNode.TreeStepsNode` returns node name, range, sum, and children. `TestSegmentTree` runs datadriven commands for initialization, add, sum, depth options, and URL output. `TestSegmentTreePassthrough` defines `nodeA`, `nodeBWrapper`, and `nodeB` to verify passthrough identity.

## Control Flow and State
The segment tree stores nodes in an array. `Add` recurses to the target point, starts operations on visited nodes, updates sums, calls `NodeUpdated`, and finishes operations. `Sum` starts operations only when `IsRecording` is true, defers finish with the result, and recurses over overlapping children. Tests start recordings around operations and render finished steps.

## Dependencies and Integration
The file depends on `math/bits`, `testing`, and `datadriven`. It serves as executable documentation for instrumenting real hierarchical algorithms with treesteps.

## Risks and Gaps
Tests are skipped without the `invariants` tag, so ordinary CI must include an invariants lane to exercise this behavior. The segment tree is a test vehicle, not a production structure, and focuses on recording semantics rather than algorithm robustness.

## Test Signals
The datadriven outputs define how operation start/update/finish steps, max tree depth, max op depth, and passthrough node identity should appear in rendered recordings.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/treesteps/tree_steps_test.go -->
