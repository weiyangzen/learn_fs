# sources/test-tools/filebench subset-b-009219 research

This grouped report covers the requested Filebench files in manifest order. Each section is delimited for reconciliation into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/mtwist.h -->
## sources/test-tools/filebench/cvars/mtwist/mtwist.h

### Purpose
`mtwist.h` is the C and C++ public interface for the bundled Mersenne Twister pseudo-random number generator. It defines the generator state object, the seeding/state-persistence API, the default-generator API, conversion helpers, tempering macros, and the C++ `mt_prng` wrapper. Filebench uses this PRNG indirectly through `fb_random.c`, while the mtwist distribution library uses the state-based functions to build higher-level distributions.

### Important APIs, Types, And Functions
The central type is `mt_state`, containing `statevec[MT_STATE_SIZE]`, `stateptr`, and an `initialized` flag. `MT_STATE_SIZE` is fixed at 624, matching the 32-bit MT19937 state. State-specific APIs include `mts_seed32`, `mts_seed32new`, `mts_seedfull`, `mts_seed`, `mts_goodseed`, `mts_bestseed`, `mts_refresh`, `mts_savestate`, and `mts_loadstate`. Default-generator APIs mirror those without the `mts_` state parameter: `mt_seed32`, `mt_goodseed`, `mt_bestseed`, `mt_getstate`, `mt_savestate`, and `mt_loadstate`. Generation APIs include `mts_lrand`, `mts_llrand`, `mts_drand`, `mts_ldrand`, plus default-state versions `mt_lrand`, `mt_llrand`, `mt_drand`, and `mt_ldrand`. The C++ class `mt_prng` wraps a protected `mt_state` and exposes constructors, seed methods, random-value methods, stream operators, and `operator()`.

### Control Flow
This header is mostly declarations, but it also fixes the interface contract used by the implementation in `mtwist.c`: callers seed an `mt_state`, then draw 32-bit, 64-bit, or floating-point values. The comments document the reversed state-vector traversal, where zeroed state is treated as uninitialized and refreshes are triggered by a zero-oriented pointer test. The tempering macros apply the MT19937 bit-mixing steps to generated state words.

### State And Persistence
State is explicit through `mt_state` or implicit through exported `mt_default_state`. The save/load functions persist generator state in ASCII to a `FILE *`, allowing deterministic replay. Seeding can derive entropy from `/dev/urandom`, `/dev/random`, or time fallback depending on the API. `mt_32_to_double` and `mt_64_to_double` are exported conversion multipliers shared by random-distribution code.

### Dependencies And Integration Points
The header depends on `stdio.h`, `stdint.h`, and C++ `iostream` when compiled as C++. `randistrs.h` includes this header and uses the protected C++ `mt_prng::state` through friendship for empirical distributions. Filebench includes `cvars/mtwist/mtwist.h` from `fb_random.c` to use `mt_llrand()` as a default random source.

### Risks
The implementation assumes a 32-bit PRNG word; changing integer widths or constants would break distribution quality. The default generator is global state and not inherently synchronized. The seed APIs provide only 32 bits of entropy for `seed`/`goodseed`, which is adequate for benchmarking reproducibility but not cryptographic use. The header advertises `mt_default_state` as an undocumented external, which makes coupling convenient but exposes internals.

### Test Signals
Relevant tests are the mtwist test programs elsewhere in the directory and the distribution harnesses `rdtest.c` and `rdcctest.cc`. Practical verification should check deterministic sequences for fixed seeds, save/load round trips, zero-initialized state behavior, 32-bit/64-bit generation paths, and C++ wrapper parity with the C state APIs.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/mtwist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/randistrs.c -->
## sources/test-tools/filebench/cvars/mtwist/randistrs.c

### Purpose
`randistrs.c` implements probability distributions on top of the mtwist PRNG. It provides state-based `rds_*` functions and default-generator `rd_*` wrappers for uniform integer/floating distributions, exponential, Erlang, Weibull, normal, lognormal, triangular, and empirical distributions.

### Important APIs, Types, And Functions
Uniform integer APIs are `rds_iuniform` and, when `INT64_MAX` exists, `rds_liuniform`. Floating uniform APIs are `rds_uniform` and `rds_luniform`. Transform-based distributions include `rds_exponential`, `rds_erlang`, `rds_weibull`, `rds_normal`, `rds_lognormal`, and `rds_triangular`, each with long-precision `l` variants. Empirical support is built around `rd_empirical_setup`, `rd_empirical_free`, `rds_int_empirical`, `rds_double_empirical`, and `rds_continuous_empirical`. The `rd_*` functions delegate to the same stateful implementations using `mt_default_state`.

### Control Flow
The integer-uniform functions use a fast double-scaling path for small ranges below `RD_UNIFORM_THRESHOLD`, then switch to rejection sampling with a computed bitmask for larger ranges to avoid unacceptable bias. Exponential, Erlang, Weibull, and normal distributions repeatedly draw until the random input avoids zero or invalid transform domains. Normal uses the polar form of Box-Muller and discards the second variate to stay reentrant. Empirical setup normalizes caller weights, divides entries into low/high stacks, builds alias-style cutoff/remap tables in O(n), then generation scales a uniform value by `n` and either returns the direct slot or its remap.

### State And Persistence
The file does not maintain persistent distribution state except in heap-allocated `rd_empirical_control` structures returned by `rd_empirical_setup`. Those controls own `cutoff`, `remap`, and `values` arrays and must be freed with `rd_empirical_free`. Random-generator state is external: either supplied `mt_state *` or `mt_default_state`.

### Dependencies And Integration Points
It depends on `mtwist.h`, `randistrs.h`, `math.h`, and `stdlib.h`. The C++ wrapper in `randistrs.h` directly calls these functions. The standalone test programs `rdtest.c` and `rdcctest.cc` exercise these APIs from the command line.

### Risks
Parameter validation is mostly left to callers. Invalid bounds such as `upper <= lower`, nonpositive means/scales, or invalid triangular mode can produce biased, nonsensical, or undefined math results. `rd_empirical_setup` copies `n_probs + 1` values when `values` is provided, so callers that pass only `n_probs` entries risk out-of-bounds reads. The code assigns `control->remap` twice before allocating `values`, leaking the first allocation. Empirical setup also divides by `prob_total`; all-zero weights would be invalid. `MT_CACHING` makes integer mask caching static and non-reentrant.

### Test Signals
Useful tests include deterministic output for fixed seeds, boundary checks for integer ranges, rejection-sampling behavior near large ranges, statistical smoke tests for each distribution, empirical alias-table coverage, and allocation-failure cleanup tests for `rd_empirical_setup`. Existing `rdtest` and `rdcctest` are generation harnesses but do not assert distribution quality.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/randistrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/randistrs.h -->
## sources/test-tools/filebench/cvars/mtwist/randistrs.h

### Purpose
`randistrs.h` declares the mtwist-based random distribution API for C and C++ consumers. It documents the three access styles: `rds_*` functions using caller-provided `mt_state`, `rd_*` functions using the default mtwist state, and C++ `mt_distribution`/`mt_empirical_distribution` wrappers.

### Important APIs, Types, And Functions
The key exported control type is `rd_empirical_control`, which stores the alias-table data used by empirical distributions: `n`, `cutoff`, `remap`, and `values`. The header declares all state-based distribution functions, all default-state wrappers, and `rd_empirical_setup`/`rd_empirical_free`. Under C++, `mt_distribution` derives from `mt_prng` and forwards methods like `uniform`, `normal`, and `triangular` to the C functions. `mt_empirical_distribution` owns an `rd_empirical_control *` and exposes empirical generation methods taking an `mt_prng &`.

### Control Flow
The header itself does not implement C control flow, but it fixes the calling patterns for `randistrs.c`: initialize or zero an `mt_state`, call a distribution function, and optionally reuse empirical control tables across independent generators. In C++, constructors initialize the underlying `mt_prng`; distribution methods forward through the protected state object.

### State And Persistence
Distribution calls are stateless except for the PRNG state and empirical control allocations. The header explicitly recommends the `rds_*` stateful interface for serious uses because independent streams reduce accidental correlation. `mt_empirical_distribution` manages the control lifetime with RAII but forbids copying and assignment.

### Dependencies And Integration Points
The header includes `mtwist.h` and, for C++, `stdexcept` and `vector`. It is included by `randistrs.c`, `rdtest.c`, and `rdcctest.cc`, and can be used by custom variable libraries that need mtwist distributions.

### Risks
The documented empirical `values` contract is easy to misuse: even discrete double empirical setup copies `n_probs + 1` values if `values` is non-null. The C++ empirical wrapper assumes C `malloc/free` interoperate safely in the runtime used by C++ object construction/destruction. The header exposes raw pointers and does not encode parameter constraints in types.

### Test Signals
Compile tests should cover both C and C++ inclusion. Runtime tests should verify that `rd_*` and `rds_*` produce equivalent sequences when given equivalent default and explicit states, that the C++ wrappers match the C functions, and that empirical construction rejects mismatched vector sizes in C++.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/randistrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/rdcctest.cc -->
## sources/test-tools/filebench/cvars/mtwist/rdcctest.cc

### Purpose
`rdcctest.cc` is a C++ command-line generator for manually exercising the random distribution library. It parses a seed, a count, a distribution name, and distribution parameters, then prints generated values to stdout using the C++ mtwist distribution wrappers.

### Important APIs, Types, And Functions
The only public entry point is `main`. It uses `mt_distribution` for PRNG/distribution generation and conditionally allocates an `mt_empirical_distribution` for empirical cases. `usage()` prints accepted distributions and exits with status 2. Supported distribution names include `iuniform`, `uniform`, `exponential`, `erlang`, `weibull`, `normal`, `lognormal`, `triangular`, `empirical`, and `continuous_empirical`.

### Control Flow
The program validates a minimum argument count, parses numeric parameters into a dynamically allocated `double` array, then branches by distribution name to determine required parameter count. Empirical modes build `std::vector<double>` values and probabilities, reject negative probabilities, and create an `mt_empirical_distribution`. A generator is constructed with automatic seeding when the seed argument is zero; otherwise `seed32(seed)` fixes deterministic output. The main loop dispatches to the selected distribution and writes one value per line.

### State And Persistence
State is in the local `mt_distribution distr` object and, for empirical runs, a heap-allocated `mt_empirical_distribution`. No files or persistent state are written. A fixed nonzero seed provides reproducibility; seed zero delegates seed selection to mtwist.

### Dependencies And Integration Points
It includes `randistrs.h`, `iostream`, `stdlib.h`, `string.h`, and `vector`. It validates the C++ wrapper interface in `randistrs.h` and indirectly exercises `randistrs.c` plus `mtwist.c`.

### Risks
The code allocates `params` with `new[]` and empirical objects with `new` but never deletes them; acceptable for a short test program but not clean. `usage()` prints a stale syntax line missing the seed parameter even though `main` expects it. Numeric parsing uses `atoi`/`atof`, so malformed strings silently become zero. There is no statistical assertion; this is an output generator, not an automated correctness test.

### Test Signals
Useful signals are successful compilation as C++, expected failure on bad parameter counts and negative empirical weights, deterministic output for fixed seeds, and parity against `rdtest.c` for equivalent distributions and seeds.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/rdcctest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/rdtest.c -->
## sources/test-tools/filebench/cvars/mtwist/rdtest.c

### Purpose
`rdtest.c` is the C command-line harness for generating values from `randistrs.c`. It is useful for manual inspection, deterministic sequence checks, and simple statistical pipelines outside the Filebench runtime.

### Important APIs, Types, And Functions
`main` parses `seed`, `count`, `distribution`, and distribution parameters. It calls the default-state `rd_*` APIs such as `rd_iuniform`, `rd_uniform`, `rd_exponential`, `rd_erlang`, `rd_weibull`, `rd_normal`, `rd_lognormal`, `rd_triangular`, `rd_double_empirical`, and `rd_continuous_empirical`. `rd_empirical_setup` prepares empirical controls, while `usage()` prints accepted syntax and exits.

### Control Flow
After parsing input, the program determines the expected number of parameters for the requested distribution. Empirical modes allocate separate `probs` and `values` arrays, reject negative probabilities, and build a control table. If seed is zero it calls `mt_goodseed`; otherwise it calls `mt_seed32`. The generation loop dispatches by string comparison on every iteration and prints one floating-point value per line.

### State And Persistence
The program uses mtwist's default global generator state rather than an explicit `mt_state`. Empirical control state is heap-allocated and not freed before process exit. No persistent files are written.

### Dependencies And Integration Points
It includes `randistrs.h`, `stdio.h`, `stdlib.h`, and `string.h`. It exercises the C API in `randistrs.c` and mtwist default-state seeding. It is the C counterpart to `rdcctest.cc`.

### Risks
Malformed numeric parameters silently parse as zero. Memory allocated for `params`, `probs`, `values`, and empirical controls is not freed. Most distribution parameter domains are not validated beyond Erlang order and empirical nonnegative probabilities. The loop repeatedly compares distribution strings, which is fine for a test harness but not efficient library style.

### Test Signals
Primary test signals are process exit status, stdout sample count, deterministic output for a fixed seed, and compatibility with the C++ harness. Stronger tests should pipe output into statistical checks and cover invalid arguments, all empirical branches, and seed-zero behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/rdtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/test/sanity.c -->
## sources/test-tools/filebench/cvars/test/sanity.c

### Purpose
`sanity.c` is a standalone dynamic-loader sanity checker for Filebench custom variable libraries. It loads a cvar shared object, resolves the expected symbol vector, allocates a custom-variable handle from a parameter string, revalidates it, prints requested generated values, and frees the handle.

### Important APIs, Types, And Functions
`main` is the only runtime entry point. It uses `cvar_operations_t` from `fb_cvar.h` and the symbol-name macros `FB_CVAR_MODULE_INIT`, `FB_CVAR_ALLOC_HANDLE`, `FB_CVAR_REVALIDATE_HANDLE`, `FB_CVAR_NEXT_VALUE`, `FB_CVAR_FREE_HANDLE`, `FB_CVAR_MODULE_EXIT`, `FB_CVAR_USAGE`, and `FB_CVAR_VERSION`. `print_usage()` explains the shared-library, parameter-string, and count arguments.

### Control Flow
The program validates three user arguments, opens the library with `dlopen(..., RTLD_NOW | RTLD_GLOBAL)`, resolves required and optional symbols with `dlsym`, calls optional module init/version/usage hooks, then calls `cvar_alloc_handle(parameters, malloc, free)`. It revalidates the handle, loops `count` times calling `cvar_next_value`, prints comma-separated values, frees the handle, calls optional module exit, closes the library, and returns an error-specific status on failure paths.

### State And Persistence
State is local to the process: a `dlopen` handle, a module-created `cvar_handle`, and transient generated values. No Filebench shared memory is used despite including the same cvar ABI. No persistent output beyond stdout/stderr is produced.

### Dependencies And Integration Points
It depends on `dlfcn.h`, libc allocation functions, and `fb_cvar.h`. It is an external contract checker for cvar modules built under `sources/test-tools/filebench/cvars`.

### Risks
The cleanup path always calls `cvar_free_handle(cvar_handle, free)` at label `cvar_free`; if allocation failed and `cvar_handle` was not initialized, this can pass an indeterminate pointer. Some error messages reference the wrong symbol macro in the revalidate failure branch. `atoi` silently accepts invalid counts. Using `RTLD_GLOBAL` can mask symbol-collision issues or be required by some modules, depending on plugin design.

### Test Signals
A successful run prints the variable name/version, optional usage, generated values, and `All done.` with exit code zero. Negative tests should cover missing symbols, failing `cvar_module_init`, invalid parameter strings, allocation failure, revalidation failure, and zero/negative count behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/test/sanity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/eventgen.c -->
## sources/test-tools/filebench/eventgen.c

### Purpose
`eventgen.c` implements Filebench's shared event producer used by rate-limiting flowops. It generates events at a configured frequency and signals consumers waiting on shared memory condition variables, enabling workload throttles for events, operations, IOPS, and bandwidth.

### Important APIs, Types, And Functions
The external API consists of `eventgen_init`, `eventgen_setrate`, and `eventgen_reset`. The internal `eventgen_thread` is the long-lived producer loop. It reads `filebench_shm->shm_eventgen_hz`, updates `shm_eventgen_enabled`, increments `shm_eventgen_q`, and signals `shm_eventgen_cv` under `shm_eventgen_lock`.

### Control Flow
`eventgen_init` creates a detached-style pthread running `eventgen_thread` and exits the process on creation failure. The thread waits until a rate variable is configured, then fetches the current rate with `avd_get_int`. For positive rates it sleeps for ten periods, computes elapsed nanoseconds with `gethrtime`, derives how many events elapsed, caps queue depth to about five seconds of events, increments the shared event queue, signals the condition variable, and repeats forever. `eventgen_reset` clears the queue before worker execution starts.

### State And Persistence
All operational state is in shared memory through `filebench_shm`: configured rate, enabled flag, event queue, mutex, and condition variable. The producer has a local `last` timestamp, but no persistent storage. Events accumulated before worker start are intentionally dropped by `eventgen_reset`.

### Dependencies And Integration Points
It includes `filebench.h`, `vars.h`, `eventgen.h`, `flowop.h`, and `ipc.h`. Consumer flowops in `flowop_library.c` use the shared event queue for rate limiting. `fbtime.c` provides a portable `gethrtime` fallback when the OS lacks Solaris `gethrtime`.

### Risks
The thread runs forever and has no explicit shutdown path in this file. A zero or negative rate causes the loop to continue without sleeping in the `else` branch after reading a non-null rate, which can spin if the configured rate is nonpositive. Queue depth is capped only before adding `count`, so a large delayed wake can still overshoot the cap. Rate changes are read without a separate configuration lock beyond shared variable access assumptions.

### Test Signals
Test signals include thread creation success, event queue growth matching configured rates over wall-clock intervals, reset clearing queued events, consumers waking on `shm_eventgen_cv`, and behavior under rate changes or disabled/null rates.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/eventgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/eventgen.h -->
## sources/test-tools/filebench/eventgen.h

### Purpose
`eventgen.h` exposes the minimal public interface for Filebench's event generator. It lets the main runtime start the generator, configure its rate, and reset the event queue before a benchmark run.

### Important APIs, Types, And Functions
The header declares `eventgen_init(void)`, `eventgen_setrate(avd_t rate)`, and `eventgen_reset(void)`. It includes `filebench.h` to obtain `avd_t` and shared Filebench definitions.

### Control Flow
The header defines no implementation, but the intended sequence is: initialize the eventgen thread, set a rate variable, and reset the queue before worker flowops consume events. Consumers do not include this header directly for queue access; they use shared-memory fields and flowop helpers.

### State And Persistence
State is not declared in the header. The implementation stores all runtime state in `filebench_shm`, so the API remains process-global rather than object-based.

### Dependencies And Integration Points
This is integrated with `eventgen.c`, parser/runtime setup code that calls `eventgen_setrate`, and flowop rate-limit consumers. Its dependency on `filebench.h` ties it to the full Filebench type system rather than a small forward declaration.

### Risks
The API does not expose shutdown or error returns. `eventgen_init` handles errors internally by logging and exiting, so callers cannot recover. The opaque shared-memory state means tests need either Filebench runtime setup or a mock `filebench_shm`.

### Test Signals
Compile tests should verify the header can be included where `filebench.h` is already available. Runtime tests should exercise the implementation sequence and check that rate-setting and reset mutate shared memory as expected.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/eventgen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/fb_avl.c -->
## sources/test-tools/filebench/fb_avl.c

### Purpose
`fb_avl.c` is Filebench's generic embedded-node AVL tree implementation, adapted from Solaris. It supplies ordered-set primitives used by filesets to track free, existing, and non-existing entries by index.

### Important APIs, Types, And Functions
Core operations are `avl_create`, `avl_find`, `avl_insert`, `avl_insert_here`, `avl_add`, `avl_remove`, `avl_first`, `avl_last`, `avl_walk`, `avl_nearest`, `avl_update`, `avl_update_lt`, `avl_update_gt`, `avl_numnodes`, `avl_is_empty`, `avl_destroy_nodes`, and `avl_destroy`. The internal `avl_rotation` handles both single and double rotations by symmetry.

### Control Flow
Search descends by comparator results, requiring exact `-1`, `0`, or `1`. Insertion places a leaf at an `avl_index_t` returned by `avl_find`, then walks ancestors adjusting balance and performs at most one rotation. Removal swaps two-child nodes with an adjacent node, deletes a node with at most one child, then walks ancestors applying rotations until height stabilizes. Iteration is iterative and uses parent pointers rather than recursion.

### State And Persistence
Tree state lives in caller-owned `avl_tree_t` and embedded `avl_node_t` fields inside caller data structures. The AVL layer allocates no memory and persists nothing. Node parent/child/balance data is stored in separate fields on 32-bit builds and packed into low bits of the parent pointer on 64-bit builds.

### Dependencies And Integration Points
It includes `filebench.h` and `fb_avl.h`, using `boolean_t` and `filebench_log`. `fileset.c` uses AVL trees for membership indexes. Any caller must provide locking around mutations and usually around traversal if concurrent mutation is possible.

### Risks
Comparator contract violations are logged and can leave callers without a found node. There is no internal synchronization. Passing unaligned data on 64-bit builds is rejected because low pointer bits are used for metadata. `avl_destroy` only logs when the tree is non-empty; it does not free nodes. There are duplicated log lines in a few error paths, but they do not change behavior.

### Test Signals
Tests should insert, find, iterate, remove, update, and destroy nodes in sorted and random orders; verify node count and ordering after every operation; run 32-bit/64-bit layout builds if supported; and exercise duplicate insert and comparator-error handling.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/fb_avl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/fb_avl.h -->
## sources/test-tools/filebench/fb_avl.h

### Purpose
`fb_avl.h` defines the public API and layout contract for Filebench's embedded AVL tree. It describes how callers embed `avl_node_t` in their own structures and use `avl_tree_t` plus comparator functions to maintain ordered sets.

### Important APIs, Types, And Functions
The key types are `avl_node_t`, `avl_tree_t`, and `avl_index_t`. Macros convert between embedded nodes and containing data (`AVL_NODE2DATA`, `AVL_DATA2NODE`), encode insertion cookies (`AVL_MKINDEX`, `AVL_INDEX2NODE`, `AVL_INDEX2CHILD`), and expose iteration helpers (`AVL_NEXT`, `AVL_PREV`). Function prototypes cover creation, lookup, insertion, removal, update, traversal, node count, empty check, bulk destruction, and final destroy.

### Control Flow
The header documents the expected usage sequence: create a tree with a comparator and offset, use `avl_find`/`avl_insert` or `avl_add`, traverse with first/last/next/previous, optionally use nearest-node queries, remove nodes, and destroy remaining nodes with `avl_destroy_nodes` before `avl_destroy`.

### State And Persistence
`avl_tree_t` holds the root pointer, comparator, embedded-node offset, node count, and user object size. `avl_node_t` stores child links and either explicit parent/child/balance fields or a packed parent-child-balance word on 64-bit builds. No persistence or allocation policy is included.

### Dependencies And Integration Points
The header includes `filebench.h` for shared types. `fileset.h` embeds `avl_node_t` in `filesetentry_t`, making this header part of the fileset public type contract.

### Risks
The macros rely on pointer arithmetic and correct `offsetof`-style offsets. On 64-bit builds they rely on pointer alignment to leave low bits available. The comparator must return exactly `-1`, `0`, or `1`, not arbitrary negative/positive values. The API places all locking responsibility on callers.

### Test Signals
Header-level checks should compile both packing branches where possible, verify offsets with embedded structs, and use static or runtime tests for iteration macros and `avl_index_t` encoding.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/fb_avl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/fb_cvar.c -->
## sources/test-tools/filebench/fb_cvar.c

### Purpose
`fb_cvar.c` implements Filebench custom variable support. It discovers cvar shared libraries, records their metadata in shared memory, loads each library per process, binds required function symbols, allocates per-variable handles, retrieves values, clamps/rounds them, and revalidates handles.

### Important APIs, Types, And Functions
Public functions are `cvar_alloc`, `init_cvar_library_info`, `init_cvar_libraries`, `init_cvar_handle`, `get_cvar_value`, and `revalidate_cvar_handles`. Internal helpers include `alloc_cvar_lib_info`, `gettype`, `init_cvar_library`, `load_library`, `free_cvar_library`, and `init_cvar_library_ops`. The global `cvar_libraries` points to the per-process array of loaded library objects.

### Control Flow
Discovery scans a directory for names ending in `.so`, derives a type by stripping leading `lib` and suffix after the first dot, and appends `cvar_library_info_t` records to `filebench_shm`. Initialization counts those records, allocates an array, loads each shared object with `dlopen`, resolves required and optional symbols, and invokes optional module init. Handle initialization finds a matching type and calls the plugin's `cvar_alloc_handle`. Value retrieval locks the cvar, calls `cvar_next_value`, unlocks, rounds to nearest configured increment, and clamps to min/max.

### State And Persistence
Library metadata is shared-memory state (`shm_cvar_lib_info_list`) so child processes can find the same library types. Actual `dlopen` handles and function vectors are process-local in `cvar_libraries`. Individual `cvar_t` objects live in shared memory and carry a cross-process mutex, bounds, round value, plugin handle, and library info pointer.

### Dependencies And Integration Points
It depends on `ipc.h`, `fb_cvar.h`, directory iteration, `dlfcn`, and Filebench logging/shutdown. Parser code creates cvars and variables can call `get_cvar_value` through the variable subsystem. The module ABI is tested externally by `cvars/test/sanity.c`.

### Risks
`gettype` allocates a temporary type string that is copied into IPC memory but never freed by `alloc_cvar_lib_info`. Error cleanup notes that `cli->filename` and `cli->type` cannot be freed. `init_cvar_libraries` does not unwind already loaded libraries on later failure. Missing `cvar_revalidate_handle` is logged but not fatal despite being part of the named operation set. The array `cvar_libraries` has no stored count, so callers rely on shared metadata indexes remaining consistent.

### Test Signals
Tests should cover directory discovery, type derivation, loading libraries with required/optional symbols, module init failure, handle allocation failure, value rounding/clamping, concurrent `get_cvar_value`, and revalidation across all configured handles.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/fb_cvar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/fb_cvar.h -->
## sources/test-tools/filebench/fb_cvar.h

### Purpose
`fb_cvar.h` defines the ABI between Filebench and custom variable shared libraries, plus the runtime structures Filebench uses to track those libraries and variable handles.

### Important APIs, Types, And Functions
Symbol-name macros identify plugin functions: `cvar_module_init`, `cvar_alloc_handle`, `cvar_revalidate_handle`, `cvar_next_value`, `cvar_free_handle`, `cvar_module_exit`, `cvar_usage`, and `cvar_version`. `cvar_library_info_t` stores shared metadata (`filename`, `type`, `index`, `next`). `cvar_t` stores a mutex, plugin handle, bounds, rounding, library info pointer, and list link. `cvar_operations_t` is the dlsym-populated function vector. `cvar_library_t` pairs metadata with a `dlopen` handle and operations vector. The header declares all cvar runtime functions and `cvar_libraries`.

### Control Flow
The declared model is discovery first, library initialization second, handle initialization per cvar third, then repeated value generation through the bound `cvar_next_value` function. Revalidation can be run later across all handles.

### State And Persistence
The structures distinguish shared metadata and handles from process-local library handles. The `cvar_t` mutex is intended for exclusive access across threads and processes. Bounds and rounding are stored directly on each cvar object and enforced by `get_cvar_value`.

### Dependencies And Integration Points
It includes integer and system types and requires pthread types through the wider Filebench include environment. It is included by Filebench runtime code and external cvar sanity tests.

### Risks
The ABI uses raw function pointers and `void *` handles, so type safety is entirely conventional. Plugin allocation/free functions must use the allocator callbacks provided by Filebench. Optional hooks are nullable; callers must check before invoking. The header does not encode ownership for strings and handles, which is handled by implementation convention.

### Test Signals
Compile-time tests should build a minimal plugin exporting required symbols. Runtime tests should load that plugin, allocate a handle, generate values, revalidate, free, and verify optional version/usage/module hooks.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/fb_cvar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/fb_localfs.c -->
## sources/test-tools/filebench/fb_localfs.c

### Purpose
`fb_localfs.c` implements the default local filesystem plugin for Filebench. It fills `fs_functions_vec` with POSIX-backed operations and, when AIO support is available, registers local-filesystem-specific async write/wait flowops.

### Important APIs, Types, And Functions
External functions are `fb_lfs_funcvecinit` and `fb_lfs_newflowops`. The static `fb_lfs_funcs` vector maps Filebench filesystem operations to wrappers for open, read, pread, write, pwrite, lseek, truncate, rename, close, link, symlink, unlink, readlink, mkdir, rmdir, opendir/readdir/closedir, fsync, stat/fstat, access, freemem, and recursive remove. Under `HAVE_AIO`, `fb_lfsflow_aiowrite`, `fb_lfsflow_aiowait`, `aio_allocate`, and `aio_deallocate` manage asynchronous writes.

### Control Flow
Initialization points the global filesystem vector at local wrappers and optionally registers AIO flowops. Most wrappers directly call the corresponding POSIX function, using configured `*64` aliases from `filebench.h`. `fb_lfs_freemem` maps chunks of a file and invalidates them with `msync(MS_INVALIDATE)`. AIO write sets up a random offset through `flowoplib_iosetup`, allocates an `aiolist_t`, fills `aiocb64`, submits `aio_write64`, and records flowop timing. AIO wait reaps roughly half of outstanding requests or one minimum, using either `aio_waitn64` or polling `aio_error64`.

### State And Persistence
The filesystem vector is global process state. AIO state is stored on each threadflow's `tf_aiolist`. The wrappers operate on external filesystem state and file descriptors in `fb_fdesc_t`. No separate persistence is maintained by the plugin.

### Dependencies And Integration Points
It depends on `filebench.h`, `fsplug.h`, `flowop.h`, `threadflow.h`, and POSIX filesystem/AIO headers. `fileset.c` and `flowop_library.c` call through the `FB_*` macros backed by `fs_functions_vec`.

### Risks
`fb_lfs_recur_rm` constructs `rm -rf %s` with `snprintf` and `system`, so paths with shell metacharacters are dangerous. AIO list handling has duplicated `break` and does not free deallocated `aiolist_t` nodes, which may leak during long runs. `fb_lfs_freemem` does not check `mmap64` failure before `msync`/`munmap`. Most wrappers return raw system errors and leave interpretation to callers.

### Test Signals
Tests should verify vector initialization, all wrapper return paths, recursive removal safety with controlled paths, AIO submit/reap behavior when enabled, direct I/O/fadvise integration through fileset opens, and portability paths where 64-bit or AIO functions are macro-mapped.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/fb_localfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/fb_random.c -->
## sources/test-tools/filebench/fb_random.c

### Purpose
`fb_random.c` provides Filebench random number helpers and random-distribution objects. It can draw raw random values from mtwist or an `avd_t` random variable, apply max/round constraints, and initialize distribution objects for uniform, gamma, or table-driven workload parameters.

### Important APIs, Types, And Functions
Public APIs are `fb_random64`, `fb_random32`, `randdist_alloc`, and `randdist_init`. Internal helpers include `fb_random_probability`, `fb_rand_src_rand48`, `fb_rand_src_random`, `rand_uniform_get`, `rand_gamma_get`, `rand_table_get`, and `rand_seed_set`. Distribution objects are `randdist_t` from `fb_random.h`.

### Control Flow
`fb_random64` either obtains a value from an `avd_t` random variable or calls `mt_llrand`, normalizes it to `[0,max]`, subtracts `round` from `max` to keep later I/O ranges safe, and rounds down to a multiple when requested. `fb_random32` delegates to the 64-bit path and casts. `randdist_alloc` allocates a shared-memory distribution and links it into `shm_rand_list`. `randdist_init` resolves AVD parameters, selects the generation function by `rnd_type`, chooses either `erand48` seeded from `rnd_seed` or Filebench's mtwist source, and converts any probability table into a 100-slot normalized lookup table.

### State And Persistence
Random distribution definitions live in shared memory through `filebench_shm->shm_rand_list`. Each distribution stores resolved means, gamma, min, round, random source state (`rnd_xi`), and function pointers. The mtwist default state is external global state. No persistent files are written.

### Dependencies And Integration Points
It includes `filebench.h`, `ipc.h`, `gamma_dist.h`, and `cvars/mtwist/mtwist.h`. Variables and parser-created random distributions use `randdist_t`; fileset picking and flowops use `fb_random64` for offsets and random selections.

### Risks
`fb_random64` subtracts `round` from `max` without guarding `round > max`, which can underflow. Table initialization logs but does not abort if percentages do not total exactly 100, leaving uninitialized lookup slots possible. `erand48` source state is per distribution, while mtwist default state may be shared. Rounding uses floating-point conversion for large integers, which can lose precision near `UINT64_MAX`.

### Test Signals
Tests should cover max/round boundaries, avd-backed random validation, deterministic seeded generator mode, uniform/gamma/table distribution initialization, malformed probability tables, and 32-bit/64-bit macro selection via `filebench.h`.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/fb_random.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/fb_random.h -->
## sources/test-tools/filebench/fb_random.h

### Purpose
`fb_random.h` declares Filebench random helper APIs and defines the structures used for random distribution variables in workload definitions.

### Important APIs, Types, And Functions
`probtabent_t` represents parsed probability table segments. `randfunc_t` is a normalized lookup-table entry with base and range. `randdist_t` stores distribution function pointers, source function pointers, AVD parameters, resolved double/integer values, table entries, lookup table, `erand48` seed words, and type flags. Public functions are `fb_random64`, `fb_random32`, `randdist_alloc`, and `randdist_init`.

### Control Flow
The header establishes the initialization model: parser code fills a `randdist_t` with type/source/parameter AVDs and optional probability table entries, then calls `randdist_init` to resolve function pointers and numeric tables before values are generated through `rnd_get`.

### State And Persistence
`randdist_t` objects are linked through `rnd_next` and commonly allocated in shared memory. They store both declarative AVD pointers and resolved values, so they are mutable initialization products rather than immutable specifications.

### Dependencies And Integration Points
It includes `filebench.h` for `avd_t`, `fbint_t`, and shared runtime types. `vars.c` and parser code use these structures to represent random variables; `fb_random.c` implements the declared behavior.

### Risks
The function-pointer fields require successful initialization before use. `PF_TAB_SIZE` is fixed at 100, so probability table percentages are expected to map to integer slots. Type/source flags share `rnd_type` bits, so masks must be used correctly. No ownership comments are provided for `probtabent_t` chains.

### Test Signals
Compile tests should validate consumers can allocate and initialize all distribution types. Runtime tests should inspect `rnd_get`, `rnd_src`, `rnd_rft`, and resolved fields after `randdist_init` for uniform, gamma, table, mtwist, and generator source modes.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/fb_random.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/fbtime.c -->
## sources/test-tools/filebench/fbtime.c

### Purpose
`fbtime.c` supplies a portable fallback implementation of Solaris-style `gethrtime()` when the platform does not provide it. Filebench uses high-resolution nanosecond timestamps for event generation, flowop timing, and reporting.

### Important APIs, Types, And Functions
The only implemented function is `gethrtime(void)` under `#ifndef HAVE_GETHRTIME`. It returns `hrtime_t`, defined in `fbtime.h` for fallback builds.

### Control Flow
The fallback calls `gettimeofday`, multiplies seconds by one billion, converts microseconds to nanoseconds, adds them, and returns the result. If the platform already has `gethrtime`, this file contributes no replacement function.

### State And Persistence
The function is stateless and writes no persistent data. It returns wall-clock-derived time rather than a monotonic clock in fallback mode.

### Dependencies And Integration Points
It includes `sys/time.h`, `stdlib.h`, `stdio.h`, `fbtime.h`, `config.h`, and `filebench.h`. `eventgen.c` and `fileset.c` call `gethrtime` for elapsed-time calculations.

### Risks
`gettimeofday` can move backward or jump with system clock adjustments, unlike a monotonic high-resolution timer. There is no error handling for `gettimeofday` failure. Precision is microsecond-derived even though the return unit is nanoseconds.

### Test Signals
Tests should verify increasing values under normal conditions, approximate unit conversion, compilation with and without `HAVE_GETHRTIME`, and tolerance in callers for non-monotonic fallback behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/fbtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/fbtime.h -->
## sources/test-tools/filebench/fbtime.h

### Purpose
`fbtime.h` abstracts high-resolution time definitions for Filebench. It declares a fallback `hrtime_t` and `gethrtime` only on systems that lack a native implementation, and it defines floating conversion constants.

### Important APIs, Types, And Functions
When `HAVE_GETHRTIME` is absent, the header typedefs `hrtime_t` to `uint64_t` and declares `gethrtime(void)`. It defines `SEC2NS_FLOAT` and `SEC2MS_FLOAT` as floating constants for seconds-to-nanoseconds and seconds-to-micro/millisecond-style scaling used by timing calculations.

### Control Flow
There is no runtime control flow. Compile-time configuration controls whether the fallback type and function declaration are visible.

### State And Persistence
The header defines no state. It standardizes units and declarations for code that needs elapsed time.

### Dependencies And Integration Points
It includes `config.h` and conditionally `stdint.h`. `fbtime.c` implements the fallback. Filebench modules use the constants and `gethrtime` name without caring whether the platform is Solaris-like or using the fallback.

### Risks
Callers may assume monotonic nanosecond precision even on fallback builds where `fbtime.c` uses `gettimeofday`. The macro `SEC2MS_FLOAT` is named as milliseconds but set to `1000000.0`, which is microseconds per second; callers need to understand the intended unit context.

### Test Signals
Build tests should cover both native and fallback configurations. Runtime tests should validate elapsed-time arithmetic in event generation and reports on fallback systems.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/fbtime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/filebench.h -->
## sources/test-tools/filebench/filebench.h

### Purpose
`filebench.h` is the umbrella header for the Filebench runtime. It normalizes platform differences, defines shared scalar types and constants, declares core globals and logging/shutdown functions, and includes most subsystem headers.

### Important APIs, Types, And Functions
Important types and constants include `fbint_t`, `boolean_t`, `u_longlong_t`, `uint_t`, compatibility aliases for 64-bit file APIs, `KB`/`MB`/`GB`, `MMAP_SIZE`, `FILEBENCH_VERSION`, prompt and line limits, shutdown wait seconds, and status codes `FILEBENCH_DONE`, `FILEBENCH_OK`, `FILEBENCH_ERROR`, and `FILEBENCH_NORSC`. It declares `my_pid`, `my_procflow`, `execname`, `filebench_log`, `filebench_shutdown`, and `filebench_plugin_funcvecinit`. It maps `fb_random` to `fb_random64` or `fb_random32` based on word size.

### Control Flow
The header itself drives compile-time control flow through feature macros from `config.h`. It maps missing `off64_t`, `stat64`, `open64`, `pread64`, AIO, mmap, and related symbols to portable equivalents. It also supplies a fallback `sigignore` implementation where needed.

### State And Persistence
It declares process-global runtime state but does not define it. By including many subsystem headers, it establishes a shared-memory-heavy runtime model centered around `filebench_shm` from included IPC definitions.

### Dependencies And Integration Points
Nearly every Filebench C file includes this header directly or indirectly. It pulls in system headers, then Filebench subsystems such as flags, vars, custom variables, AVL, stats, procflow, misc, filesystem plugin, filesets, threadflow, flowops, random, and IPC.

### Risks
As an umbrella header, it creates heavy coupling and potential include cycles. Compatibility macros can hide platform behavior differences, especially around 64-bit file APIs and AIO. Declaring `extern int errno` is obsolete on many modern platforms where `errno` is thread-local macro-backed. The `fb_random` macro changes behavior by architecture.

### Test Signals
Build matrix coverage across Linux, FreeBSD, Solaris-like configurations, AIO/no-AIO, and 32-bit/64-bit is the main signal. Unit tests should verify status-code assumptions and random macro selection in dependent modules.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/filebench.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/fileset.c -->
## sources/test-tools/filebench/fileset.c

### Purpose
`fileset.c` implements Filebench filesets: logical trees of files and directories used by workloads. It defines, populates, preallocates, picks, opens, marks busy/unbusy, prints, and deletes fileset entries while tracking membership in AVL trees.

### Important APIs, Types, And Functions
Public APIs include `fileset_define`, `fileset_createsets`, `fileset_delete_all_filesets`, `fileset_openfile`, `fileset_pick`, `fileset_unbusy`, `fileset_resolvepath`, `fileset_find`, `fileset_iter`, `fileset_print`, plus declared-but-not-present-in-this-file histogram functions from the header. Important internal helpers include `fileset_mkdir`, `fileset_create_subdirs`, `fileset_alloc_file`, `fileset_alloc_leafdir`, `fileset_pickreset`, `fileset_find_entry`, `fileset_create`, `fileset_populate_file`, `fileset_populate_leafdir`, `fileset_populate_subdir`, `fileset_populate`, and `fileset_checkraw`.

### Control Flow
Workloads call `fileset_define` during parsing to allocate a shared fileset and link it to `shm_filesetlist`. `fileset_createsets` validates all definitions once, handles raw devices, calls `fileset_populate` to construct in-memory entries, then `fileset_create` to create directories and preallocate selected files/leaf directories. Population recursively builds directory/file entries based on entry counts, leaf directory counts, directory width, depth, and gamma/random variables. Runtime flowops call `fileset_pick` to choose a file/dir/leafdir from the appropriate AVL tree, blocking on condition variables if no idle entries are available. Callers eventually call `fileset_unbusy`, which updates existence flags, moves entries between AVL trees, adjusts idle counts, and signals waiters.

### State And Persistence
Filesets and entries are allocated in Filebench shared memory and mirrored to real filesystem state when created. Each `fileset_t` maintains lists, AVL trees for free/existing/non-existing files and leafdirs, directory trees, idle counters, condition variables, pick locks, rotors, and byte/file counts. Persistent side effects are actual directories/files under `fs_path/fs_name`; deletion calls recursive remove unless raw-device mode is active.

### Dependencies And Integration Points
It depends on `filebench.h`, `fileset.h`, `gamma_dist.h`, `utils.h`, and `fsplug.h`. It calls through `FB_*` filesystem plugin macros implemented by `fb_localfs.c` by default. Parser code creates filesets, flowops pick/open entries, `fb_random64` provides random selection, and `fb_avl` stores membership indexes.

### Risks
`filecreate_done` is global, so filesets defined after creation are ignored, as the code comment notes. Recursive directory population can be deep depending on random parameters. `fileset_resolvepath` allocates paths that callers must free. `fileset_create` uses `rand()` for preallocation selection without explicit seeding in this file. Parallel preallocation uses shared counters and detached threads; failures are signaled through `shm_fsparalloc_count = -1`. Path construction relies on fixed `MAXPATHLEN` buffers. Underlying recursive remove safety depends on the filesystem plugin.

### Test Signals
Tests should cover define/find/iterate, raw-device detection, populate counts and AVL membership, pick/unbusy transitions for existing/non-existing/free entries, create/reuse/trust-tree behavior, parallel preallocation success/failure, open flags for direct/sync/fadvise, and deletion cleanup. Integration tests need real temporary directories and the local filesystem plugin.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/fileset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/fileset.h -->
## sources/test-tools/filebench/fileset.h

### Purpose
`fileset.h` defines the public structures, flags, and function prototypes for Filebench filesets and fileset entries. It is the contract used by parser, flowop, filesystem, and statistics code to work with logical collections of files and directories.

### Important APIs, Types, And Functions
`filesetentry_t` represents a file, internal directory, or leaf directory with list links, parent pointer, embedded AVL link, index, path, depth, size, open count, flags, and back-pointer to its fileset. `fileset_t` stores workload parameters (`fs_name`, `fs_path`, entries, leafdirs, size, create/reuse/read-only flags), computed counts, locks, condition variables, AVL trees, rotors, lists, and histogram state. Flags define entry type and state (`FSE_TYPE_FILE`, `FSE_TYPE_DIR`, `FSE_TYPE_LEAFDIR`, `FSE_FREE`, `FSE_EXISTS`, `FSE_BUSY`, `FSE_REUSING`, `FSE_THRD_WAITNG`) plus pick semantics (`FILESET_PICK*`) and fileset attributes (`FILESET_IS_RAW_DEV`, `FILESET_IS_FILE`). Public prototypes expose create, define, find, pick, open, resolve, iterate, print, unbusy, histogram, and cleanup functions.

### Control Flow
The header establishes that callers define filesets, create/populate them, pick entries under runtime flowops, open files, then release entries through `fileset_unbusy`. The pick flags determine whether callers need files, directories, leaf directories, unique/free entries, existing entries, non-existing entries, or index-based selection.

### State And Persistence
`fileset_t` combines shared-memory runtime state with real filesystem intent. Its AVL trees classify entries by existence/free state, while idle counters and condition variables coordinate concurrent workers. Histogram pointers allow shared access tracking.

### Dependencies And Integration Points
It includes `filebench.h`, which supplies `avd_t`, `fbint_t`, `avl_node_t`, `avl_tree_t`, pthread types, and filesystem descriptor types through nested includes. `fileset.c` implements most prototypes; flowops consume `fileset_pick` and `fileset_openfile`.

### Risks
The structure is large and shared across modules, so layout changes have wide blast radius. `FSE_MAXPATHLEN` is only 16 for per-entry generated names, while full paths use `MAXPATHLEN` elsewhere. `fs_file_exrotor` is indexed by thread id up to `FSE_MAXTID`; callers must keep ids in range. Many fields are protected by `fs_pick_lock`, but the header relies on comments rather than type-enforced access.

### Test Signals
Tests should check flag combinations, pick semantics, AVL offset correctness for `fse_link`, shared-memory initialization, thread-id bounds, and compatibility of structure layout with parser and flowop code.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/fileset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/flag.h -->
## sources/test-tools/filebench/flag.h

### Purpose
`flag.h` provides a tiny volatile integer flag abstraction used by Filebench code that needs a simple set/clear/query/wait primitive.

### Important APIs, Types, And Functions
It defines `flag_t` as `volatile int` and four static inline functions: `clear_flag`, `set_flag`, `query_flag`, and `wait_flag`. `wait_flag` spins until `query_flag` returns nonzero.

### Control Flow
`clear_flag` writes zero, `set_flag` writes one, `query_flag` tests nonzero, and `wait_flag` is a busy-wait loop. There is no sleeping, yielding, timeout, or memory-barrier operation.

### State And Persistence
The state is entirely the caller-provided integer. The header does not allocate memory or persist anything. Since the integer is volatile, compilers should reload it in the spin loop, but this is not a full synchronization primitive.

### Dependencies And Integration Points
It is included by `filebench.h`, making it widely available throughout the runtime. It can be used for simple inter-thread or signal-adjacent flags where stronger pthread synchronization is not required.

### Risks
`volatile` does not provide atomicity or ordering across threads on all architectures. `wait_flag` can burn CPU indefinitely and has no cancellation path. Concurrent writers/readers can race if callers assume mutex-like behavior.

### Test Signals
Tests should be minimal: compile the inline API, verify set/clear/query behavior, and avoid using `wait_flag` in unit tests without a bounded helper thread. Higher-level tests should prefer pthread condition variables for real synchronization.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/flag.h -->
