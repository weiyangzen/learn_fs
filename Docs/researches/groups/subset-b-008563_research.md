# Research: subset-b-008563

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/setup_centos7.sh -->
# sources/storage-engines/rocksdb/build_tools/setup_centos7.sh

## Purpose
This Bash provisioning script configures a CentOS 7 style host, apparently a Vagrant environment, to build and smoke-test RocksDB 6.7.3 with compression dependencies. It installs system packages, builds zstd 1.4.4 from source, expands RocksDB into `/usr/local`, and compiles the static library plus examples.

## Important APIs, functions, and control flow
The script is linear and uses `set -ex`, so every command is echoed and any failing command terminates the run. It declares `ROCKSDB_VERSION` and `ZSTD_VERSION`, updates yum, installs EPEL and packages such as `gcc-c++`, `snappy-devel`, `zlib-devel`, `bzip2-devel`, `lz4-devel`, `libasan`, and `gflags`, then creates `/usr/local/rocksdb-${ROCKSDB_VERSION}` and symlinks `/usr/local/rocksdb`. It downloads GitHub release tarballs into `/tmp`, builds zstd with `make && make install`, changes ownership of the RocksDB tree to `vagrant:vagrant`, runs `sudo -u vagrant make static_lib`, builds examples, and runs `c_simple_example`.

## State, persistence, and dependencies
Persistent state is installed into system package databases, `/usr/local/lib`, `/usr/local/rocksdb-*`, and the `/usr/local/rocksdb` symlink. It assumes yum, internet access to GitHub, `sudo`, a `vagrant` user, and write access to `/usr/local` and `/tmp`. It also assumes RocksDB 6.7.3 still builds with the installed CentOS toolchain and the manually installed zstd.

## Integration points
This is not used by cache runtime code; it is a build/bootstrap utility for older CentOS environments. It integrates with RocksDB's make build, examples directory, and system dynamic library path through `LD_LIBRARY_PATH=/usr/local/lib/` for examples.

## Risks and test signals
The hard-coded versions are old, GitHub download URLs are mutable network dependencies, and the `vagrant` user assumption makes the script unsuitable for generic CentOS hosts without edits. `ln -sfT` and `chown -R` affect global `/usr/local` state. A successful smoke signal is completion of `make static_lib`, `make all` in `examples/`, and `./c_simple_example` under the `vagrant` account.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/setup_centos7.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/ubuntu20_image/Dockerfile -->
# sources/storage-engines/rocksdb/build_tools/ubuntu20_image/Dockerfile

## Purpose
This Dockerfile defines a RocksDB CI/build image based on Ubuntu 20.04. It installs compilers, compression libraries, Java, MinGW, gtest-parallel, libprotobuf-mutator, and Google Benchmark for regular builds, sanitizer/fuzzer workflows, benchmark builds, and cross-platform checks.

## Important APIs, functions, and control flow
The image is built through Docker `RUN` layers. It updates and upgrades apt packages, installs basic tools, configures `tzdata` noninteractively, installs default GCC/G++/Clang tooling, package management helpers, `libgflags-dev`, `libtbb-dev`, compression dev packages, `cmake`, and `libssl-dev`. It downloads `llvm.sh` from apt.llvm.org and installs clang-13, installs GCC 7, 8, 10, and 11 through the Ubuntu toolchain PPA, installs Valgrind, `libgoogle-glog-dev`, OpenJDK 8 with `JAVA_HOME`, and MinGW. It clones `google/gtest-parallel` onto `PATH`, then builds `google/libprotobuf-mutator` at branch `v1.0` pinned to commit `ffd86a3...` with clang-13 and Ninja, exposes `PKG_CONFIG_PATH` and `PROTOC_BIN`, builds Google Benchmark v1.7.0, and removes apt lists and the benchmark source checkout.

## State, persistence, and dependencies
Persistent image state includes apt packages, LLVM/GCC toolchains, `/root/gtest-parallel`, `/root/libprotobuf-mutator`, `/usr/local` installs for libprotobuf-mutator and benchmark, and environment variables for Java, `PATH`, protobuf pkg-config, and `protoc`. It depends heavily on external apt repositories, GitHub, the Ubuntu toolchain PPA, and apt.llvm.org.

## Integration points
The image supports RocksDB's make/CMake builds, gtest-parallel test execution, fuzzers needing libprotobuf-mutator and bundled protobuf, benchmark targets needing Google Benchmark, Java API builds, Valgrind checks, and MinGW compilation.

## Risks and test signals
Risks include unpinned package upgrades, branch `master` for gtest-parallel, reliance on old OpenJDK 8 packages, and no apt cache cleanup until the end, which enlarges intermediate layers. The PPA and LLVM installer are external trust and availability points. Test by building the image, compiling RocksDB with default GCC and clang-13, running gtest-parallel, building fuzzers against `PROTOC_BIN`, and linking benchmark targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/ubuntu20_image/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/ubuntu22_image/Dockerfile -->
# sources/storage-engines/rocksdb/build_tools/ubuntu22_image/Dockerfile

## Purpose
This Dockerfile defines a publishable RocksDB Ubuntu 22.04 build image, with inline instructions for building and pushing `ghcr.io/facebook/rocksdb_ubuntu:22.2`. It modernizes compiler coverage while preserving clang-13/fuzzer compatibility.

## Important APIs, functions, and control flow
The comment header documents GHCR login, build, push, and visibility steps. The Docker body starts from `ubuntu:22.04`, updates and upgrades apt, installs `vim`, `wget`, `curl`, `ccache`, timezone data, compilers, package helpers, gflags/TBB/compression/CMake/OpenSSL. It installs clang-13 through `llvm.sh`, installs `libc++-13-dev` and `libc++abi-13-dev`, then purges clang-14 to avoid libc++/libstdc++ confusion with C++20. It installs GCC 10 and GCC 13 from the toolchain PPA, Valgrind, and builds glog v0.7.1 from source because the packaged dependency path lacks compatible libunwind. It adds OpenJDK 8, MinGW, gtest-parallel, libprotobuf-mutator pinned to commit `ffd86a3...` built with clang-13, and Google Benchmark v1.7.0, then removes apt lists.

## State, persistence, and dependencies
Persistent image state includes the compiler matrix, ccache, source-built glog in `/usr/local`, gtest-parallel under `/root`, libprotobuf-mutator/protobuf build artifacts, benchmark install files, and Java/protobuf environment variables. Network dependencies include Docker Hub base image pulls, apt.llvm.org, Ubuntu archives, the toolchain PPA, GitHub, and GHCR for publication.

## Integration points
The image is an official-ish RocksDB CI image used by build scripts and human release workflows. It integrates with C++20 clang/libc++ testing, GCC version testing, fuzzers, benchmark builds, Java builds, and cross-compile checks.

## Risks and test signals
Risks include hand-built glog needing `-DGLOG_USE_GLOG_EXPORT` in consumers, fragility of OpenJDK 8 availability on Jammy, unpinned package updates, and stale image tag instructions if GHCR naming changes. Test by building the image from `build_tools/ubuntu22_image`, compiling RocksDB under GCC 10/13 and clang-13 with libc++, running representative unit tests, building fuzzers and benchmark targets, and verifying glog-dependent folly paths link.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/ubuntu22_image/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/ubuntu24_image/Dockerfile -->
# sources/storage-engines/rocksdb/build_tools/ubuntu24_image/Dockerfile

## Purpose
This Dockerfile defines a RocksDB Ubuntu 24.04 build image and documents publishing it as `ghcr.io/facebook/rocksdb_ubuntu:24.1`. It tracks newer Ubuntu defaults, newer GCC, and an LLVM snapshot clang-21 path while keeping common RocksDB CI dependencies.

## Important APIs, functions, and control flow
The comments mirror the Ubuntu 22 image publishing workflow. The Docker build starts from `ubuntu:24.04`, updates/upgrades apt, installs basics plus ccache, timezone data, default GCC/G++/Clang tooling, then adds the LLVM snapshot apt key and `llvm-toolchain-noble-21` repository to install clang-21. It installs package helpers, gflags, TBB, compression libraries, CMake, OpenSSL, GCC/G++ 12 and 14, Valgrind, `libgoogle-glog-dev`, OpenJDK 8, MinGW, gtest-parallel, libprotobuf-mutator pinned to commit `ffd86a3...` using default clang/clang++, Google Benchmark v1.7.0, and removes apt lists.

## State, persistence, and dependencies
The image persists apt repository configuration under `/etc/apt`, LLVM GPG material under trusted keyrings, multiple compiler versions, Java configuration, `/root/gtest-parallel`, libprotobuf-mutator build artifacts, and `/usr/local` installs. It depends on Ubuntu Noble package availability, apt.llvm.org snapshot packages, GitHub source repositories, and GHCR for distribution.

## Integration points
It supports RocksDB testing on the newest supported Ubuntu baseline, including compiler matrix runs with GCC 12/14 and clang-21, fuzzing, benchmarks, Java builds, and MinGW targets. Because libprotobuf-mutator is built with default clang instead of a versioned clang, it follows the image default compiler state more closely than the 20/22 images.

## Risks and test signals
OpenJDK 8 on Ubuntu 24.04 can be availability-sensitive. The LLVM snapshot repository and clang-21 are moving external dependencies. `libgoogle-glog-dev` is packaged here, unlike the Ubuntu 22 source-build workaround, so folly/glog behavior can differ between images. Test by building the image, compiling RocksDB with GCC 12/14 and clang-21, running unit tests, building fuzzers and benchmarks, checking Java builds, and verifying Docker push instructions still match the intended GHCR tag.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/ubuntu24_image/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/update_dependencies.sh -->
# sources/storage-engines/rocksdb/build_tools/update_dependencies.sh

## Purpose
This shell script generates `dependencies_platform010.sh` from Meta internal `third-party2` library locations. It captures concrete compiler and library base paths for a platform010/centos8-native RocksDB build environment.

## Important APIs, functions, and control flow
The script sets `BASEDIR=$(dirname $0)`, `TP2_LATEST=/data/users/$USER/fbsource/fbcode/third-party2/`, and writes to `$BASEDIR/dependencies_platform010.sh`. `log_header()` writes a copyright and generated-file note. `log_variable()` appends `NAME=value` for a shell variable using indirect expansion. `get_lib_base(lib, version, platform)` locates a library under third-party2: it chooses latest version when `LATEST` or blank, chooses latest `gcc-*[^fb]` platform when no platform is passed, resolves the first leaf directory with `readlink -f`, converts the library name to an uppercase `_BASE` variable name, assigns it with `eval`, and logs it.

The main body deletes/recreates the output file, logs compiler bases for GCC 11.x and llvm-fb 15, then logs bases for libgcc, glibc, snappy, zlib, bzip2, lz4, zstd, gflags, jemalloc, numa, libunwind, tbb, liburing, benchmark, kernel headers, binutils, and Valgrind. It ends with `git diff $OUTPUT`.

## State, persistence, and dependencies
The generated state is a shell fragment under `build_tools/dependencies_platform010.sh`. It depends on internal Meta filesystem layout, GNU `ls -v`, `readlink -f`, Bash features despite the shebang being `/bin/sh`, and a git checkout for the final diff. It mutates only the generated dependency file.

## Integration points
The generated dependency file is likely sourced by RocksDB internal build scripts that need fixed third-party roots. The variables form a contract: `GCC_BASE`, `CLANG_BASE`, `LIBGCC_BASE`, `GLIBC_BASE`, `SNAPPY_BASE`, and similar uppercase names.

## Risks and test signals
The `/bin/sh` shebang is risky because the script uses Bash-only `function`, `${var^^}`, and indirect expansion. The `eval` assignment is sensitive to whitespace or unusual path characters, and `ls | head` silently chooses arbitrary first matches if the tree shape changes. Test by running under Bash in the internal environment, confirming the generated shell fragment sources cleanly, reviewing `git diff`, and building an internal platform010 RocksDB target using the produced paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/update_dependencies.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/version.sh -->
# sources/storage-engines/rocksdb/build_tools/version.sh

## Purpose
This Bash helper prints RocksDB version components from `include/rocksdb/version.h`. It supports release scripts and build tooling that need `major`, `minor`, `patch`, or full semantic version text.

## Important APIs, functions, and control flow
The script requires one argument and prints usage for no arguments. For `major`, `minor`, and `patch`, it greps the first matching macro line and prints the third token with awk. For `full`, it scans `#define ROCKSDB...` lines into an awk map and prints `ROCKSDB_MAJOR.ROCKSDB_MINOR.ROCKSDB_PATCH`.

## State, persistence, and dependencies
It is read-only and depends on being run from the repository root or another working directory where `include/rocksdb/version.h` resolves. It depends on `grep`, `head`, and `awk`.

## Integration points
Release packaging, Docker tagging, or build scripts can call it as `build_tools/version.sh full` or one component at a time. It uses the public version header as the source of truth.

## Risks and test signals
Unknown arguments silently produce no output but exit 0, which can mask caller mistakes. Grep patterns are broad and could match unexpected macro names if the header changes. Test by comparing all four outputs to `include/rocksdb/version.h` and checking caller behavior on invalid arguments.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/build_tools/version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache.cc -->
# sources/storage-engines/rocksdb/cache/cache.cc

## Purpose
This file implements shared `Cache` and `SecondaryCache` factory/parsing behavior plus generic cache item helpers and default async-lookup behavior. It is part of RocksDB's cache abstraction layer rather than a concrete cache implementation.

## Important APIs, types, and functions
It defines `kNoopCacheItemHelper`, `kSliceCacheItemHelper`, and internal helper callbacks for slices. `lru_cache_options_type_info` maps string options to `LRUCacheOptions` fields such as capacity, shard bits, strict capacity, and priority-pool ratios. `comp_sec_cache_options_type_info` maps options for `CompressedSecondaryCacheOptions`.

`SecondaryCache::CreateFromString()` recognizes `compressed_secondary_cache://` URIs, parses the remaining option string through `OptionTypeInfo::ParseStruct`, and calls `NewCompressedSecondaryCache`; otherwise it delegates to `LoadSharedObject<SecondaryCache>`. `Cache::CreateFromString()` recognizes `null`, numeric capacity strings, `key=value` LRU option strings, and shared-object URIs. Async helpers implement synchronous fallback: `StartAsyncLookup()` calls `Lookup()`, `Wait()` calls `WaitAll()`, `WaitAll()` asserts that derived pending handles have been detached from pending caches, and `SetEvictionCallback()` stores a single callback with an assertion against overwriting non-empty callbacks.

## Control flow, state, and persistence
Factory methods create in-memory cache objects only. The slice helper has a no-op deleter that asserts if used, size/save callbacks for persisting slice bytes, and a create callback that is intentionally unsupported. Async lookup state lives in `AsyncLookupHandle`: base `Cache` implementations complete immediately by setting `result_handle`; derived caches can set `pending_handle`.

## Dependencies and integration points
The file integrates `rocksdb/cache.h`, `cache/lru_cache.h`, compressed secondary cache construction, customizable shared object loading, and options parsing infrastructure. It is used by option-string configuration paths, cache benchmarks, DB options parsing, and secondary-cache warming paths that need a `CacheItemHelper`.

## Risks and test signals
Factory parsing is string-sensitive; malformed LRU or secondary-cache option strings must return meaningful `Status` without partially swapping results. `kSliceCacheItemHelper` is safe only for borrowed slice-like objects because its deleter asserts. Async base behavior is intentionally synchronous, so derived implementations must preserve the pending-handle contract. Test via option parsing, URI loading, LRU creation, compressed secondary cache creation, async lookup tests, and secondary-cache save/create paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_bench.cc -->
# sources/storage-engines/rocksdb/cache/cache_bench.cc

## Purpose
This is the executable entry point for the cache benchmark tool. It compiles either a stub that tells users to install gflags or, when `GFLAGS` is enabled, delegates to the real benchmark implementation in `cache_bench_tool.cc`.

## Important APIs, functions, and control flow
Without `GFLAGS`, `main()` writes `Please install gflags to run rocksdb tools` to stderr and exits 1. With `GFLAGS`, `main(int argc, char** argv)` calls `ROCKSDB_NAMESPACE::cache_bench_tool(argc, argv)` and returns its status.

## State, persistence, and dependencies
The file has no persistent state. Its key dependency is the compile-time `GFLAGS` macro and the declaration of `cache_bench_tool` from `rocksdb/cache_bench_tool.h`.

## Integration points
Build targets for `cache_bench` link this file with the larger benchmark tool when gflags is available. It lets the source tree provide a graceful failure binary in builds without gflags support.

## Risks and test signals
The main risk is build configuration drift: if the binary is expected to benchmark but `GFLAGS` is absent, the stub exits immediately. Test signals are successful linking in both configurations and correct CLI delegation when `GFLAGS` is defined.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_bench.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_bench_tool.cc -->
# sources/storage-engines/rocksdb/cache/cache_bench_tool.cc

## Purpose
This file implements RocksDB's cache benchmark and two embedded stress tools. The default mode measures concurrent cache operations under configurable cache type, workload mix, key skew, pinning, capacity variation, secondary cache, allocator, and stats-gathering settings. `-stress_cache_key` simulates cache-key collision probabilities. `-stress_cache_instances=N` measures repeated cache construction/destruction cost.

## Important APIs, types, and functions
The tool is compiled only when `GFLAGS` is defined and exposes `int cache_bench_tool(int argc, char** argv)`. Global flags configure thread count, cache size, shard bits, HyperClock eviction effort, resident ratio, operation count, value sizes, compression ratio, degenerate hash bits, skew, population, pinning, capacity variation, operation percentages, stats collection, sleeps, lean mode, histograms, problem reporting, seed, secondary cache URI, cache type, jemalloc no-dump allocator, and the two stress subtools.

Key internal types are `SharedState`, which coordinates benchmark thread start/finish and aggregates lookup/pinned stats; `ThreadState`, which holds per-thread RNG, histogram, and duration; `KeyGen`, which emits 16-byte cache keys with optional hash-bit degeneracy for HyperClock collision stress; and `CacheBench`, which owns the cache and workload thresholds. Helper callbacks `SizeFn`, `SaveToFn`, `CreateFn`, and `DeleteFn` make inserted values compatible with secondary cache persistence and promotion, with three `CacheItemHelper`s using data/index/filter roles.

`CacheBench::MakeCache()` builds LRU, fixed HyperClock, auto HyperClock, or default HyperClock caches, optionally with `JemallocNodumpAllocator` and a configured secondary cache. `PopulateCache()` inserts until occupancy stops increasing. `Run()` starts worker threads, optionally starts a stats thread, computes throughput and histograms, reports cache load factor/pinned count, and calls `ReportProblems()`. `OperateCache()` executes the configured operation mix: lookup+insert, insert with retained handle, blind insert, lookup, erase, optional `SetCapacity`, sleep, hash value consumption, and bounded pinned-handle release. `StatsBody()` repeatedly calls `ApplyToAllEntries()` outside the coordination mutex and reports entry counts, charge, key size, table occupancy, helper diversity, and collection latency.

`StressCacheKey` simulates many DB/session/process/file generations, converts `TableProperties` to base cache keys through `BlockBasedTable::SetupBaseCacheKey()`, reduces keys to a configurable bit width, tracks live-file representatives in a hash table, and extrapolates observed collisions. `StressCacheInstances` creates and clears many caches over ten iterations and prints average create/destroy times.

## Control flow, state, and persistence
Default execution parses flags, initializes a random seed from process ID when needed, constructs `CacheBench`, optionally populates the cache, then runs the concurrent benchmark. Worker threads are detached but synchronized by `SharedState`; the stats thread is joined after foreground workers complete. State is in-memory only: cache entries allocated through RocksDB allocators, pinned `Cache::Handle*` deques, histograms, and stress simulation arrays. There is no persistent output beyond stdout/stderr.

## Dependencies and integration points
The tool integrates concrete cache creation (`NewLRUCache`, HyperClock options), sharded cache internals for load factor, secondary cache URI parsing, block-based table cache-key setup, RocksDB DB session ID generation, histogram/statistics utilities, distributed mutex reporting, gflags, stack traces, system clock, and optional jemalloc no-dump allocator. It exercises cache item helper roles and secondary-cache save/create callbacks under load.

## Risks and test signals
Operation percentages must sum to 100 or the constructor exits. Some configurations intentionally stress unsupported or pathological cases, such as old `clock_cache`, degenerate hash bits, imprecise value-size estimates, or capacity variation near pinned ratio. The `SharedState::AddLookupStats` implementation shadows `pinned_count_` with the parameter name and therefore does not aggregate pinned count as intended. Stress extrapolation depends on simplifying assumptions documented in the file. Test signals include stable completion under LRU and HyperClock, meaningful hit ratio/load factor/histograms, successful secondary-cache promotion when URI is set, no `ReportProblems()` findings, and plausible halving of collision rates when `sck_keep_bits` increases.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_bench_tool.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_entry_roles.cc -->
# sources/storage-engines/rocksdb/cache/cache_entry_roles.cc

## Purpose
This file defines human-readable names for RocksDB cache entry roles and string keys used when reporting block cache entry statistics.

## Important APIs, types, and functions
It defines `kCacheEntryRoleToCamelString` and `kCacheEntryRoleToHyphenString`, each sized to `kNumCacheEntryRoles`, covering data blocks, filter blocks, index blocks, write buffer, compression dictionary building buffers, filter construction, table readers, file metadata, blob roles, and misc. `GetCacheEntryRoleName(CacheEntryRole)` returns the hyphenated role name. `BlockCacheEntryStatsMapKeys` returns stable map keys for cache id, capacity, last collection duration, last collection age, per-role entry counts, per-role used bytes, and per-role used percent.

## Control flow, state, and persistence
Most functions return static strings or construct prefixed strings using a local helper. There is no mutable persistent state. Returned references for fixed keys point to function-local static strings; role-derived keys are returned by value.

## Dependencies and integration points
This code integrates with `rocksdb/cache.h` role enums and block cache stats reporting. It is consumed by tools and DB properties that need stable textual keys such as `count.data-block`, `bytes.index-block`, and `percent.blob-cache`.

## Risks and test signals
The arrays must stay in enum order and size-compatible with `kNumCacheEntryRoles`; adding a role without updating both arrays would mislabel stats. String keys are external-facing and should be treated as compatibility-sensitive. Test via stats collection outputs and any tests that compare role names or map keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_entry_roles.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_entry_roles.h -->
# sources/storage-engines/rocksdb/cache/cache_entry_roles.h

## Purpose
This header declares the role-name arrays defined in `cache_entry_roles.cc`, making cache entry role labels available to other RocksDB components.

## Important APIs, types, and functions
It includes `<array>`, `<cstdint>`, and `rocksdb/cache.h`, then declares `extern std::array<std::string, kNumCacheEntryRoles> kCacheEntryRoleToCamelString` and `kCacheEntryRoleToHyphenString` in the RocksDB namespace.

## Control flow, state, and persistence
There is no control flow. The declarations expose global arrays whose storage is in the `.cc` file.

## Dependencies and integration points
Consumers that need direct role-name arrays include stats formatters, diagnostics, and tests. The header depends on `CacheEntryRole` and `kNumCacheEntryRoles` being visible from `rocksdb/cache.h`.

## Risks and test signals
The header uses `std::string` without including `<string>` directly, relying on transitive includes; this is usually stable through `rocksdb/cache.h` but is a include-hygiene risk. Test by compiling consumers under stricter include checks and verifying role-name arrays link exactly once.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_entry_roles.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_entry_stats.h -->
# sources/storage-engines/rocksdb/cache/cache_entry_stats.h

## Purpose
This templated header provides `CacheEntryStatsCollector<Stats>`, a reusable mechanism for collecting expensive cache-entry statistics through `Cache::ApplyToAllEntries()` while sharing and caching recent results per `Cache` instance.

## Important APIs, types, and functions
The `Stats` template contract requires `BeginCollection(Cache*, SystemClock*, uint64_t)`, `GetEntryCallback()`, `EndCollection(Cache*, SystemClock*, uint64_t)`, and `SkippedCollection()`, plus copyability and trivial construction. `CollectStats(min_interval_seconds, min_interval_factor)` serializes collectors with `working_mutex_`, computes a maximum acceptable cached-result age from an absolute interval and a multiple of the previous collection duration, scans the cache when stale, or calls `SkippedCollection()` when recent enough. It copies working stats into `saved_stats_` under `saved_mutex_`. `GetStats()` returns the saved copy. `GetShared()` stores a single collector object inside the cache using `BasicTypedCacheInterface<CacheEntryStatsCollector, CacheEntryRole::kMisc>` and a process-lifetime `CacheKey`, with a static mutex to avoid duplicate insert races, then returns an aliasing `shared_ptr` via `SharedGuard()`.

## Control flow, state, and persistence
State is in-memory and per cache: saved stats, working stats, last start/end timestamps, the raw cache pointer, and a clock pointer. The collector object is itself held as a cache entry with zero charge, so its lifetime is tied to cache handles/shared guards. The initial `last_end_time_micros_` value is pessimistic, helping first-collection age logic.

## Dependencies and integration points
The collector integrates with typed cache wrappers, `CacheKey::CreateUniqueForProcessLifetime()`, system clocks, `ApplyToAllEntries`, and test sync points. It supports block cache property collectors that would otherwise each rescan the whole cache for every DB or column family sharing a cache.

## Risks and test signals
The raw `Cache*` and `SystemClock*` must outlive collector use. Zero charge avoids flaky cache-usage tests but means metadata accounting understates the collector. `GetShared()` still has a lookup/insert race without the static mutex; that mutex is global per template instantiation. Test by concurrent callers sharing one cache, repeated stats calls within and beyond the min interval, and cache destruction with outstanding shared guards.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_entry_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_helpers.cc -->
# sources/storage-engines/rocksdb/cache/cache_helpers.cc

## Purpose
This file implements small cache helper utilities for releasing handles through `Cleanable` callbacks and warming serialized cache entries back into a cache.

## Important APIs, types, and functions
`ReleaseCacheHandleCleanup(void* arg1, void* arg2)` casts `arg1` to `Cache*` and `arg2` to `Cache::Handle*`, asserts both are non-null, and calls `cache->Release(handle)`. `WarmInCache()` calls a `CacheItemHelper`'s `create_cb` with saved bytes, no compression, volatile tier, a create context, and the cache memory allocator, then inserts the resulting object into the cache with the helper, charge, and priority; it optionally returns the charge.

## Control flow, state, and persistence
`WarmInCache()` creates transient in-memory cache objects from persisted or serialized bytes. It does not persist data itself. If object creation fails, insertion is skipped and the error status is returned.

## Dependencies and integration points
These helpers integrate `Cache`, `Cleanable`, cache item helper callbacks, memory allocators, and secondary/persistent cache warmup paths. `ReleaseCacheHandleCleanup` is used by RAII wrappers that transfer handle ownership into RocksDB cleanup chains.

## Risks and test signals
`WarmInCache()` assumes `helper` and `helper->create_cb` are valid and asserts otherwise; callers must not pass helpers like no-op slice helpers that cannot recreate objects. If insertion fails after creation, ownership and deleter semantics depend on `Cache::Insert()` behavior. Test with secondary-cache promotion/warming, custom helpers, and cleanup transfer paths under ASAN/valgrind.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_helpers.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_helpers.h -->
# sources/storage-engines/rocksdb/cache/cache_helpers.h

## Purpose
This header defines generic cache-handle utilities, including typed value extraction, pointer-to-slice keys, a movable RAII handle guard, aliasing shared-pointer construction, and the `WarmInCache()` declaration.

## Important APIs, types, and functions
`GetFromCacheHandle<T>()` returns `static_cast<T*>(cache->Value(handle))`. `GetSliceForKey<T>()` treats an object pointer as a fixed-size byte key. `CacheHandleGuard<T>` owns a `Cache::Handle*`, caches the typed value pointer, releases the handle on destruction, disallows copying, supports move construction/assignment, exposes cache/handle/value accessors, can `Reset()`, and can `TransferTo(Cleanable*)` by registering `ReleaseCacheHandleCleanup`. `MakeSharedCacheHandleGuard<T>()` creates a shared wrapper guard and returns an aliasing `shared_ptr<T>` pointing to the cached value while keeping the handle alive. `WarmInCache()` is declared for reconstructing cache entries from saved bytes.

## Control flow, state, and persistence
The guard's state is just `Cache*`, `Cache::Handle*`, and `T*`. Move operations transfer those fields and clear the source. `TransferTo()` transfers cleanup responsibility to another object and clears the guard without releasing immediately. The header does not persist data.

## Dependencies and integration points
It depends on `rocksdb/advanced_cache.h` and `rocksdb/rocksdb_namespace.h`. It integrates with typed cache users, `Cleanable` ownership chains, table/block cache code that wants RAII over handles, and secondary-cache warm-in code.

## Risks and test signals
Type safety is manual: a caller using the wrong `T` gets an invalid cast. `GetSliceForKey()` uses raw object bytes and is only appropriate for stable, trivially represented keys. `TransferTo(nullptr)` clears the guard without releasing, so callers must provide a valid cleanable when transferring a non-empty guard. Test by move/reset/destructor paths, cleanup transfer, and typed shared guards under sanitizer builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_key.cc -->
# sources/storage-engines/rocksdb/cache/cache_key.cc

## Purpose
This file implements RocksDB's standardized 16-byte cache key generation, including cache-lifetime unique keys, process-lifetime unique keys, and file-offset-derived block cache keys based on SST internal unique IDs.

## Important APIs, types, and functions
`CacheKey::CreateUniqueForCacheLifetime(Cache*)` returns `(0, cache->NewId()+1)` and asserts the id does not enter the high-bit range reserved for process-lifetime keys. `CacheKey::CreateUniqueForProcessLifetime()` uses a static atomic counter starting at `UINT64_MAX`, counts down with relaxed ordering, and asserts the high bit is set. `OffsetableCacheKey(const std::string&, const std::string&, uint64_t)` calls `GetSstInternalUniqueId(..., force=true)` and delegates to `FromInternalUniqueId()`.

`OffsetableCacheKey::FromInternalUniqueId(UniqueIdPtr)` transforms two 64-bit internal ID words into a base cache key using `DownwardInvolution(session_lower)`, `ReverseBits(file_num_etc)`, and `ReverseBits(session_lower)`, preserving empty input as empty and swapping words if needed to ensure the first word is non-zero for non-empty keys. `ToInternalUniqueId()` reverses that transformation, with the same swap convention.

## Control flow, state, and persistence
The only mutable state is the process-lifetime atomic counter. File-derived keys are deterministic from persistent SST identity data (`db_id`, `db_session_id`, and file number), which lets cache keys remain stable across DB reopen, backup/restore, import/export, and persistent cache lookup. `WithOffset()` in the header later combines the base key with offsets by XORing the second word.

## Dependencies and integration points
The implementation depends on `rocksdb/advanced_cache.h`, SST unique ID helpers from `table/unique_id_impl.h`, hashing/math utilities such as `DownwardInvolution()` and `ReverseBits()`, and cache `NewId()`. It is used by block-based table readers, reservation dummy entries, process-shared cache metadata, and the cache-key stress simulation in `cache_bench_tool.cc`.

## Risks and test signals
The correctness argument is mathematical and relies on assumptions about SST unique ID structure, non-empty lower words, and structured values fitting into 128 bits. Endianness is intentionally not portable for persisted cache entries across platforms. Cache-lifetime keys assume `Cache::NewId()` counts from low values and never reaches the process-lifetime high-bit range. Test with cache-key encoder/decoder tests, `StressCacheKey`, collision simulations, persistent cache reopen scenarios, and assertions around empty/non-empty transformations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_key.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_key.h -->
# sources/storage-engines/rocksdb/cache/cache_key.h

## Purpose
This header defines `CacheKey`, RocksDB's fixed 16-byte cache key holder, and `OffsetableCacheKey`, a file-specific base key that efficiently derives per-offset cache keys for block and related caches.

## Important APIs, types, and functions
`CacheKey` has an empty default constructor, `IsEmpty()`, `AsSlice()` which asserts non-empty and exposes the object bytes as a 16-byte `Slice`, `CreateUniqueForCacheLifetime(Cache*)`, and `CreateUniqueForProcessLifetime()`. It stores two protected `uint64_t` words and exposes `kCacheKeySize`.

`OffsetableCacheKey` privately inherits `CacheKey` to prevent accidentally using a base key directly. It can be built from DB id/session id/file number or from a `UniqueIdPtr`, inverted with `ToInternalUniqueId()`, checked with `IsEmpty()`, converted to a concrete `CacheKey` with `WithOffset(uint64_t)` by XORing the offset into the second word, and exposed as an 8-byte common prefix with `CommonPrefixSlice()`.

## Control flow, state, and persistence
The header's inline methods are hot-path primitives with no allocation. File-derived keys are intended to be stable from table properties and suitable for persistent cache lookup; unique cache/process lifetime keys are not stable beyond their respective lifetimes.

## Dependencies and integration points
It depends on RocksDB namespace, `Slice`, `Cache`, and `UniqueId` types. Integration points include block-based table cache key setup, cache reservation manager dummy entries, cache stats collector keys, and code needing common-prefix locality for cache lookups.

## Risks and test signals
`AsSlice()` is endian-dependent and points at the object's own memory, so callers must copy if the slice outlives the object. `OffsetableCacheKey::IsEmpty()` only checks the first word and asserts consistency with the second. Misusing a base key instead of `WithOffset()` would collide all offsets, which private inheritance helps prevent. Test by comparing generated keys for uniqueness, common prefix behavior, stable table-property-derived keys, and inverse transformations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_key.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_reservation_manager.cc -->
# sources/storage-engines/rocksdb/cache/cache_reservation_manager.cc

## Purpose
This file implements `CacheReservationManagerImpl<R>`, which reserves capacity in a cache by inserting pinned dummy entries. It is used when memory consumed outside the block cache must still count toward a shared cache budget.

## Important APIs, types, and functions
`CacheReservationHandle` stores an incremental memory amount and a shared manager pointer; its destructor releases that amount. The manager constructor wraps the cache in `PlaceholderSharedCacheInterface<R>`, stores delayed-decrease mode, and initializes allocated and used counters. The destructor releases all remaining dummy handles with `ReleaseAndEraseIfLastRef()`.

`UpdateCacheReservation(new_mem_used)` records total memory used, then increases dummy entries until reserved size is at least the new usage, decreases them down to the smallest 256 KiB multiple still covering usage, or keeps them when unchanged. In delayed-decrease mode it keeps existing reservations until usage falls below 3/4 of the reserved size. `MakeCacheReservation()` updates total usage by an increment and returns an RAII handle. `IncreaseCacheReservation()` inserts dummy entries with unique cache-lifetime keys and `kSizeDummyEntry` charge. `DecreaseCacheReservation()` releases dummy handles from the vector tail. `GetNextCacheKey()` stores the generated `CacheKey` in a member so the returned `Slice` remains valid for the insert call. The file explicitly instantiates the template for table reader, compression dictionary, filter construction, misc, write buffer, file metadata, and blob cache roles.

## Control flow, state, and persistence
State is in-memory: the target cache wrapper, `delayed_decrease_`, atomic `cache_allocated_size_`, non-atomic `memory_used_`, dummy handle vector, and scratch `cache_key_`. There is no disk persistence. The class is explicitly not thread-safe except `GetTotalReservedCacheSize()`; concurrent callers should use `ConcurrentCacheReservationManager` from the header.

## Dependencies and integration points
It depends on cache roles, typed cache placeholders, `CacheKey`, `rocksdb/cache.h`, and block-based reader common definitions. It integrates with memory accounting for write buffers, blob caches, table readers, file metadata, and charged caches.

## Risks and test signals
Insert failures under strict capacity can leave partial dummy reservations while `memory_used_` records the requested amount, so callers must inspect returned `Status`. The 256 KiB quantum can over-reserve, and delayed decrease intentionally keeps stale reservations. `GetNextCacheKey()` returns a slice into mutable member storage and must only be used immediately. Test signals are reservation manager unit tests covering key generation, exact and rounded increases/decreases, strict-capacity failure recovery, delayed decrease thresholds, destructor cleanup, and RAII handle release.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_reservation_manager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_reservation_manager.h -->
# sources/storage-engines/rocksdb/cache/cache_reservation_manager.h

## Purpose
This header declares the cache reservation abstraction, its dummy-entry implementation, and a mutex-protected concurrent wrapper. The abstraction lets RocksDB reserve block-cache capacity for memory consumed by related structures that are not themselves normal block cache entries.

## Important APIs, types, and functions
`CacheReservationManager` defines the interface: `UpdateCacheReservation(new_memory_used)`, delta-based `UpdateCacheReservation(memory_used_delta, increase)`, `MakeCacheReservation(incremental_memory_used, handle*)`, `GetTotalReservedCacheSize()`, and `GetTotalMemoryUsed()`. `CacheReservationManagerImpl<R>` implements the interface for a `CacheEntryRole`, with nested RAII `CacheReservationHandle`, a static dummy entry size of 256 KiB, deleted copy/move operations, delayed-decrease configuration, helper test access, and private increase/decrease/key-generation methods.

`ConcurrentCacheReservationManager` wraps any `CacheReservationManager` with a mutex. Its nested handle holds both the wrapper manager and an underlying handle; destruction locks the wrapper before resetting the underlying handle. The wrapper serializes absolute updates, delta updates, handle creation, and total memory reads. `GetTotalReservedCacheSize()` intentionally forwards without locking to the underlying implementation's atomic reserved-size read.

## Control flow, state, and persistence
The implementation reserves cache state indirectly by holding dummy entry handles. The concurrent wrapper owns a shared manager pointer and a mutex; the nested handles keep the wrapper alive until their underlying reservations are released. State is volatile and bounded by target cache lifetime.

## Dependencies and integration points
The header depends on cache entry roles, cache keys, typed cache placeholders, `Slice`, `Status`, and coding utilities. It is used by `charged_cache.cc` and other components that need to charge memory against a shared cache.

## Risks and test signals
The base implementation warns that callers must use either absolute updates or RAII handles, not both, to avoid unexpected accounting. The non-concurrent implementation's `memory_used_` and handle vector require external synchronization. `ConcurrentCacheReservationManager::MakeCacheReservation()` resets `*handle` even if the underlying call returns non-OK, so callers must handle status and returned handle carefully. Test with concurrent deltas, RAII handle destruction ordering, manager lifetime with outstanding handles, and role-specific helper identity.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_reservation_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_reservation_manager_test.cc -->
# sources/storage-engines/rocksdb/cache/cache_reservation_manager_test.cc

## Purpose
This unit test file validates dummy-entry cache reservation behavior, including key generation, rounding, strict-capacity failures, delayed decrease, destructor cleanup, and RAII reservation handles.

## Important APIs, types, and tests
`CacheReservationManagerTest` creates a single-shard LRU cache and a misc-role `CacheReservationManagerImpl`. `GenerateCacheKey` verifies that the first dummy entry can be found by reconstructing the expected cache-lifetime key sequence. `KeepCacheReservationTheSame`, `IncreaseCacheReservationByMultiplesOfDummyEntrySize`, and `IncreaseCacheReservationNotByMultiplesOfDummyEntrySize` validate absolute update accounting and rounded dummy insertion. `IncreaseCacheReservationOnFullCache` uses strict capacity to force `Status::MemoryLimit()`, checks partial bookkeeping, then decreases and later increases capacity to recover. Decrease tests validate exact and rounded release. `DecreaseCacheReservationWithDelayedDecrease` checks the 3/4 delayed-decrease threshold. `ReleaseRemainingDummyEntriesOnDestruction` checks destructor cleanup. `CacheReservationHandleTest` checks `MakeCacheReservation()`, handle reset release, and manager lifetime held by outstanding handles.

## Control flow, state, and persistence
All tests operate in memory using LRU caches. Assertions compare `GetTotalReservedCacheSize()`, `GetTotalMemoryUsed()`, and `cache->GetPinnedUsage()` with a metadata-overhead tolerance. The test `main()` installs RocksDB's stack trace handler and runs GoogleTest.

## Dependencies and integration points
The tests depend on `cache/cache_reservation_manager.h`, LRU cache construction, cache entry roles, `CacheKey`, GoogleTest helpers, and coding utilities. They indirectly validate the typed placeholder helper used by reservation dummy entries.

## Risks and test signals
The `GenerateCacheKey` test depends on `CacheKey` internals and `Cache::NewId()` sequencing, making it sensitive to legitimate implementation changes. Metadata overhead thresholds are heuristic. The test suite does not exercise `ConcurrentCacheReservationManager` under real concurrency. Passing tests strongly signal that reservation accounting works for single-threaded callers and strict-capacity failure paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_reservation_manager_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_test.cc -->
# sources/storage-engines/rocksdb/cache/cache_test.cc

## Purpose
This parameterized GoogleTest suite validates the shared `Cache` interface across RocksDB cache implementations, especially LRU and HyperClock variants supplied by `secondary_cache_test_util::GetTestingCacheTypes()`. It checks usage accounting, pinning, lookup/insert/erase behavior, eviction, capacity, iteration, hash seed behavior, and block-cache uncache aggressiveness logic.

## Important APIs, types, and tests
The test fixture `CacheTest` adapts key encoding: HyperClock requires 16-byte keys while LRU accepts 4-byte keys. It provides helpers for `Lookup`, `Insert`, and `Erase`, a deleter that records deleted integer values, and two caches with different capacities. Basic tests include `UsageTest`, `PinnedUsageTest`, `HitAndMiss`, `InsertSameKey`, `Erase`, `EntriesArePinned`, `EvictionPolicy`, `ExternalRefPinsEntries`, `EvictionPolicyRef`, `EvictEmptyCache`, `EraseFromDeleter`, `ErasedHandleState`, `HeavyEntries`, `NewId`, `ReleaseAndErase`, and `ReleaseWithoutErase`.

Typed-cache tests use a local `Value` class and `BasicTypedSharedCacheInterface`. `SetCapacity` validates LRU capacity changes and cleanup; `SetStrictCapacityLimit` validates strict LRU behavior with and without returned handles; `OverCapacity` checks pinned entries over capacity and different LRU/HyperClock eviction timing. Iteration tests cover `ApplyToAllEntries`, `ApplyToAllEntriesDuringResize`, and `ApplyToHandle`. `DefaultShardBits` checks auto shard-bit selection. `GetChargeAndDeleter` validates charge/helper retrieval. `CacheUniqueSeeds` and `CacheHostSeed` verify quasi-random and host-stable hash seeds and their observable ordering effect. `MiscBlockCacheTest.UncacheAggressivenessAdvisor` checks decision traces for uncache aggressiveness values.

## Control flow, state, and persistence
The tests are in-memory and create fresh caches per fixture or test. They intentionally retain and release `Cache::Handle*` values to test pinning and deletion order. Some tests bypass unsupported behavior for HyperClock, such as guaranteed overwrite on same-key insert and arbitrary capacity adjustment. The test main installs the stack trace handler and runs all tests.

## Dependencies and integration points
The suite integrates `rocksdb/cache.h`, LRU cache construction, typed cache wrappers, block cache helpers, secondary cache test utilities, stack traces, hash containers, string utilities, and GoogleTest. It exercises the public cache contract expected by table readers, block caches, secondary cache wrappers, and memory-accounting users.

## Risks and test signals
Tests encode implementation-specific differences between LRU and HyperClock, so broadening cache implementations requires updating parameter logic or bypasses. Some assertions rely on rough metadata behavior and eviction eventually happening after enough churn. Passing tests signal that core cache semantics, handle lifetimes, accounting, iteration under resize, hash seed options, and uncache advisor thresholds remain compatible across supported cache types.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/cache_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/charged_cache.cc -->
# sources/storage-engines/rocksdb/cache/charged_cache.cc

## Purpose
This file implements `ChargedCache`, a `CacheWrapper` that forwards operations to an underlying cache while reserving equivalent usage in a separate block cache through `ConcurrentCacheReservationManager`. It lets blob-cache or secondary cache memory count toward a global block-cache memory limit.

## Important APIs, types, and functions
The constructor stores the wrapped cache in `CacheWrapper` and creates a concurrent reservation manager backed by `CacheReservationManagerImpl<CacheEntryRole::kBlobCache>` against the provided block cache. `Insert()` forwards to `target_->Insert()` and, on success, updates reservation to `target_->GetUsage()` because insertion can evict entries. `Lookup()` forwards and updates reservation when helper/create callbacks are present, covering possible secondary-cache promotion into the primary cache. `WaitAll()` forwards async waits then updates usage for promotions that complete during waits. Both `Release()` overloads capture `target_->GetUsage(handle)` before forwarding release; if the entry was erased, they decrease reservation by that delta. `Erase()`, `EraseUnRefEntries()`, and `SetCapacity()` forward then refresh reservation to target usage.

## Control flow, state, and persistence
`ChargedCache` stores only the reservation manager in addition to `CacheWrapper` state. It has no disk persistence. Reservation state is dummy entries in the block cache, updated after mutating or promotion-capable operations.

## Dependencies and integration points
It depends on `cache/charged_cache.h` and `cache/cache_reservation_manager.h`. It integrates cache wrappers, blob cache memory accounting, block cache global budgets, secondary cache promotion, async lookup wait paths, and cache capacity changes.

## Risks and test signals
Reservation updates ignore errors via `PermitUncheckedError()`, so a full strict block cache can silently under-reserve. Release paths use per-handle usage deltas and assume the erased return value accurately signals whether reservation should decrease. Lookup updates only when `helper && helper->create_cb`, so promotion paths must supply a create-capable helper. Test with blob cache insert/lookup/release/erase, secondary cache promotion through `WaitAll`, block cache strict-capacity pressure, and capacity shrink evictions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/charged_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/charged_cache.h -->
# sources/storage-engines/rocksdb/cache/charged_cache.h

## Purpose
This header declares `ChargedCache`, a cache wrapper that charges one cache's usage against another cache through reservations.

## Important APIs, types, and functions
`ChargedCache` derives from `CacheWrapper`. It declares overrides for `Insert`, `Lookup`, `WaitAll`, both `Release` signatures, `Erase`, `EraseUnRefEntries`, `SetCapacity`, `Name()`, and `GetCache()`. `kClassName()` returns `"ChargedCache"`. `TEST_GetCacheReservationManager()` exposes the internal `ConcurrentCacheReservationManager` for tests.

## Control flow, state, and persistence
The class holds a `std::shared_ptr<ConcurrentCacheReservationManager>`. All behavior is defined in the `.cc` file and is in-memory only.

## Dependencies and integration points
It depends on `rocksdb/advanced_cache.h` for `CacheWrapper` and `Cache` types plus RocksDB port headers. It forward declares `ConcurrentCacheReservationManager` to avoid exposing reservation implementation details to header users. It is intended for blob-cache/global-memory-limit integration.

## Risks and test signals
Because this is a wrapper, correctness depends on overriding every operation that can change target usage. New `Cache` mutation APIs added later could bypass reservation accounting unless `ChargedCache` is updated. Test by comparing target cache usage to block-cache reservation after each public operation and by exercising wrapper name/type checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/cache/charged_cache.h -->
