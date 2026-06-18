# subset-b-008549 Research

Grouped research report for Pebble SSTable table tests, table filter implementations, value blocks, tiered metadata, test fixtures, virtual bounds, and writer helpers. Each section preserves the exact source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/table_test.go -->
# sources/storage-engines/pebble/sstable/table_test.go

## Purpose
Provides broad SSTable reader/writer regression coverage over prebuilt Hamlet fixture tables and freshly generated in-memory tables. It verifies point lookup, forward/backward iteration, bounds, Bloom/table filter behavior, final block flushing, synthetic sequence numbers, metaindex ordering, and footer decoding across table formats/checksum types.

## Important APIs, Types, And Functions
`check` opens a `Reader`, validates `get`, `NewIter`, `SeekGE`, `SeekLT`, `First`, `Last`, bounds, and missing-key behavior. `testReader` drives prebuilt fixtures. `countingFilterDecoder` wraps the Bloom decoder and classifies true/false positives/negatives. Tests include `TestReaderDefaultCompression`, `TestReaderNoCompression`, `TestReaderTableBloom`, `TestReaderBloomUsed`, `TestBloomFilterFalsePositiveRate`, `TestWriterRoundTrip`, `TestFinalBlockIsWritten`, `TestReaderSymtheticSeqNum`, `TestMetaIndexEntriesSorted`, `TestFooterRoundTrip`, and `TestReadFooter`.

## Control Flow
Most tests construct or open an SST, create a `Reader`, and exercise public/internal iterator APIs over the same expected Hamlet word-count data. Bloom tests replace the decoder with a counting shim. Writer round trips vary block and index sizes, optionally attach a Bloom policy, close the writer, reopen the file, and reuse `check`. Footer tests encode synthetic footers into arbitrary offsets, read them back, and exercise malformed encodings.

## State And Persistence Behavior
The file persists test SSTs in memory for generated cases and reads durable prebuilt fixtures from `testdata`. It validates physical table state through reopened readers, metaindex block contents, block flush completion, and footer handles. It does not mutate production DB state.

## Dependencies And Integration Points
Depends on `Reader`, `newReader`, `Writer`, `NewRawWriter`, `objstorageprovider`, block compression/checksum code, Bloom filter decoders, row-block raw iterators, VFS implementations, and fixture helpers in `test_fixtures.go`. The tests indirectly cover table format compatibility and reader integration with filter policies.

## Risks And Edge Cases
Important risks covered are final partial block loss, out-of-bounds iterator behavior, false-negative filters, degenerate filters that always return true, malformed footers with table-number context, and metaindex key ordering. The Hamlet data is fixed, so coverage is deterministic but not exhaustive for newer columnar-format features.

## Test Signals
Signals are exact key/value equality, expected ErrNotFound, bounded iteration counts, Bloom false-positive ratios, byte counts after reopening, sorted metaindex keys, footer round-trip equality, and expected error substrings for corrupt footers.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/table_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/binary_fuse.go -->
# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/binary_fuse.go

## Purpose
Defines Pebble's binary fuse table filter policy family and decoder registration. It exposes configurable fingerprint widths as `base.TableFilterPolicy` values for SSTable writers and a `base.TableFilterDecoder` for readers.

## Important APIs, Types, And Functions
`Family` is the table filter family string. `SupportedBitsPerFingerprint` mirrors bitpacking support. `FilterPolicy(bitsPerFingerprint)` validates 4, 8, 10, 12, or 16 bits and returns `filterPolicyImpl`. `filterPolicyImpl.Name` emits `binaryfuse(N)`, `NewWriter` creates a writer, and `PolicyFromName` parses policy names. `Decoder` implements `Family` and `MayContain`.

## Control Flow
Callers choose a policy during SSTable writing. The policy creates a writer that hashes keys and emits binary fuse filter bytes tagged with `Family`. During reads, the table-filter dispatcher selects `Decoder` by family and calls `MayContain`, which hashes the lookup key with xxh3 and delegates to `mayContain`.

## State And Persistence Behavior
The only persistent output is policy name metadata and filter bytes stored in SSTables. The file itself has no mutable state beyond immutable policy structs.

## Dependencies And Integration Points
Integrates with `base.TableFilterPolicy`, `base.TableFilterWriter`, `base.TableFilterDecoder`, `tablefilters.PolicyFromName`, `bitpacking`, `xxh3`, and the binary fuse build/probe code in neighboring files.

## Risks And Edge Cases
Unsupported fingerprint widths panic at policy construction and are ignored by name parsing. Older Pebble binaries may not understand this family, making format compatibility a deployment concern. FPR and bits/key are documented as size-dependent, especially for smaller filters.

## Test Signals
Covered by binary fuse end-to-end tests, policy name parsing paths, build tests, and writer/probe benchmarks in this package.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/binary_fuse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/binary_fuse_test.go -->
# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/binary_fuse_test.go

## Purpose
Exercises binary fuse filters through the shared table-filter test harness and records benchmark baselines for filter construction and membership queries.

## Important APIs, Types, And Functions
`TestEndToEnd` calls `filtertestutils.RunEndToEndTest` for 4, 8, 10, 12, and 16 bit fingerprints with generous FPR thresholds. `BenchmarkWriter`, `BenchmarkMayContain`, and `BenchmarkMayContainLarge` call shared benchmark helpers using every supported fingerprint size.

## Control Flow
The end-to-end test randomly generates key sets, builds a filter through `FilterPolicy`, verifies every inserted key is reported as present, then probes random non-members and fails if the observed false-positive rate exceeds the supplied threshold. Benchmarks construct filters over fixed key sizes/counts and repeatedly call decoder membership checks.

## State And Persistence Behavior
All state is in-memory filter data and random test keys. No SSTable file is written directly; the test exercises the policy/decoder contract used by table writers.

## Dependencies And Integration Points
Depends on `filtertestutils`, the package `Decoder`, and `SupportedBitsPerFingerprint`. It provides integration confidence for `binary_fuse.go`, `filter.go`, `hash_collector.go`, `writer.go`, and `bitpacking`.

## Risks And Edge Cases
FPR thresholds are intentionally loose to avoid flakes, so they catch gross regressions rather than precise probabilistic drift. Benchmarks document expected performance but are not assertions.

## Test Signals
Signals are no false negatives, FPR below threshold, successful filter creation, and benchmark metrics for MKeys/s and nanosecond membership checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/binary_fuse_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/bitpacking/bitpacking.go -->
# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/bitpacking/bitpacking.go

## Purpose
Implements compact random-access encodings for binary fuse fingerprints with 4, 8, 10, 12, and 16 bits per value. The package optimizes for fast decoding of individual or triple fingerprint positions without materializing an unpacked slice.

## Important APIs, Types, And Functions
`SupportedBitsPerValue` lists valid widths. `EncodedSize` computes exact output sizes including padding needed for unsafe reads. `Encode8` handles 4- and 8-bit values; `Encode16` handles 10-, 12-, and 16-bit values. Helpers include `encode4bpv`, `encode10bpv`, `encode12bpv`, `encode16bpv`, `Decode`, `Decode3`, and unsafe little-endian readers.

## Control Flow
Encoding switches on bits-per-value and uses specialized packing loops: SWAR nibble packing for 4 bits, direct copy for 8/16 bits on little-endian systems, 32-value groups for 10 bits, and 2-value/8-value groups for 12 bits. Decoding computes byte offsets and shifts for the selected width. `Decode3` performs one max-index bounds check and returns three values for binary fuse probes.

## State And Persistence Behavior
The functions are pure transformations over caller-owned buffers. The encoded bytes are persisted inside binary fuse SSTable filter blocks, with padding bytes included to support safe unaligned reads.

## Dependencies And Integration Points
Depends on `encoding/binary`, `unsafe`, CockroachDB errors, and invariants. It is used by `binaryfuse.build` to encode fingerprints and by `binaryfuse.mayContain` to decode the three probe positions.

## Risks And Edge Cases
The code relies on exact output sizes, padding, little-endian interpretation, and unsafe pointer arithmetic. Unsupported bpv values panic. Odd value counts, partial groups, and zero-length input need to remain consistent with `EncodedSize`.

## Test Signals
Unit tests cover known encodings, round trips across random data and all widths, `Decode3`, and encode/decode benchmarks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/bitpacking/bitpacking.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/bitpacking/bitpacking_test.go -->
# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/bitpacking/bitpacking_test.go

## Purpose
Validates binary fuse fingerprint bitpacking correctness and provides performance benchmarks for encode and triple-decode operations.

## Important APIs, Types, And Functions
Tests include `TestEncode8_BPV4`, `TestEncode8_BPV8`, `TestEncode16_BPV10`, `TestEncode16_BPV12`, `TestEncode16_BPV16`, `TestDecode_BPV4`, `TestDecode_BPV8`, `TestDecode_BPV10`, `TestDecode_BPV12`, `TestDecode_BPV16`, and `TestRoundTrip`. Benchmarks include `BenchmarkEncode` and `BenchmarkDecode3`.

## Control Flow
Known-value tests encode fixed arrays and compare exact bytes or decode them back. `TestRoundTrip` generates random inputs, encodes for every supported width, checks `Decode` for every index, then samples random triples and checks `Decode3`.

## State And Persistence Behavior
The tests operate entirely on in-memory byte slices. They intentionally prefill encoded buffers to expose missing writes in partial encoders.

## Dependencies And Integration Points
Depends on `math/rand/v2`, `testing`, and `testify/require`. It directly protects the binary fuse filter's persisted fingerprint representation.

## Risks And Edge Cases
Coverage includes odd counts, high bits masking, partial 10-bit/12-bit groups, and little-endian 16-bit output. It does not fuzz malformed encoded data because production callers calculate offsets from trusted filter metadata.

## Test Signals
Signals are exact encoded bytes, equality of decoded masked values, and stable benchmark metrics for Gvals/s and ns/op.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/bitpacking/bitpacking_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/filter.go -->
# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/filter.go

## Purpose
Builds and probes binary fuse filter byte encodings. It manages builder memory reuse/concurrency limits, constructs filters with the external xorfilter library, packs fingerprints, appends the trailer, and implements zero-allocation membership checks over packed data.

## Important APIs, Types, And Functions
Constants `maxSizeForPool`, `maxSizeForReuse`, and `maxSize` define regimes. `globalState`, `builder`, `ensureInitialized`, `builderPool`, and `withBuilder` coordinate reusable builders and a semaphore. `buildFilter`, generic `build[T]`, `mayContain`, and `murmur64` implement filter construction and lookup. `trailerLen` is 14 bytes containing seed, segment count, segment shift, and fingerprint width.

## Control Flow
`buildFilter` rejects empty and too-large collectors, gathers hash blocks into a builder slice, selects `uint8` or `uint16` fingerprints, and calls `BuildBinaryFuse`. The result fingerprints are bitpacked, then seed/segment metadata is appended. `mayContain` parses the trailer, recomputes the binary fuse probe positions from the hash plus seed, decodes three packed fingerprints, and compares their xor with the target fingerprint.

## State And Persistence Behavior
The persisted filter is packed fingerprint bytes followed by a fixed trailer. Builder pools and reusable builders are process-local memory optimizations. No persistent state exists outside SSTable filter bytes.

## Dependencies And Integration Points
Depends on `github.com/FastFilter/xorfilter`, `fifo.Semaphore`, `bitpacking`, `runtime.GOMAXPROCS`, and `hashCollector`. It is invoked by `tableFilterWriter.Finish` and `Decoder.MayContain`.

## Risks And Edge Cases
Builder memory is large, so concurrency throttling is correctness-adjacent for resource pressure. Construction can theoretically fail for small sets and returns `ok=false`. `mayContain` trusts trailer consistency and packed data size enough to decode positions, so corrupted filters may panic if metadata is nonsensical.

## Test Signals
`TestBuildFilter`, end-to-end filter tests, simulations, and benchmarks validate no false negatives, expected FPR shape, and performance across sizes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/filter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/filter_test.go -->
# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/filter_test.go

## Purpose
Stress-tests binary fuse filter construction over random set sizes up to the configured maximum and verifies sampled inserted hashes always probe as present.

## Important APIs, Types, And Functions
`TestBuildFilter` picks random size ranges with a bias toward 10K and occasional 1M/max-size cases. `testBuild` loads hashes into a `hashCollector`, picks a random supported fingerprint width, builds the filter, and probes up to 100K inserted hashes.

## Control Flow
Each run allocates random hashes, adds them to the collector, calls `buildFilter`, requires success, then randomly samples existing hashes and checks `mayContain`. The test exercises pool, reuse, and large-builder regimes indirectly through randomized sizes.

## State And Persistence Behavior
All state is in-memory hashes and filter bytes. The collector may use pooled hash blocks and builder code may use global pools/semaphores.

## Dependencies And Integration Points
Depends on `math/rand/v2`, `testify/require`, `hashCollector`, `buildFilter`, and `mayContain`. It complements the policy-level end-to-end tests by bypassing key hashing.

## Risks And Edge Cases
The test does not assert false-positive rates or corrupted-input behavior. Random size selection can miss specific boundary values on a given run, but it samples small, medium, large, and max-size regimes.

## Test Signals
Signals are successful filter construction and absence of false negatives for sampled inserted hashes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/filter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/hash_collector.go -->
# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/hash_collector.go

## Purpose
Provides a pooled block-based collector for 64-bit key hashes used while building binary fuse table filters.

## Important APIs, Types, And Functions
`hashCollector` tracks `numHashes`, `lastHash`, current block, and a slice of pooled `hashBlock`s. `hashBlockLen` is 8192. `Init`, `Add`, `NumHashes`, `Blocks`, and `Reset` are the primary methods; `hashBlockPool` reuses block allocations.

## Control Flow
`Add` skips consecutive duplicate hashes, allocates a new pooled block when the current block fills, writes the hash, and advances counters. `Blocks` returns an `iter.Seq` over full blocks and the final partial block. `Reset` returns blocks to the pool and reinitializes inline block-slice storage.

## State And Persistence Behavior
State is transient writer memory. Consecutive duplicate suppression affects the constructed filter by avoiding redundant adjacent keys, matching sorted SSTable key insertion patterns.

## Dependencies And Integration Points
Used by the binary fuse table filter writer and `buildFilter`. Depends only on Go `iter` and `sync.Pool`.

## Risks And Edge Cases
`Blocks` must not be called on an empty collector, as documented. Reset must return all blocks exactly once to avoid leaks or aliasing. Only consecutive duplicate hashes are removed, not all duplicates.

## Test Signals
Covered indirectly by filter build/end-to-end tests. No direct unit test targets block iteration or reset.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/hash_collector.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/simulation.go -->
# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/simulation.go

## Purpose
Runs probabilistic simulations for binary fuse filter false-positive rates and average bits per key for documentation and tuning.

## Important APIs, Types, And Functions
`SimulateFPR(avgSize, fpBits)` returns mean FPR, standard deviation, and average bits per key. It uses `filtersim.SimulateFPR`, random 64-bit hashes, `hashCollector`, `buildFilter`, `mayContain`, and atomic counters for aggregate key/filter bytes.

## Control Flow
For each run, the simulation chooses a set size near `avgSize`, builds a filter for random hashes, performs `10000 * 2^fpBits` random non-member probes, computes the positive rate, and accumulates bytes/key. It prints a human-readable summary.

## State And Persistence Behavior
No persisted state. It constructs transient filters and collectors for generated documentation. Atomic counters coordinate concurrent simulation workers.

## Dependencies And Integration Points
Depends on `filtersim`, `crhumanize`, random number generation, and binary fuse build/probe internals. `simulation_gen.go` consumes it to produce `simulation.md`.

## Risks And Edge Cases
If filter construction fails, the simulation panics because documentation generation expects valid parameter combinations. The random model uses uniformly distributed hashes and may not reflect pathological real key distributions beyond the hash function.

## Test Signals
The output FPR table is the signal; it supports comments in the policy file but is not part of normal tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/simulation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/simulation_gen.go -->
# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/simulation_gen.go

## Purpose
Standalone ignored build program that generates binary fuse `simulation.md` documentation.

## Important APIs, Types, And Functions
`main` defines fingerprint widths, average key-set sizes, calls `binaryfuse.SimulateFPR`, formats a markdown table with `ascii.Make`, and writes `simulation.md`.

## Control Flow
The program iterates bits/fingerprint and average sizes, collects FPR/stddev/bits-key results, appends table rows, prints the board, and writes it to disk.

## State And Persistence Behavior
The only persistence is the generated `simulation.md` file in the current package directory. It is excluded from normal builds by `//go:build ignore`.

## Dependencies And Integration Points
Depends on `binaryfuse.SimulateFPR`, `crhumanize`, and `internal/ascii`. It is a documentation generator for policy comments and tuning.

## Risks And Edge Cases
The listed `bitVals` omit 10 even though the implementation supports 10-bit fingerprints, which may be intentional documentation scope or a stale generator choice. Long simulation runs can be CPU-heavy.

## Test Signals
Manual `go run simulation_gen.go` output and the generated markdown table are the primary signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/simulation_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/writer.go -->
# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/writer.go

## Purpose
Implements `base.TableFilterWriter` for binary fuse filters, translating SSTable keys into xxh3 hashes and final filter bytes.

## Important APIs, Types, And Functions
`tableFilterWriter` stores `bitsPerFingerprint` and a `hashCollector`. `newTableFilterWriter`, `init`, `AddKey`, and `Finish` implement construction and the table-filter writer interface.

## Control Flow
The policy creates a writer with a configured fingerprint width. SSTable writing calls `AddKey` for each filter key, storing the xxh3 hash. `Finish` calls `buildFilter`; on success it resets the collector and returns filter bytes plus `Family`, otherwise it returns `ok=false`.

## State And Persistence Behavior
The collector is transient until `Finish`. The returned filter data is persisted in the SSTable filter block. `Finish` releases pooled hash blocks through `Reset` only on successful build.

## Dependencies And Integration Points
Depends on Pebble `base` filter interfaces, `xxh3`, `hashCollector`, and `buildFilter`. Created from `filterPolicyImpl.NewWriter`.

## Risks And Edge Cases
Empty filters, too-large filters, or construction failure produce no filter. If a caller abandons a writer without `Finish`, hash blocks are not reset through this file's path.

## Test Signals
Covered by binary fuse end-to-end tests, build tests, and writer benchmarks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/adaptive_policy.go -->
# sources/storage-engines/pebble/sstable/tablefilters/bloom/adaptive_policy.go

## Purpose
Adds an adaptive Bloom table filter policy that caps filter byte size by reducing bits per key when necessary.

## Important APIs, Types, And Functions
`AdaptivePolicy(targetBitsPerKey, maxFilterSize)` returns `adaptivePolicyImpl`. `adaptivePolicyImpl.Name` emits `adaptive_bloom(target,max)`, and `NewWriter` returns `adaptiveFilterWriter`. `adaptiveFilterWriter.AddKey` and `Finish` build the filter. `FilterSize` computes serialized size, and `MaxBitsPerKey` finds the largest bits/key fitting a byte limit.

## Control Flow
The writer collects hashes like a normal Bloom writer. On `Finish`, it computes the target filter size; if larger than `maxSize`, it calls `MaxBitsPerKey`. If the result is below 2 bits/key, it declines to build a filter. Otherwise it builds a standard cache-line Bloom filter with adjusted probes and line count.

## State And Persistence Behavior
The policy name and generated Bloom filter bytes persist in SSTables. Adaptive decisions are per-filter at finish time, based on collected key count and configured byte limit.

## Dependencies And Integration Points
Depends on Bloom `hashCollector`, `FilterSize`, `calculateNumLines`, `calculateProbes`, `buildFilter`, `Family`, Pebble filter interfaces, and invariants. Name parsing is integrated in `bloom.PolicyFromName`.

## Risks And Edge Cases
A too-small max size suppresses the filter entirely. The max-size math must honor odd cache-line counts and trailer bytes. Lowering bits/key trades memory for higher FPR; one-bit filters are intentionally rejected as not useful.

## Test Signals
`adaptive_policy_test.go` covers size math, policy behavior, randomized max sizes, and name parsing.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/adaptive_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/adaptive_policy_test.go -->
# sources/storage-engines/pebble/sstable/tablefilters/bloom/adaptive_policy_test.go

## Purpose
Validates adaptive Bloom size calculations, capped filter construction, empty/too-small behavior, and policy-name parsing.

## Important APIs, Types, And Functions
Tests include `TestFilterSize`, `TestMaxBitsPerKey`, `TestAdaptivePolicy`, and `TestAdaptivePolicyFromName`. Local helpers build filters with deterministic little-endian keys, require size constraints, and check inserted-key membership plus rough FPR sanity.

## Control Flow
`TestFilterSize` compares formula output to actual writer output over randomized counts and bits/key. `TestMaxBitsPerKey` verifies boundary behavior around exact filter sizes and random max sizes. `TestAdaptivePolicy` builds capped filters under full, oversized, half, quarter, empty, too-small, and randomized cases. Name parsing asserts adaptive and non-adaptive cases.

## State And Persistence Behavior
All state is in-memory filter bytes. It verifies serialized byte sizes but does not write SSTables.

## Dependencies And Integration Points
Depends on Bloom policy internals, `base.TableFilterFamily`, and `testify/require`. It protects the adaptive policy used through `tablefilters.PolicyFromName`.

## Risks And Edge Cases
FPR sanity only ensures the filter is not effectively all-true. Randomized tests may not cover every odd-line transition, but exact boundary checks around `FilterSize` cover important math.

## Test Signals
Signals are size equality/inequality, successful membership for inserted keys, rejection of empty or impractically small filters, and correct parsed policy fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/adaptive_policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/bits.go -->
# sources/storage-engines/pebble/sstable/tablefilters/bloom/bits.go

## Purpose
Implements cache-line-oriented Bloom filter bit storage, serialization, construction, and membership probing compatible with RocksDB full-file filters.

## Important APIs, Types, And Functions
Constants `cacheLineSize` and `cacheLineBits` define 64-byte lines. `filterBits` aliases raw bytes with a line count. `aliasFilterBits`, `cacheLine`, `probe`, `set`, `buildFilter`, and `mayContain` implement the bit-level behavior.

## Control Flow
`buildFilter` allocates `nLines*64 + 5` bytes, sets all probes for every collected hash within one cache line, then appends one byte of probe count and four bytes of line count. `mayContain` parses this trailer, validates expected cache-line sizing, aliases the bit region, and probes all bits for the candidate hash.

## State And Persistence Behavior
The filter bytes are persisted in SSTables as bit data plus a 5-byte trailer. `filterBits` is just a transient unsafe alias over the byte slice.

## Dependencies And Integration Points
Used by Bloom writer, adaptive writer, decoder, simulations, and tests. Depends on `encoding/binary`, `unsafe`, and CockroachDB errors.

## Risks And Edge Cases
The code performs unsafe aliasing and panics if the serialized line sizing is inconsistent. Corrupt filters with zero line count could misbehave before validation. All probes remain within one cache line for locality, which drives FPR/probe tuning.

## Test Signals
Bloom unit tests verify exact small-filter bytes, inserted-key membership, false-positive bounds, and RocksDB-compatible hash expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/bits.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/bloom.go -->
# sources/storage-engines/pebble/sstable/tablefilters/bloom/bloom.go

## Purpose
Defines Pebble's RocksDB-compatible Bloom table filter policy, hash function, writer, decoder, and policy-name parsing.

## Important APIs, Types, And Functions
`probes` and `calculateProbes` tune probes per bits/key. `hash` implements a RocksDB/LevelDB-compatible Murmur-like 32-bit hash including signed-byte tail behavior. `tableFilterWriter` collects hashes. `FilterPolicy`, `filterPolicyImpl.Name`, `NewWriter`, `PolicyFromName`, `Family`, and `Decoder` expose the table-filter contract.

## Control Flow
Writers call `AddKey`, accumulating hashes while suppressing consecutive duplicates in the collector. `Finish` calculates an odd number of 64-byte cache lines, builds filter bytes, resets the collector, and returns `Family`. Readers select `Decoder` by family and call `mayContain` over the serialized filter.

## State And Persistence Behavior
The policy name and `rocksdb.BuiltinBloomFilter` family are persisted in table metadata/filter blocks. The default 10-bit policy preserves the historical family name for compatibility.

## Dependencies And Integration Points
Integrates with SSTable writer/reader filter plumbing, `tablefilters.PolicyFromName`, adaptive policy parsing, and test fixture generation. Depends on Pebble base filter interfaces and `bits.go`.

## Risks And Edge Cases
Hash compatibility depends on signed-byte tail casting. Bits/key must be at least one. For bits/key above 10, probe count is capped at the simulated optimum table entry. Approximate bits/key is rounded by cache-line granularity and odd line count.

## Test Signals
Bloom tests compare exact small-filter bits, hash outputs from RocksDB, end-to-end FPR, and benchmark construction/probing speed.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/bloom.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/bloom_test.go -->
# sources/storage-engines/pebble/sstable/tablefilters/bloom/bloom_test.go

## Purpose
Tests Bloom filter serialization, hash compatibility, false-positive behavior, end-to-end policy/decoder operation, and performance.

## Important APIs, Types, And Functions
`filterStr` renders filter bytes. `newTableFilter` builds a filter through the policy. Tests include `TestSmallBloomFilter`, `TestBloomFilter`, `TestHash`, and `TestEndToEnd`. Benchmarks include `BenchmarkBloomFilterWriter`, `BenchmarkMayContain`, and `BenchmarkMayContainLarge`.

## Control Flow
Small-filter tests compare exact visual bits from RocksDB. The main Bloom test builds filters for increasing key counts, verifies size bounds and no false negatives, then samples 10K non-members and checks FPR. Hash tests compare known RocksDB values. End-to-end tests use the shared randomized harness for multiple bits/key settings.

## State And Persistence Behavior
All filter state is in-memory. The exact small-filter bytes model the persisted SSTable filter format.

## Dependencies And Integration Points
Depends on `filtertestutils`, Bloom policy internals, and RocksDB-derived expected outputs. Protects fixture compatibility and reader/writer filter behavior.

## Risks And Edge Cases
FPR checks are probabilistic and could theoretically flake, though thresholds are broad. Exact expected bytes make the test sensitive to any serialization or hash change.

## Test Signals
Signals are exact byte rendering, no false negatives, FPR under configured limits, stable hash outputs, and benchmark metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/bloom_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/hash_collector.go -->
# sources/storage-engines/pebble/sstable/tablefilters/bloom/hash_collector.go

## Purpose
Provides a pooled block-based collector for 32-bit Bloom filter hashes.

## Important APIs, Types, And Functions
`hashCollector` stores count, last hash, current block, and block slice. `hashBlockLen` is 16384. `Init`, `Add`, `NumHashes`, `Blocks`, and `Reset` manage collection and iteration. `hashBlockPool` reuses block memory.

## Control Flow
`Add` skips consecutive duplicate hashes, obtains a new block when needed, and appends the hash. `Blocks` yields all full blocks and the final partial block through an `iter.Seq`. `Reset` returns blocks to the pool and reinitializes the collector.

## State And Persistence Behavior
State is transient during filter construction. Consecutive duplicate suppression changes the generated filter only for adjacent duplicate filter keys.

## Dependencies And Integration Points
Used by normal and adaptive Bloom writers plus simulations. Depends only on Go `iter` and `sync.Pool`.

## Risks And Edge Cases
`Blocks` is documented as invalid when empty. Pool misuse or missing reset could retain memory. The collector deduplicates only adjacent equal hashes, which matches sorted table write behavior but is not global deduplication.

## Test Signals
Covered indirectly by Bloom filter construction, adaptive policy, and simulation tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/hash_collector.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/simulation.go -->
# sources/storage-engines/pebble/sstable/tablefilters/bloom/simulation.go

## Purpose
Simulates Bloom filter false-positive rates for a given bits/key and probe count, supporting the probe table and documentation.

## Important APIs, Types, And Functions
`SimulateFPR(bitsPerKey, numProbes)` uses `filtersim.SimulateFPR`, random hash collection, `calculateNumLines`, `buildFilter`, `aliasFilterBits`, and `probe`. It returns mean FPR and a formatted string.

## Control Flow
Each run builds a filter for a random size near 10K, probes `cacheLineSize * size` random hashes, subtracts estimated true-positive hash collision contribution, and contributes the result to the aggregate.

## State And Persistence Behavior
No durable state. It builds transient filter bytes for generated documentation.

## Dependencies And Integration Points
Consumed by `simulation_gen.go`. Depends on shared `filtersim` helpers and Bloom internals.

## Risks And Edge Cases
The simulation assumes uniform random 32-bit hashes and estimates true positives from hash-space collision probability. It is CPU-heavy but not used in normal builds.

## Test Signals
Printed lines and the generated simulation markdown table are the primary signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/simulation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/simulation_gen.go -->
# sources/storage-engines/pebble/sstable/tablefilters/bloom/simulation_gen.go

## Purpose
Ignored standalone generator for Bloom filter `simulation.md`, including best probe counts and full FPR data.

## Important APIs, Types, And Functions
`main` iterates bits/key up to 20 and probe counts up to 16, calls `bloom.SimulateFPR`, selects the lowest-FPR probe count with a 1 percent tolerance for fewer probes, formats markdown through `ascii.Make`, and writes `simulation.md`.

## Control Flow
The generator first fills FPR tables, then chooses the best probe count per bits/key. It writes a compact best table followed by full data for all simulated combinations.

## State And Persistence Behavior
Only persists the generated markdown file. `//go:build ignore` keeps it out of normal builds.

## Dependencies And Integration Points
Depends on `bloom.SimulateFPR`, `internal/ascii`, and `os.WriteFile`. Its output informs `probes` and comments in `bloom.go`.

## Risks And Edge Cases
Simulation runtime scales with bits/key/probe combinations. The 1 percent tolerance chooses smaller probe counts for speed even if not strictly optimal.

## Test Signals
Manual generation output and consistency with the hard-coded probe table are the signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/bloom/simulation_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/internal/filtersim/fpr.go -->
# sources/storage-engines/pebble/sstable/tablefilters/internal/filtersim/fpr.go

## Purpose
Provides shared concurrent helpers for estimating and formatting table-filter false-positive rates.

## Important APIs, Types, And Functions
`SimulateFPR(numRuns, avgSize, runExperiment)` executes experiments in parallel and aggregates rates with `metricsutil.Welford`. `FormatFPR` prints a percentage plus 1-in-N ratio. `FormatFPRWithStdDev` adds relative standard deviation formatting.

## Control Flow
`SimulateFPR` preloads a channel with run tokens, starts `GOMAXPROCS` workers, picks a random size within +/-10 percent of average for each run, invokes the caller experiment, and adds the result under a mutex.

## State And Persistence Behavior
No persistent state. The Welford accumulator is transient and protected by a mutex.

## Dependencies And Integration Points
Used by Bloom and binary fuse simulation packages. Depends on `runtime`, `sync`, `math/rand/v2`, `metricsutil`, and `crhumanize`.

## Risks And Edge Cases
`FormatFPR` assumes positive non-zero FPR; zero would produce log/ratio issues. Concurrent simulations share the global random source from `math/rand/v2`.

## Test Signals
No direct tests; correctness is inferred from simulation generators and plausible formatted output.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/internal/filtersim/fpr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/internal/filtertestutils/bench.go -->
# sources/storage-engines/pebble/sstable/tablefilters/internal/filtertestutils/bench.go

## Purpose
Provides reusable benchmark harnesses for table filter writers and membership checks across Bloom and binary fuse implementations.

## Important APIs, Types, And Functions
`BenchmarkWriter`, `BenchmarkMayContain`, `BenchmarkMayContainLarge`, and `randKeys` are the main helpers. They accept `base.TableFilterPolicy` and decoder interfaces.

## Control Flow
Writer benchmarks generate fixed random key sets for key lengths 6, 16, and 128 and counts 10K, 100K, and 1M, then repeatedly construct filters. Membership benchmarks build a filter, run positive and negative subbenchmarks, and large benchmarks prebuild 1024 large filters then query them with configurable goroutine counts.

## State And Persistence Behavior
All state is in-memory random keys and filter bytes. `crypto/rand` fills key buffers, and benchmark loops report derived throughput metrics.

## Dependencies And Integration Points
Used by Bloom and binary fuse benchmark files. Depends on Pebble base filter interfaces, `crhumanize`, `runtime`, and synchronization primitives.

## Risks And Edge Cases
Large benchmarks allocate substantial memory and are intended for explicit benchmark runs. Positive benchmark indexing assumes at least 4096 keys in the generated set, which holds for configured counts.

## Test Signals
Benchmark output reports MKeys/s or ns/op; fatal checks catch unexpected false negatives or filter build failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/internal/filtertestutils/bench.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/internal/filtertestutils/end_to_end.go -->
# sources/storage-engines/pebble/sstable/tablefilters/internal/filtertestutils/end_to_end.go

## Purpose
Provides a shared randomized correctness and coarse-FPR test for table filter policies and decoders.

## Important APIs, Types, And Functions
`RunEndToEndTest(t, policy, decoder, maxFPR)` builds random filters and checks no false negatives plus an upper bound on false positives. `randKey` creates crypto-random keys.

## Control Flow
For ten runs, it chooses a random key count from small to occasional 1M, generates random keys of length 10-19, builds a filter, verifies every inserted key through the decoder, then probes 1000 random non-members and compares the observed rate to `maxFPR`.

## State And Persistence Behavior
Only in-memory keys and filters are used. No SSTable is written.

## Dependencies And Integration Points
Used by Bloom and binary fuse tests. Depends on `base.TableFilterPolicy`, `base.TableFilterDecoder`, crypto random, and `math/rand/v2`.

## Risks And Edge Cases
The FPR bound is deliberately broad and the sample count is small to keep tests fast and non-flaky. Crypto-random generation errors are ignored.

## Test Signals
Signals are successful filter build, no false negatives, and false-positive rate below the caller-provided threshold.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/internal/filtertestutils/end_to_end.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/table_filters.go -->
# sources/storage-engines/pebble/sstable/tablefilters/table_filters.go

## Purpose
Centralizes registration and name parsing for SSTable table filter families supported by Pebble.

## Important APIs, Types, And Functions
`Decoders` lists Bloom and binary fuse decoders. `PolicyFromName` resolves `"none"`, Bloom names, adaptive Bloom names, and binary fuse names to `base.TableFilterPolicy`.

## Control Flow
Callers parse a configured policy name by checking the no-filter sentinel first, then delegating to Bloom and binary fuse package parsers. Readers can use `Decoders` to recognize filter families present in SSTables.

## State And Persistence Behavior
No mutable state. The file defines process-level decoder registration and policy lookup behavior.

## Dependencies And Integration Points
Integrates `base`, `bloom`, and `binaryfuse` packages with higher-level options/config parsing.

## Risks And Edge Cases
Parsing order means Bloom gets first chance after `"none"`, then binary fuse. Unknown names return `(nil,false)` and must be handled by callers.

## Test Signals
Covered indirectly by Bloom adaptive name tests, binary fuse policy parsing, and any option parsing that calls `PolicyFromName`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tablefilters/table_filters.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/test_fixtures.go -->
# sources/storage-engines/pebble/sstable/test_fixtures.go

## Purpose
Defines Hamlet-based SSTable fixture data, fixture metadata, and builders for reproducible reader/writer tests.

## Important APIs, Types, And Functions
`testKVs` and `SortedKeys` model expected data. `hamletWordCount` lazily parses `testdata/h.txt`. `hamletNonsenseWords` lists guaranteed misses. `buildHamletTestSST` writes the fixture data plus periodic range deletions. `TestFixtureInfo`, `TestFixtures`, `Build`, fixture size constants, and `fixtureComparer` define fixture variants.

## Control Flow
`hamletWordCount` loads and validates 1710 word-count rows once. Fixture builds sort keys, create a writer with requested compression/filter/comparer/index size/table format, write every key, and mirror `make-table.cc` range deletion generation.

## State And Persistence Behavior
The parsed Hamlet map is cached in package global state. Fixture builds persist SSTables to a caller-provided VFS. The prebuilt fixtures under `testdata` are regenerated from this metadata.

## Dependencies And Integration Points
Used by `table_test.go`, `writer_fixture_test.go`, and `testdata/make-table.go`. Depends on `Writer`, Bloom filter policy, block compression profiles, VFS, and object-storage writable adapters.

## Risks And Edge Cases
Fixture byte equality depends on deterministic writer behavior, compression implementation, and fixed fixture format. The prefix comparer uses full-key split on Hamlet data, which is limited as a prefix-filter stressor.

## Test Signals
Signals are parsed row count, absence of nonsense words in data, successful table reads, and fixture byte-for-byte comparisons.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/test_fixtures.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/test_utils.go -->
# sources/storage-engines/pebble/sstable/test_utils.go

## Purpose
Provides test helpers for reading full SSTable contents, parsing textual key/span specifications, constructing SSTables from test input, and parsing writer options for datadriven tests.

## Important APIs, Types, And Functions
`ReadAll` returns point KVs, range deletions, and range keys. `ParsedKVOrSpan` models point keys, range spans, blob handles, dual-tier blob handles, and force-obsolete markers. `ParseTestKVsAndSpans`, `ParseTestSST`, `ParseWriterOptions`, `testingBloomFilterPolicy`, `makeTestingBloomFilterPolicy`, and `comparerFromCmdArg` are the main utilities.

## Control Flow
Parsing walks line-oriented input, handles `Span:` lines through `keyspan.ParseSpan`, point lines through `base.ParseInternalKV`, optional `force-obsolete`, blob/dual-tier handle decoding, attributes, and test-key metadata extraction. `ParseTestSST` dispatches each parsed item to `RawWriter.Add`, blob add methods, or `EncodeSpan`. Writer option parsing mutates `WriterOptions` from datadriven command args.

## State And Persistence Behavior
Helpers create or read SSTable state through supplied readers/writers. Parsing itself is transient, with panic recovery returning errors for bad input.

## Dependencies And Integration Points
Used by many SSTable datadriven tests. Integrates `Reader`, `RawWriter`, `blobtest.Values`, `keyspan`, `testkeys`, Bloom policies, and comparer selection.

## Risks And Edge Cases
Ignoring unknown writer-option keys is explicitly noted as error-prone. Blob parsing requires a non-nil blob test value registry. `force-obsolete` is rejected for range deletions. Returned `ReadAll` values clone keys/spans to avoid iterator buffer lifetimes.

## Test Signals
Signals are successful parse/write/read cycles and clear wrapped errors identifying the failed parsed item.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/test_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/testdata/Makefile -->
# sources/storage-engines/pebble/sstable/testdata/Makefile

## Purpose
Defines fixture regeneration targets for SSTable testdata.

## Important APIs, Types, And Functions
Targets are `all`, `.PHONY: rebuild`, `rebuild`, and `h.txt`. `rebuild` runs `go run ./make-table.go`. `h.txt` derives word counts from `hamlet-act-1.txt`.

## Control Flow
The `h.txt` pipeline lowercases Hamlet text, extracts words, sorts, counts unique words, formats count/key rows, and writes `h.txt`. Rebuild then invokes the Go fixture generator.

## State And Persistence Behavior
Persists regenerated `h.txt` and SST fixture files under `sstable/testdata`.

## Dependencies And Integration Points
Used with `make-table.go`, fixture metadata in `test_fixtures.go`, and standard Unix text tools (`cat`, `tr`, `grep`, `sort`, `uniq`, `awk`).

## Risks And Edge Cases
The pipeline depends on locale/tool behavior for word extraction and sorting. Regenerated fixture bytes can change if writer, compression, or input text changes.

## Test Signals
Successful `make rebuild` and matching fixture tests indicate consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/testdata/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/testdata/make-table.go -->
# sources/storage-engines/pebble/sstable/testdata/make-table.go

## Purpose
Regenerates SSTable fixture files from `sstable.TestFixtures`.

## Important APIs, Types, And Functions
`main` validates it is run from the `testdata` directory, changes to the parent `sstable` directory so relative fixture paths work, iterates `sstable.TestFixtures`, and calls `fixture.Build`.

## Control Flow
The program reads the working directory, asserts the base name is `testdata`, changes up one level, prints each generated filename, and writes it through the default VFS.

## State And Persistence Behavior
Persists fixture SST files under `testdata/<fixture.Filename>`. It does not create commits or update metadata beyond those files.

## Dependencies And Integration Points
Depends on `sstable.TestFixtures`, `vfs.Default`, and CockroachDB errors. It is invoked by the Makefile.

## Risks And Edge Cases
Running from the wrong directory panics. Fixture byte output depends on current writer implementation and compression libraries.

## Test Signals
Console "Generating ..." lines and successful completion indicate regeneration; `writer_fixture_test.go` validates byte equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/testdata/make-table.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tieredmeta/histogram.go -->
# sources/storage-engines/pebble/sstable/tieredmeta/histogram.go

## Purpose
Implements tiering statistics histograms using t-digest sketches to estimate byte distributions by `base.TieringAttribute`.

## Important APIs, Types, And Functions
`digestDelta` configures t-digest compression. `StatsHistogram` stores total bytes/count, no-attribute bytes, and a digest. Methods include `CDF`, `Quantile`, `BytesWithAttr`, `BytesBelowThreshold`, `BytesAboveThreshold`, `encode`, `DecodeStatsHistogram`, and `Merge`. `histogramWriter`, `makeHistogramWriter`, `record`, and `encode` build histograms.

## Control Flow
Writers record `(attribute, bytes)` values, counting attribute zero separately and adding non-zero attributes to the digest weighted by bytes. Encoding writes varints for totals/no-attr/digest size followed by serialized digest data. Decoding reverses the process and validates digest size.

## State And Persistence Behavior
Encoded histograms persist inside tiering histogram blocks. In-memory digest state is mergeable for aggregating file-level statistics.

## Dependencies And Integration Points
Used by `TieringHistogramBlockWriter` and decoding paths in `histogram_block.go`. Depends on `tdigest`, Pebble `base`, binary varints, and corruption errors.

## Risks And Edge Cases
Attribute zero is excluded from digest calculations by design. Decode distinguishes corruption for malformed varints from digest-size mismatch errors. Quantile/CDF accuracy is approximate and controlled by digest compression.

## Test Signals
Histogram round-trip tests verify totals, counts, and zero-byte accounting. Randomized block tests exercise encoded histograms through the block wrapper.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tieredmeta/histogram.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tieredmeta/histogram_block.go -->
# sources/storage-engines/pebble/sstable/tieredmeta/histogram_block.go

## Purpose
Encodes and decodes tiering histogram metadata blocks for SSTables and blob files, including per-span histograms and per-SSTable summary counters.

## Important APIs, Types, And Functions
`KindAndTier` enumerates histogram categories. `Key` combines kind and `TieringSpanID` with encode/decode helpers. `TieringHistogramBlockWriter` supports `Add`, `AddKeyBytes`, `AddHotAndColdBlobRefBytes`, `IsEmpty`, `Finish`, and reset. `SSTableSummary` stores summary counters. `DecodeTieringHistogramBlock` decodes summary and histogram map.

## Control Flow
The writer lazily creates one `histogramWriter` per `(kind, spanID)`, records bytes, separately accumulates summary fields, sorts keys by kind/span ID, encodes them into a columnar key-value block, prefixes summary varints, then resets itself. Decoding reads three summary varints and iterates the columnar key-value block to decode keys and histograms.

## State And Persistence Behavior
The finished byte slice persists in table/blob metadata. Writer state is transient and reusable after `Finish`.

## Dependencies And Integration Points
Depends on `colblk.KeyValueBlockWriter/Decoder`, tiering base types, `StatsHistogram`, and map/slice sorting helpers. It supports future compaction/tiering decisions using persisted metadata.

## Risks And Edge Cases
Key decode rejects too-short or invalid kind values. Empty writers still encode summary zeros plus an empty histogram block if `Finish` is called. Sorting determines deterministic persisted bytes.

## Test Signals
Randomized tests validate summary counters, presence of every expected key, and decoded histogram aggregate fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tieredmeta/histogram_block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tieredmeta/histogram_test.go -->
# sources/storage-engines/pebble/sstable/tieredmeta/histogram_test.go

## Purpose
Randomized tests for tiering histogram block and individual histogram encoding/decoding.

## Important APIs, Types, And Functions
`expectedStats`, `generateRandomRecords`, and `requireStatsEqual` are helpers. `TestHistogramBlock_Randomized` tests full block encode/decode. `TestHistogramEncoding_Roundtrip` tests individual histogram writer round trips.

## Control Flow
Tests create random spans, kinds, attributes, byte counts, key-byte summaries, and hot/cold blob reference bytes. They record expected aggregate totals while writing histograms, encode, decode, and compare summary plus every histogram's total/count/no-attribute accounting.

## State And Persistence Behavior
All state is in memory. Encoded byte slices model persisted tiering metadata blocks.

## Dependencies And Integration Points
Depends on `base.TieringSpanID`, `base.TieringAttribute`, `testutils.RandIntInRange`, `TieringHistogramBlockWriter`, and `DecodeStatsHistogram`.

## Risks And Edge Cases
Random seeds use current time, so failure reproduction requires captured seed/logging not currently present. Tests assert aggregate accounting, not t-digest quantile accuracy.

## Test Signals
Signals are successful decode, matching summary counters, expected histogram map length, and exact aggregate fields for every histogram.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/tieredmeta/histogram_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/valblk/reader.go -->
# sources/storage-engines/pebble/sstable/valblk/reader.go

## Purpose
Implements lazy fetching of values stored in SSTable value blocks, including access while an SSTable iterator is open and fallback access after iterator closure.

## Important APIs, Types, And Functions
Interfaces `ReaderProvider`, `ExternalBlockReader`, and `IteratorBlockReader` abstract block reads. `blockProviderWhenClosed` bridges closed-iterator lazy fetches. `Reader`, `MakeReader`, `GetInternalValueForPrefixAndValueHandle`, and `Close` implement block value construction. `valueBlockFetcher`, `FetchHandle`, `getValueInternal`, `getBlockHandle`, and `fetcherStats` implement actual fetching and caching.

## Control Flow
When a data block value prefix points to a value block, `Reader` lazily allocates a `valueBlockFetcher`, decodes value length and short attribute, and returns a `LazyValue` carrying the remaining handle. Fetching first reads the value-block index if absent, then reads/caches the referenced value block, slices out the requested value, and updates stats. If the fetcher was closed, it temporarily obtains an external reader through `ReaderProvider` and copies the value into caller-owned storage.

## State And Persistence Behavior
Persistent state is the value-block index and value blocks in the SSTable. Reader state caches the index block and last value block, with buffer handles released on close.

## Dependencies And Integration Points
Integrates with block readers, `base.LazyValue`, iterator stats, block category stats, `valblk.IndexHandle`, and `DecodeRemainingHandle`. Called by the SSTable internal value constructor in `values.go`.

## Risks And Edge Cases
Lazy values may outlive iterators, requiring the closed-reader path. Buffer handle lifetime and release ordering are critical. There is no explicit bounds check before slicing the value from a decoded handle, so corrupted indexes/handles depend on lower-level validation or may panic.

## Test Signals
Covered indirectly through SSTable value-block tests and iterator lazy-value behavior. Stats counters offer runtime signals for separated values and fetched bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/valblk/reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/valblk/valblk.go -->
# sources/storage-engines/pebble/sstable/valblk/valblk.go

## Purpose
Documents and implements value-block handle and index encodings for Pebble v3+ SSTables, where older MVCC values may be separated from data blocks for read locality.

## Important APIs, Types, And Functions
`Handle` stores value length, value block number, and offset. `HandleMaxLen`, `EncodeHandle`, `DecodeLenFromHandle`, `DecodeRemainingHandle`, and `DecodeHandle` encode/decode variable-width handles. `IndexHandle` stores the block handle plus fixed field widths. `EncodeIndexHandle`, `DecodeIndexHandle`, `DecodeIndex`, `DecodeBlockHandleFromIndex`, `littleEndianPut`, `lenLittleEndian`, and `littleEndianGet` implement index metadata.

## Control Flow
Data block values store a prefix plus varint handle. Readers can decode length first for lazy-value attributes, then decode remaining block/offset only when fetching. The value index block stores fixed-width rows `(blockNum, blockOffset, blockLength)`, enabling direct lookup by `blockNum * rowWidth`.

## State And Persistence Behavior
Handle bytes persist inside data blocks. Index handles persist in the metaindex. Value index blocks persist in the SSTable and map logical value block numbers to physical block handles.

## Dependencies And Integration Points
Used by value-block writer/reader, block handle encoding, SSTable writer format v3+, and default internal value construction. Depends on Pebble `block` and `base` corruption errors.

## Risks And Edge Cases
Manual unsafe varint decoding assumes valid enough input length. Index decoding validates row length and sequential block numbers. Fixed-width field lengths must fit maximum offsets/lengths selected by the writer.

## Test Signals
Unit tests cover handle encode/decode, index-handle encode/decode, and little-endian helper round trips.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/valblk/valblk.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/valblk/valblk_test.go -->
# sources/storage-engines/pebble/sstable/valblk/valblk_test.go

## Purpose
Tests value-block handle encoding helpers and little-endian fixed-width integer helpers.

## Important APIs, Types, And Functions
`TestHandleEncodeDecode`, `TestValueBlocksIndexHandleEncodeDecode`, and `TestLittleEndianGetPut` exercise `EncodeHandle`, `DecodeHandle`, `EncodeIndexHandle`, `DecodeIndexHandle`, `lenLittleEndian`, `littleEndianPut`, and `littleEndianGet`.

## Control Flow
Each test defines boundary-heavy values, encodes into stack buffers, decodes back, and asserts exact structural equality. The little-endian test computes the minimal byte length before writing and reading.

## State And Persistence Behavior
Tests operate only on in-memory buffers that model persisted handle/index bytes.

## Dependencies And Integration Points
Depends on `block.Handle`, `math`, random values, leaktest, and `testify/require`. Protects encodings consumed by SSTable readers and writers.

## Risks And Edge Cases
The tests cover selected maximum-ish values but not malformed input or every varint length boundary. Decode error paths are lightly covered elsewhere.

## Test Signals
Signals are exact decoded equality and no leaktest failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/valblk/valblk_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/valblk/writer.go -->
# sources/storage-engines/pebble/sstable/valblk/writer.go

## Purpose
Writes value blocks and the value-block index for SSTables that separate values from data blocks.

## Important APIs, Types, And Functions
`Writer`, `bufferedValueBlock`, `NewWriter`, `AddValue`, `Size`, `Finish`, `writeValueBlocksIndex`, `Release`, `WriterStats`, and `LayoutWriter` are the main APIs. `valueBlockWriterPool` reuses writers.

## Control Flow
`AddValue` appends non-empty values to the current uncompressed buffer, flushing it through `compressAndFlush` when the block flush governor says it would grow too large. `Finish` flushes the final block, writes buffered physical value blocks through `LayoutWriter`, converts relative handles to file offsets, computes compact field widths, writes the metadata index block, and returns stats. `Release` frees blocks/buffers and returns the writer to the pool.

## State And Persistence Behavior
The writer buffers compressed value blocks in memory until final layout order is known. Persisted output is a sequence of value blocks plus a metadata index block. `WriterStats` records block/value counts and total value-block/index size.

## Dependencies And Integration Points
Depends on block flush governance, physical block maker, block kinds, `valblk.IndexHandle`, and SSTable layout writer methods. Used by raw SSTable writers when value separation is enabled.

## Risks And Edge Cases
All finished value blocks are retained in memory until `Finish`, creating memory pressure for many separated values. Empty values are rejected only under invariants. Errors during layout writes must release owned physical blocks through the layout contract.

## Test Signals
Direct unit tests cover lower-level encodings; end-to-end value-block writer behavior is covered indirectly by SSTable writer tests with value separation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/valblk/writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/values.go -->
# sources/storage-engines/pebble/sstable/values.go

## Purpose
Defines how SSTable iterators construct `base.InternalValue` instances from encoded value prefixes and handles, including in-place values, value-block handles, and external blob handles.

## Important APIs, Types, And Functions
`AssertNoBlobHandles`, `DebugHandlesBlobContext`, `LoadValBlobContext`, `BlobReferences`, `TableBlobContext`, and `defaultInternalValueConstructor.GetInternalValueForPrefixAndValueHandle` are key APIs. The constructor embeds blob context, read env, `valblk.Reader`, and a reusable lazy fetcher.

## Control Flow
If the value prefix indicates a value-block handle, the method delegates to `valblk.Reader`. If it indicates a blob handle, it decodes the inline handle preface, optionally returns a debug representation, resolves blob reference IDs to file IDs, sets lazy-fetcher metadata and stats, and returns a `LazyValue` carrying the handle suffix.

## State And Persistence Behavior
Persistent state is encoded in SSTable value bytes and blob reference metadata. Runtime state includes lazy fetchers, blob contexts, and iterator stats. `LoadValBlobContext` creates a blob `ValueFetcher` that the caller must close.

## Dependencies And Integration Points
Integrates SSTable block iterators with value-block reader, blob reader/provider code, `base.LazyValue`, iterator stats, and manifest blob references.

## Risks And Edge Cases
Missing blob references cause assertion panics unless a debug handle function is installed. `AssertNoBlobHandles` intentionally panics on unexpected external blobs. Lazy fetcher reuse means returned internal values must respect documented lifetimes or be cloned.

## Test Signals
Covered by SSTable/blob/value-block tests and debug formatting paths. Runtime stats for separated point values indicate construction/fetch behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/values.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/virtual/virtual_reader_params.go -->
# sources/storage-engines/pebble/sstable/virtual/virtual_reader_params.go

## Purpose
Defines the bounds and file number metadata needed to read a virtual SSTable and constrains requested spans to virtual bounds.

## Important APIs, Types, And Functions
`VirtualReaderParams` contains `Lower`, `Upper`, and `FileNum`. `ConstrainBounds(start, end, endInclusive, compare)` returns whether the last key is inclusive plus constrained first/last user keys.

## Control Flow
The method raises the start bound to the virtual lower bound if needed. It initializes the last bound from the virtual upper key and inclusivity from the upper sentinel kind, then narrows it with the caller end bound when the caller end is inside or equal to the virtual upper bound.

## State And Persistence Behavior
The struct carries manifest/reader metadata for virtual table views. The method is pure and does not persist state.

## Dependencies And Integration Points
Depends on `base.InternalKey`, file numbers, and comparer functions. Used by virtual SSTable reader paths to map physical table bounds to virtual spans.

## Risks And Edge Cases
The TODO notes undefined behavior if caller bounds are completely outside virtual bounds. Inclusivity handling depends on `Upper.IsExclusiveSentinel`.

## Test Signals
No direct tests in this file; coverage is expected through virtual SSTable reader behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/virtual/virtual_reader_params.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/write_queue.go -->
# sources/storage-engines/pebble/sstable/write_queue.go

## Purpose
Implements the asynchronous write queue used by row-format SSTable writing to preserve write ordering while allowing data block compression to happen separately.

## Important APIs, Types, And Functions
`writeTask` carries compressed data block buffers, index block state, separator keys, inflight size accounting, and a reusable `compressionDone` channel. `writeQueue` owns a task channel, worker goroutine, writer pointer, error state, and close flag. Methods include `clear`, `newWriteQueue`, `performWrite`, `releaseBuffers`, `runWorker`, `addSync`, and `finish`.

## Control Flow
Compression producers enqueue tasks whose `compressionDone` channel is signaled when physical block bytes are ready. The queue worker waits for that signal, writes the precompressed data block, adds the corresponding index entry, records the first error, and releases pooled buffers/tasks. `addSync` performs the same flow inline before asynchronous queue use. `finish` closes the channel and waits for the worker.

## State And Persistence Behavior
Persistent effects are data block writes and index entries through `RawRowWriter.layout` and `addIndexEntry`. Queue state is transient and manages buffer/task pool ownership.

## Dependencies And Integration Points
Integrated with `RawRowWriter`, `dataBlockBuf`, `indexBlockBuf`, block handles/properties, and writer pools. Depends on `sync`.

## Risks And Edge Cases
Task channel reuse requires compression signals to be drained before pooling. Once an error occurs, later blocks skip writes but still release buffers. `addSync` is valid only before asynchronous `add` usage, per comment.

## Test Signals
Covered indirectly by writer round-trip, fixture byte equality, and final-block tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/write_queue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/writer.go -->
# sources/storage-engines/pebble/sstable/writer.go

## Purpose
Defines the public SSTable writer facade, raw writer selection, range-key fragmentation, writer metadata, raw writer interface, and a testing logging wrapper.

## Important APIs, Types, And Functions
`NewRawWriter`, `NewRawWriterWithCPUMeasurer`, `Writer`, `NewWriter`, `Set`, `Delete`, `DeleteRange`, `Merge`, `RangeKeySet`, `RangeKeyUnset`, `RangeKeyDelete`, `Close`, `Metadata`, `RawWriter`, `WriterMetadata`, metadata setter methods, and `LoggingRawWriter` are the main exports.

## Control Flow
Raw writer creation chooses row writer for formats through Pebble v4 and columnar writer for newer formats. `NewWriter` configures a keyspan fragmenter for range keys. Point methods validate accumulated errors and strict-obsolete mode before delegating to the raw writer. Range-key methods copy caller bytes into an internal buffer, add spans to the fragmenter, and emit sorted fragmented spans through `encodeFragmentedRangeKeySpan`. `Close` finishes the fragmenter before closing the raw writer.

## State And Persistence Behavior
The writer persists point keys, range deletions, range keys, filters, indexes, and metadata through the selected raw writer. It keeps transient range-key buffers, fragmenter state, accumulated errors, and metadata until close.

## Dependencies And Integration Points
Integrates with object storage writables, row/column raw writers, keyspan fragmentation, blob handles, block handles, table format selection, CPU measurement, and higher-level ingestion/external SST construction.

## Risks And Edge Cases
Strict-obsolete writers reject public point helpers and require lower-level force-obsolete calls. Range key spans must be added in start-key order and have start < end. Returned internal buffers retain copied range-key bytes for writer lifetime. Metadata largest keys are not final until close.

## Test Signals
Covered by writer round-trip tests, range-key datadriven tests, fixture output tests, and lower-level raw writer tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/writer_fixture_test.go -->
# sources/storage-engines/pebble/sstable/writer_fixture_test.go

## Purpose
Verifies current fixture-building code reproduces prebuilt SSTable fixture files byte-for-byte.

## Important APIs, Types, And Functions
`runTestFixtureOutput` builds one fixture in memory, optionally rewrites testdata when `--rewrite` is present, and compares bytes. `TestFixtureOutput` iterates `TestFixtures` and skips zstd byte equality when the standard zstd library is unavailable.

## Control Flow
For each fixture, the test reads expected bytes from `testdata`, builds a new SST in memory through `fixture.Build`, reads all generated bytes, optionally rewrites the fixture file, otherwise compares and writes `fail.txt` on mismatch.

## State And Persistence Behavior
Normal test runs only read testdata and write an in-memory SST, except mismatches write `fail.txt`. With `--rewrite`, it persists regenerated fixture bytes to `testdata`.

## Dependencies And Integration Points
Depends on fixture metadata/builders, VFS, compression library selection, and writer deterministic output.

## Risks And Edge Cases
Byte equality is sensitive to compression implementation differences, so zstd is conditionally skipped. Rewriting fixtures is controlled by process args and should be used intentionally.

## Test Signals
Exact byte equality is the primary signal; mismatch diagnostics include first differing byte and hex dumps.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/writer_fixture_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/writer_rangekey_test.go -->
# sources/storage-engines/pebble/sstable/writer_rangekey_test.go

## Purpose
Datadriven tests for public `Writer` range-key APIs across supported table formats.

## Important APIs, Types, And Functions
`TestWriter_RangeKeys` builds SSTables from datadriven `SET`, `UNSET`, and `DEL` commands, then reads raw range-key spans. It uses `testkeys.Comparer`, `colblk.DefaultKeySchema`, `NewWriter`, `RangeKeySet`, `RangeKeyUnset`, `RangeKeyDelete`, and `NewRawRangeKeyIter`.

## Control Flow
For each table format from Pebble v2 through max, a `build` command writes range-key operations to an in-memory SST. After each operation, the input byte slices are scrambled to detect incorrect caller-slice retention. The table is closed, reopened, and raw range-key spans are iterated and printed.

## State And Persistence Behavior
Each build creates an in-memory SSTable. The writer's internal range-key copy buffer is implicitly validated by scrambling original slices after calls.

## Dependencies And Integration Points
Exercises `Writer` range-key fragmentation, key schema selection, row/column format differences, reader range-key iterators, datadriven testdata, and virtual filesystem.

## Risks And Edge Cases
The test depends on datadriven expected output for fragmented/coalesced spans. It focuses on range keys and does not mix point keys or range deletions in the same built table.

## Test Signals
Exact datadriven output, absence of slice-aliasing corruption, and successful iteration across all table formats are the signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/writer_rangekey_test.go -->
