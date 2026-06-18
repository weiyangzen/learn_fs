<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/paramgrill.c -->
## sources/compression/zstd/tests/paramgrill.c

Purpose: Benchmark and optimization tool for exploring zstd compression parameters, generating candidate compression-level tables, and finding parameter sets that satisfy speed, ratio, and memory constraints.

Important APIs and types: Core parameter modeling uses `varInds_t`, `paramValues_t`, `constraint_t`, `winnerInfo_t`, `memoTable_t`, and `buffers_t`/`contexts_t`. Parameter conversion helpers include `rangeMap`, `invRangeMap`, `sanitizeParams`, `pvalsToCParams`, `cParamsToPVals`, `adjustParams`, `paramValid`, `emptyParams`, and `overwriteParams`. Benchmark integration uses `BMK_benchMemInvertible`, `BMK_benchParam`, `allBench`, and `benchMemo`. Search logic uses `BMK_seed`, `playAround`, `BMK_generate_cLevelTable`, `climbOnce`, `optimizeFixedStrategy`, and `optimizeForSize`. CLI parsing uses `longCommandWArg`, `readU32FromChar`, `readDoubleFromChar`, and `parse_params`.

Control flow: `main()` parses modes, parameter constraints, display options, dictionaries, block size, time limit, and input files. With no input and no optimizer, it generates a 10 MiB sample and either benchmarks one configuration or generates a level table. With files, it loads data into block buffers, optionally loads a dictionary, and either runs a single benchmark, generates a table, or performs optimizer hill climbing. The optimizer first benchmarks default levels to seed strategy selection, then climbs within and around strategies using memoized candidate rejection until time or try limits stop the search.

State and persistence: Global state controls runtime (`g_timeLimit_s`, `g_time`, `g_blockSize`, `g_rand`), display (`g_displayLevel`, `g_silenceParams`), modes (`g_singleRun`, `g_optimizer`, `g_optmode`), optimizer targets (`g_target`, `g_strictness`, `g_lvltarget`, `g_ratioMultiplier`), and winner lists. `BMK_generate_cLevelTable` writes `grillResults.txt` with intermediate and final proposed configurations. Input file contents, dictionaries, contexts, destination buffers, result buffers, memo tables, and winner lists are heap allocated.

Dependencies and integration points: Includes zstd static-linking-only APIs, internal `zstd_internal.h`, benchmark helpers (`benchfn.h`, `benchzstd.h`), random data generation, xxhash, time utilities, and file utilities. It emits `--zstd=...` command lines compatible with the zstd CLI advanced-parameter syntax.

Risks: This is resource- and time-intensive by design. Several paths call `exit(1)` directly on parse or output errors. Memoization may use direct arrays or lossy xxhash tables, so collisions can suppress candidates. `readU32FromChar` accepts signed values by unsigned wrap for parameters such as force attach dict. Many globals make reentrancy impossible. `BMK_findMaxMem` probes large allocations and can affect hosts under memory pressure.

Test signals: Useful checks include `--zstd=` single-run output, `--optimize=` constraint parsing, dictionary and block-size operation, `grillResults.txt` creation for table generation, nonzero returns on invalid parameters, and stable round-trip validation inside `BMK_benchMemInvertible`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/paramgrill.c -->
