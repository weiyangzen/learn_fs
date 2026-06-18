# Research Report: subset-b-009218

Grouped research for Filebench Autotools configuration, CVAR distribution plugins, token/trace helpers, and selected Mersenne Twister sources. Each section preserves the source path for deterministic reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/configure.ac -->
# `sources/test-tools/filebench/configure.ac`

Purpose: Autoconf input for Filebench 1.5-alpha3. It discovers compiler tools, platform headers, libc functions, libraries, OS-specific direct I/O/AIO/semaphore features, and emits `Makefile`, `workloads/Makefile`, and `cvars/Makefile`.

Important APIs and macros: `AC_INIT`, `AC_CONFIG_MACRO_DIRS`, `AM_CONFIG_HEADER`, `AM_INIT_AUTOMAKE([subdir-objects])`, `AC_PROG_CC`, `AC_PROG_LIBTOOL`, `AC_PROG_YACC`, `AC_PROG_LEX`, many `AC_CHECK_HEADERS`, `AC_CHECK_FUNCS`, `AC_CHECK_LIB`, `AC_TRY_COMPILE`, `AC_DEFINE`, and `AC_OUTPUT`. It defines feature macros consumed by the C tree, including `HAVE_AIO`, `HAVE_AIOWAITN`, `HAVE_SYSV_SEM`, `HAVE_ROBUST_MUTEX`, `HAVE_PROCSCOPE_PTHREADS`, `HAVE_OFF64_T`, `HAVE_STAT64`, `HAVE_FADVISE`, `HAVE_IOPRIO`, `HAVE_O_DIRECT`, `HAVE_NOCACHE_FCNTL`, and others.

Control flow: the script initializes the package, checks programs, then performs simple header/function checks, specialized type/structure compile probes, library checks, optional `--enable-system`, and final direct-I/O feature detection. Fatal behavior is limited to missing `math.h`.

State and persistence: generated `config.h` and Makefiles persist platform decisions. No runtime state is modified except normal configure-generated cache/output files. It probes `/proc/sys/kernel/shmmax` but only records whether it exists.

Dependencies and integration: integrates Autotools with `sources/test-tools/filebench/cvars/Makefile.am` and workload builds. Links expected libraries include `rt`, `m`, `pthread`, and `dl`; generated macros drive portability branches in the wider Filebench source.

Risks: uses obsolete Autoconf macros such as `AC_TRY_COMPILE`, `AM_CONFIG_HEADER`, and `AC_PROG_LIBTOOL`. Several tests use shell `==`, which is less portable than `=` in `/bin/sh`. Some `AC_CHECK_FUNCS` blocks define the same feature macro once per found function, which can overstate grouped capability unless all call sites also test individual `HAVE_*` macros. Comments note `semtimedop` handling may be incorrect. Duplicate `AC_FUNC_MMAP` is harmless but noisy.

Test signals: successful `autoreconf/configure` should produce `config.h` and the three Makefiles. Regression checks should include Linux and non-Linux configurations for direct I/O, AIO, semaphore, large-file, and pthread feature macros.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/Makefile.am -->
# `sources/test-tools/filebench/cvars/Makefile.am`

Purpose: Automake recipe that builds Filebench custom-variable distribution plugins as libtool modules installed below `@libdir@/filebench`.

Important targets: `lib_LTLIBRARIES` lists `libcvar-erlang.la`, `libcvar-exponential.la`, `libcvar-lognormal.la`, `libcvar-normal.la`, `libcvar-triangular.la`, `libcvar-uniform.la`, `libcvar-weibull.la`, and `libcvar-gamma.la`. `common_cvar_files` expands to `mtwist/mtwist.c mtwist/randistrs.c cvar_tokens.c`.

Control flow: each plugin target compiles its distribution-specific source plus the shared tokenizer and Mersenne Twister/random distribution implementation, except gamma also links the common files but internally uses `drand48()` rather than the MT state.

State and persistence: build output is a set of `.la` libraries installed under the Filebench library directory. No runtime state is defined here.

Dependencies and integration: depends on Autotools substitutions from `configure.ac`, libtool, and the shared CVAR ABI declared in `cvar.h`. These modules are dynamically loaded by Filebench by symbol name.

Risks: shared files are compiled into every plugin, increasing duplicated code and making fixes require rebuilding all modules. `cvar-gamma.c` does not use the same RNG pathway as the other modules despite being built with `mtwist` sources.

Test signals: `make -C cvars` should produce every listed `.la`; install layout should place them in `libdir/filebench` so Filebench can locate CVAR modules.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-erlang.c -->
# `sources/test-tools/filebench/cvars/cvar-erlang.c`

Purpose: Filebench CVAR plugin returning Erlang-distributed random values.

Important APIs/functions: implements mandatory CVAR entry points `cvar_alloc_handle`, `cvar_next_value`, `cvar_free_handle`, plus optional `cvar_revalidate_handle`, `cvar_usage`, and `cvar_version`. It uses `tokenize`, `find_token`, `unused_tokens`, `free_tokens`, `mts_goodseed`, `mts_mark_initialized`, and `rds_erlang`.

Control flow: allocation tokenizes parameters, reads `shape` with `atoi` and `rate` with `atof`, defaults missing values, rejects negative values, rejects unknown tokens, seeds an `mt_state`, allocates a shared handle with Filebench's allocator, and copies stack state into it. `cvar_next_value` validates handle/value pointers and calls `rds_erlang(&h->state, h->shape, h->rate)`.

State and persistence: `handle_t` contains MT state plus `shape` and `rate`; the handle can live in Filebench shared memory. `cvar_revalidate_handle` marks the embedded MT state initialized after process changes.

Dependencies and integration: includes `mtwist/mtwist.h`, `mtwist/randistrs.h`, `cvar.h`, `cvar_trace.h`, `cvar_tokens.h`, and `cvar-erlang.h`. Loaded by Filebench through the symbol contract in `cvar.h`.

Risks: validation accepts zero despite error text saying non-zero positive; `atoi`/`atof` do not detect malformed numeric strings. Parameter name `rate` is passed to `rds_erlang` as the distribution mean per `randistrs` naming, so semantics may be confusing. Null `cvar_parameters` returns NULL via `tokenize`.

Test signals: instantiate with default, explicit `shape:2;rate:1.0`, unsupported parameter, negative values, zero values, and post-fork/shared-memory revalidation; sampling should advance embedded MT state.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-erlang.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-erlang.h -->
# `sources/test-tools/filebench/cvars/cvar-erlang.h`

Purpose: Private header for the Erlang CVAR module.

Important types/macros: parameter keys `RER_SHAPE` and `RER_RATE`, defaults `RER_SHAPE_DEFAULT` and `RER_RATE_DEFAULT`, `VERSION`, `USAGE_LEN`, global `usage`, and `handle_t` containing `mt_state state`, `int shape`, and `double rate`.

Control flow: no executable flow; it supplies compile-time constants and the handle layout consumed by `cvar-erlang.c`.

State and persistence: `handle_t` is copied into Filebench-managed memory and persists RNG state across generated values. `usage` caches the generated usage string for the module process.

Dependencies and integration: includes `mtwist/mtwist.h`; must match `cvar-erlang.c` and `randistrs` expectations for `rds_erlang`.

Risks: `usage` is a non-static definition in a header; safe only because each plugin builds one distribution source, but it would cause duplicate symbols if multiple CVAR headers were linked into one object set. `rate` naming may not match `rds_erlang` mean semantics.

Test signals: compile the module and verify `cvar_usage()` prints defaults and example matching these macros.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-erlang.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-exponential.c -->
# `sources/test-tools/filebench/cvars/cvar-exponential.c`

Purpose: Filebench CVAR plugin returning exponentially distributed random values.

Important APIs/functions: CVAR entry points `cvar_alloc_handle`, `cvar_revalidate_handle`, `cvar_next_value`, `cvar_free_handle`, `cvar_usage`, and `cvar_version`. Uses token helpers, `mts_goodseed`, `mts_mark_initialized`, and `rds_exponential`.

Control flow: allocation parses optional `mean`, defaults to `1.0`, clamps negative means to zero, rejects unused tokens, seeds MT state, allocates the handle through Filebench, and copies it. Sampling validates pointers and returns `rds_exponential(&h->state, h->mean)`.

State and persistence: `handle_t` stores `mt_state` and `mean`; revalidation marks the state initialized when reused in another process. Static `usage` caches formatted help.

Dependencies and integration: depends on `mtwist`, `randistrs`, the CVAR ABI, trace macros, and tokenizer. Built as `libcvar-exponential.la`.

Risks: negative mean silently becomes zero; this may hide bad workload parameters. `atof` accepts malformed strings as zero. `cvar_usage()` mentions only key/value assignment and omits the parameter delimiter because there is one parameter.

Test signals: default allocation, explicit `mean`, negative mean behavior, unsupported parameter handling, null handle/value checks, and sample values from `rds_exponential`.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-exponential.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-exponential.h -->
# `sources/test-tools/filebench/cvars/cvar-exponential.h`

Purpose: Private definitions for the exponential CVAR module.

Important types/macros: `RE_MEAN`, `RE_MEAN_DEFAULT`, `VERSION`, `USAGE_LEN`, global `usage`, and `handle_t` with `mt_state state` and `double mean`.

Control flow: no runtime logic; controls accepted parameter names, defaults, usage formatting, and shared handle shape.

State and persistence: embedded MT state persists per CVAR handle. Static-looking but externally linked `usage` stores help text for the module.

Dependencies and integration: includes `mtwist/mtwist.h`; consumed by `cvar-exponential.c`.

Risks: global `usage` definition in a header would conflict in a combined build. No prototype declarations are provided here; exported function contract comes from `cvar.h`.

Test signals: compile with the source and verify `cvar_usage()` reflects `mean` default `1.0`.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-exponential.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-gamma.c -->
# `sources/test-tools/filebench/cvars/cvar-gamma.c`

Purpose: Standalone gamma-distribution CVAR plugin using Knuth algorithms from original Filebench distribution code.

Important APIs/functions: CVAR entry points plus private `gamma_dist_knuth_algG` for `0 < a <= 1`, `gamma_dist_knuth_algA` for `a > 1`, `default_src`, `gamma_dist_knuth`, and `gamma_dist_knuth_src`. Parameters are `mean` and `gamma`; handle stores `mean`, `scaledmean`, and `gamma`.

Control flow: allocation tokenizes parameters, reads `mean` and `gamma`, rejects only `gamma == 0`, computes `scaledmean = mean / gamma`, rejects unknown tokens, and allocates the handle. Sampling validates pointers and calls `gamma_dist_knuth(h->gamma, h->scaledmean)`, which selects algorithm G or A and uses rejection loops driven by `drand48()`.

State and persistence: unlike other CVAR modules, no RNG state is stored in the handle. Randomness comes from process-global `drand48()` state. `cvar_revalidate_handle` is a no-op.

Dependencies and integration: includes standard `math.h`, `stdlib.h`, CVAR ABI, trace, and tokenizer. Built as `libcvar-gamma.la`; linked with the common MT sources by `Makefile.am` even though this file does not call them.

Risks: global `drand48()` is not per-handle, not explicitly seeded here, and may be non-reentrant or platform-limited. Negative `gamma` is accepted and can route into formulas whose documented domain is positive. Negative/zero mean is not validated. `gamma_dist_knuth_src` is unused in this plugin. `atof` parsing is weak.

Test signals: default sampling, explicit positive mean/gamma, `gamma:0` rejection, negative gamma/mean edge cases, reproducibility under controlled `srand48`, and concurrent handles sharing global RNG state.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-gamma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-lognormal.c -->
# `sources/test-tools/filebench/cvars/cvar-lognormal.c`

Purpose: Filebench CVAR plugin returning lognormal random values.

Important APIs/functions: standard CVAR entry points; uses tokenizer helpers, `mts_goodseed`, `mts_mark_initialized`, and `rds_lognormal`.

Control flow: allocation parses `shape` and `scale`, defaults both to `1.0`, rejects negative values, rejects unknown tokens, seeds MT state, allocates/copies the handle, and frees token state. Sampling calls `rds_lognormal(&h->state, h->shape, h->scale)`.

State and persistence: `handle_t` stores MT state, shape, and scale in Filebench-managed memory. Revalidation marks MT state initialized after process-local reload.

Dependencies and integration: built as `libcvar-lognormal.la`; depends on `randistrs` for distribution math and `cvar-lognormal.h` for layout/defaults.

Risks: validation text says non-zero positive but zero is accepted. `atof` masks invalid strings as zero. Null pointer errors use `cvar_trace`, so they disappear in non-DEBUG builds.

Test signals: default and explicit shape/scale sampling, negative parameter rejection, zero handling, unsupported token rejection, and revalidation before sampling reused handles.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-lognormal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-lognormal.h -->
# `sources/test-tools/filebench/cvars/cvar-lognormal.h`

Purpose: Private declarations for the lognormal CVAR module.

Important types/macros: `RLN_SHAPE`, `RLN_SCALE`, defaults, `VERSION`, `USAGE_LEN`, `usage`, and `handle_t` with `mt_state`, `shape`, and `scale`.

Control flow: no executable code; provides compile-time names/defaults and shared memory layout.

State and persistence: `handle_t` persists PRNG and distribution parameters. `usage` caches help output per module.

Dependencies and integration: includes `mtwist/mtwist.h`; used by `cvar-lognormal.c`.

Risks: include guard closing comment says `_RAND_NORMAL_H`, which is misleading though harmless. Header-level global `usage` is fragile outside one-source-per-plugin builds.

Test signals: compile warnings should catch guard/comment mismatch only if style checks exist; runtime usage should show shape and scale defaults.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-lognormal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-normal.c -->
# `sources/test-tools/filebench/cvars/cvar-normal.c`

Purpose: Filebench CVAR plugin returning normally distributed random values.

Important APIs/functions: standard CVAR entry points; uses `rds_normal`, token helpers, and Mersenne Twister seeding/revalidation.

Control flow: allocation reads optional `mean` and `sigma`, defaults to `0.0` and `1.0`, rejects unused tokens, seeds state, allocates the handle, and copies it. Sampling validates inputs and calls `rds_normal(&h->state, h->mean, h->sigma)`.

State and persistence: handle contains embedded MT state plus mean/sigma; `usage` caches formatted help. Revalidation restores MT initialized flag for shared memory handles.

Dependencies and integration: built as `libcvar-normal.la`; depends on `cvar-normal.h`, tokenizer, trace, `mtwist`, and `randistrs`.

Risks: no validation rejects negative sigma, so invalid standard deviations can be passed to `rds_normal`. `atof` gives no parse diagnostics. Null pointer diagnostics use trace macros and may be compiled out.

Test signals: sample defaults, non-default mean/sigma, negative sigma behavior, unsupported parameter rejection, and state revalidation.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-normal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-normal.h -->
# `sources/test-tools/filebench/cvars/cvar-normal.h`

Purpose: Private definitions for normal CVAR parameters and handle layout.

Important types/macros: `RN_MEAN`, `RN_SIGMA`, defaults, `VERSION`, `USAGE_LEN`, `usage`, and `handle_t` with `mt_state state`, `double mean`, `double sigma`.

Control flow: no runtime behavior.

State and persistence: handle persists PRNG state and distribution parameters in Filebench memory.

Dependencies and integration: includes `mtwist/mtwist.h` and is consumed by `cvar-normal.c`.

Risks: header defines a global `usage`; fine for one plugin object but unsafe in aggregate builds. It does not encode sigma constraints, leaving validation to source code, which currently does not enforce positivity.

Test signals: compile and `cvar_usage()` should expose default mean `0.0` and sigma `1.0`.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-normal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-triangular.c -->
# `sources/test-tools/filebench/cvars/cvar-triangular.c`

Purpose: Filebench CVAR plugin returning triangular-distributed random values.

Important APIs/functions: standard CVAR entry points; uses `rds_triangular`, token helpers, and MT state management.

Control flow: allocation parses `lower`, `upper`, and `mode`, defaults to `0.0`, `1.0`, and `0.5`, validates `upper >= lower` and `mode` within bounds, rejects unused tokens, seeds MT state, and allocates/copies the handle. Sampling calls `rds_triangular(&h->state, h->lower, h->upper, h->mode)`.

State and persistence: handle stores MT state and the three distribution parameters. Revalidation marks the embedded state initialized.

Dependencies and integration: built as `libcvar-triangular.la`; depends on `cvar-triangular.h`, tokenizer, trace, `mtwist`, and `randistrs`.

Risks: equal lower/upper is accepted despite message requiring greater-than; that may produce degenerate output. `atof` lacks strict validation. Null pointer logs are emitted with `cvar_log_error` and remain visible.

Test signals: valid defaults, custom bounds/mode, upper-lower inversion, out-of-range mode, equal bounds, unsupported tokens, and sampling reproducibility with a seeded state.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-triangular.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-triangular.h -->
# `sources/test-tools/filebench/cvars/cvar-triangular.h`

Purpose: Private definitions for triangular CVAR parameters and state.

Important types/macros: `RT_LOWER`, `RT_UPPER`, `RT_MODE`, defaults, `VERSION`, `USAGE_LEN`, `usage`, and `handle_t` containing `mt_state`, `lower`, `upper`, and `mode`.

Control flow: none; constants drive parse and usage output in `cvar-triangular.c`.

State and persistence: handle persists generator state and distribution bounds/mode.

Dependencies and integration: includes `mtwist/mtwist.h`; tied to `rds_triangular` argument order.

Risks: global `usage` symbol in a header. No compile-time enforcement that default mode lies inside bounds, so source validation is the safeguard.

Test signals: generated usage should list all three defaults and example syntax.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-triangular.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-uniform.c -->
# `sources/test-tools/filebench/cvars/cvar-uniform.c`

Purpose: Filebench CVAR plugin returning floating uniform random values.

Important APIs/functions: standard CVAR entry points; uses `rds_uniform`, token helpers, and MT state functions.

Control flow: allocation parses `lower` and `upper`, defaults to `0.0` and `1.0`, logs if `lower > upper`, checks unsupported tokens, seeds state, allocates/copies handle, and sampling calls `rds_uniform(&h->state, h->lower, h->upper)`.

State and persistence: per-handle MT state plus lower/upper bounds, persisted through Filebench memory. Revalidation marks the state initialized.

Dependencies and integration: built as `libcvar-uniform.la`; depends on `cvar-uniform.h`, `randistrs`, tokenizer, and trace.

Risks: validation logs `lower > upper` but does not `goto out`, so invalid bounds still produce an allocated handle and inverted-range samples. `atof` parsing is weak. Unsupported tokens are rejected after validation.

Test signals: defaults, explicit bounds, inverted bounds expecting allocation failure but currently not failing, unsupported tokens, null output pointer, and repeated sampling.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-uniform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-uniform.h -->
# `sources/test-tools/filebench/cvars/cvar-uniform.h`

Purpose: Private definitions for the uniform CVAR module.

Important types/macros: `RU_LOWER`, `RU_UPPER`, defaults, `VERSION`, `USAGE_LEN`, `usage`, and `handle_t` with `mt_state state`, `double lower`, and `double upper`.

Control flow: no executable flow.

State and persistence: handle persists lower/upper bounds and MT state.

Dependencies and integration: includes `mtwist/mtwist.h`; consumed by `cvar-uniform.c`.

Risks: header-defined global `usage`; no local invariant support for lower <= upper beyond source validation.

Test signals: usage output and handle allocation should align with defaults in this header.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-uniform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-weibull.c -->
# `sources/test-tools/filebench/cvars/cvar-weibull.c`

Purpose: Filebench CVAR plugin returning Weibull-distributed random values.

Important APIs/functions: standard CVAR entry points; uses `rds_weibull`, tokenizer helpers, and MT state management.

Control flow: allocation parses `shape` and `scale`, defaults to `1.0`, rejects negative values, rejects unused tokens, seeds MT state, allocates/copies the handle, and sampling calls `rds_weibull(&h->state, h->shape, h->scale)`.

State and persistence: handle contains MT state and shape/scale. Revalidation marks MT state initialized.

Dependencies and integration: built as `libcvar-weibull.la`; depends on `cvar-weibull.h`, `randistrs`, trace, tokenizer, and `mtwist`.

Risks: zero shape or scale is accepted despite error text saying non-zero positive. Shape error text says integer even though the field is `double`. `atof` lacks strict parsing. Null pointer diagnostics use trace and may compile out.

Test signals: default and explicit sampling, negative value rejection, zero behavior, unsupported parameter handling, and revalidation.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-weibull.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-weibull.h -->
# `sources/test-tools/filebench/cvars/cvar-weibull.h`

Purpose: Private definitions for the Weibull CVAR module.

Important types/macros: `RW_SHAPE`, `RW_SCALE`, defaults, `VERSION`, `USAGE_LEN`, `usage`, and `handle_t` with MT state plus shape/scale doubles.

Control flow: none; consumed by source parsing and usage formatting.

State and persistence: per-handle MT state and parameters persist in Filebench memory.

Dependencies and integration: includes `mtwist/mtwist.h`; paired with `cvar-weibull.c` and `rds_weibull`.

Risks: global `usage` in header; no compile-time validation for positive shape/scale.

Test signals: usage string should include shape/scale defaults and delimiter guidance.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-weibull.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar.h -->
# `sources/test-tools/filebench/cvars/cvar.h`

Purpose: ABI contract between Filebench and dynamically loaded custom-variable modules.

Important APIs: declares optional `cvar_module_init`, `cvar_revalidate_handle`, `cvar_module_exit`, `cvar_usage`, `cvar_version`; mandatory `cvar_alloc_handle`, `cvar_next_value`, and `cvar_free_handle`.

Control flow: Filebench loads a module, optionally initializes it, allocates a handle using Filebench-provided allocation callbacks, revalidates handles that were created in a different process, repeatedly calls `cvar_next_value`, and may call free/exit during teardown.

State and persistence: module handles are allocated with caller-provided memory functions, likely so Filebench can place them in shared memory. Modules must not retain allocator callback pointers.

Dependencies and integration: all CVAR modules include this header and export these exact symbol names for dynamic lookup.

Risks: function prototypes omit `void` in empty parameter lists, which is old-style C and weaker under strict compilers. Lifecycle comments explicitly allow Filebench to skip cleanup callbacks, so modules must tolerate process-exit cleanup. ABI is symbol-name based with no versioned struct.

Test signals: dynamic-loader tests should verify missing optional symbols are tolerated and missing mandatory symbols fail clearly; shared-memory revalidation should be exercised.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar_tokens.c -->
# `sources/test-tools/filebench/cvars/cvar_tokens.c`

Purpose: Parameter tokenizer and linked-list utilities for CVAR modules.

Important APIs/functions: `tokenize`, `find_token`, `unused_tokens`, `free_tokens`, and private `free_token`. Tokens are `key[:value]` pairs separated by `;` by default.

Control flow: `tokenize` duplicates the parameter string, walks delimiter-separated segments, splits each non-empty segment on the first key/value delimiter, rejects empty keys, allocates token nodes and duplicated key/value strings, links them, and returns the head. `find_token` scans by key and modules mark matches as used. `unused_tokens` finds the first unconsumed token. `free_tokens` releases the list.

State and persistence: token lists are transient allocation-time state and are freed before returning from each CVAR allocation.

Dependencies and integration: uses libc `strdup`, `strchr`, `strlen`, `strcmp`, `malloc`, `free`, and trace logging. Included in every CVAR plugin by `Makefile.am`.

Risks: if `parameters == NULL`, `tokenize` returns success without setting `*list_head`, relying on callers initializing it to NULL. Empty parameter elements are ignored, but empty keys in non-empty elements fail. Duplicate keys are allowed; `find_token` returns the first, leaving later duplicates unused and causing unsupported-parameter failure after module parsing. Memory allocation uses raw `malloc`, not Filebench shared allocator, but tokens are transient.

Test signals: empty string, NULL string, `key:value`, `key`, duplicate keys, trailing semicolon, empty key `:value`, unsupported token detection through `used`, and cleanup under allocation failure.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar_tokens.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar_tokens.h -->
# `sources/test-tools/filebench/cvars/cvar_tokens.h`

Purpose: Token utility interface for CVAR parameter parsing.

Important types/macros: `DEFAULT_PARAMETER_DELIMITER` is `;`, `DEFAULT_KEY_VALUE_DELIMITER` is `:`, and `cvar_token_t` stores `key`, optional `value`, `used`, and `next`.

Control flow: declares tokenizer, lookup, unused-token scan, and free functions; no runtime implementation here.

State and persistence: token state is a mutable linked list used during handle allocation. `used` lets modules detect unknown parameters after consuming known keys.

Dependencies and integration: included by all distribution plugins and implemented in `cvar_tokens.c`.

Risks: API exposes mutable linked-list internals, so callers can corrupt list invariants. Delimiters are single chars and there is no escaping/quoting support.

Test signals: compile all modules against the header and unit-test token list behavior through the public functions.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar_tokens.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar_trace.h -->
# `sources/test-tools/filebench/cvars/cvar_trace.h`

Purpose: Lightweight logging and optional debug tracing for CVAR modules.

Important APIs/macros: `cvar_log_error(fmt, ...)` always writes to stderr with a final period. Under `DEBUG`, `cvar_trace(fmt, ...)` logs file/line/function and `cvar_tracebuf` formats a byte buffer as hex. Without `DEBUG`, `cvar_trace` compiles away and `cvar_tracebuf` is a no-op.

Control flow: debug `cvar_tracebuf` allocates a string sized for `0x` plus two hex chars per byte, fills it nibble-by-nibble, prints it, and frees it.

State and persistence: no persistent state; debug buffer allocation is transient.

Dependencies and integration: includes `stdio.h` and `stdlib.h`; used by token and distribution sources.

Risks: debug `cvar_tracebuf` writes `sbuf[2*len + 2] = '\0'` after allocating `2 + 2*len + 1` bytes, an off-by-one write. Several modules use `cvar_trace` for error conditions, meaning diagnostics vanish in non-debug builds. Variadic macro syntax relies on GNU `##__VA_ARGS__`.

Test signals: compile with and without `DEBUG`; run `cvar_tracebuf` under ASAN/Valgrind to catch the terminator write.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/mtcctest.cc -->
# `sources/test-tools/filebench/cvars/mtwist/mtcctest.cc`

Purpose: C++ test and benchmark harness for the `mt_prng` wrapper around the Mersenne Twister implementation.

Important APIs/functions: `main`, `report_timing`, C++ `mt_prng` methods `seed32`, stream save/restore operators, `lrand`, `llrand`, `drand`, `ldrand`, and `operator()`.

Control flow: optional argument sets timing loops in millions. The test seeds with `4357`, saves to `mtccsave`, reseeds with `1`, restores from file, deletes `mtccsave`, compares generated `lrand()` values against a long static `correct_values` vector, then benchmarks long, long long, fast double, long double, and call-operator generation while accumulating into volatile sinks.

State and persistence: creates temporary file `mtccsave` in the current directory to validate stream persistence. Otherwise state is held inside local `mt_prng rng`.

Dependencies and integration: includes `mtwist.h`, C++ streams/iomanip, `unistd.h`, `stdlib.h`, `sys/resource.h`, and `sys/time.h`. Validates the C++ class and stream operators defined in `mtwist.h`/`mtwist.c`.

Risks: default timing loop is 300 million iterations, expensive for routine CI. The test writes a fixed temporary filename in cwd and is not parallel-safe. It uses `unsigned long` expected values, which can vary in width but values are 32-bit.

Test signals: success prints `Validity test...passed.` and timing lines. Failures report expected/got value index and exit nonzero.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/mtcctest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/mttest.c -->
# `sources/test-tools/filebench/cvars/mtwist/mttest.c`

Purpose: C test and benchmark harness for the C Mersenne Twister API.

Important APIs/functions: `main`, `report_timing`, `report_clock_timing`, and exercised APIs `mt_seed32new`, `mt_savestate`, `mt_loadstate`, `mt_lrand`, `mts_lrand`, `mt_llrand`, `mts_llrand`, `mt_drand`, `mts_drand`, `mt_ldrand`, `mts_ldrand`, `mt_seed`, `mt_goodseed`, and `mt_bestseed`.

Control flow: optional argument sets timing loop count in millions. It seeds with `5489`, saves default state to `mtsave`, changes seed, restores state, unlinks the file, compares generated values against a reference vector, verifies function pointers, runs default and explicit-state timing loops for integer and double generation, then times seed functions.

State and persistence: uses global default MT state and a static local `mt_state`. Creates temporary file `mtsave` for save/load validation. Timing accumulators are assigned to volatile variables to prevent optimization.

Dependencies and integration: includes `mtwist.h`, `inttypes.h`, `unistd.h`, `stdio.h`, `stdlib.h`, `sys/resource.h`, and `sys/time.h`. Validates the C interface implemented by `mtwist.c`.

Risks: fixed temp filename is not parallel-safe. Default 300 million loops are costly. Static `mt_state state` is zero-initialized and intentionally relies on lazy seeding. Seed timing can block or vary if `/dev/random` is slow.

Test signals: validity pass/fail, nonzero exit on reference mismatch, timing reports, and warnings if `mt_seed`/`mt_goodseed` return zero or the same seed.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/mttest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/mtwist.c -->
# `sources/test-tools/filebench/cvars/mtwist/mtwist.c`

Purpose: C implementation of MT19937 Mersenne Twister PRNG with explicit-state and default-state APIs, C++ stream operators, seeding helpers, random generation, refresh logic, and state save/load.

Important APIs/functions: `mts_lrand`, `mts_llrand`, `mts_drand`, `mts_ldrand`, default wrappers `mt_lrand`, `mt_llrand`, `mt_drand`, `mt_ldrand`, seeding APIs `mts_seed32`, `mts_seed32new`, `mts_seedfull`, `mts_seed`, `mts_goodseed`, `mts_bestseed`, state APIs `mts_mark_initialized`, `mts_refresh`, `mts_savestate`, `mts_loadstate`, and default wrappers `mt_seed32`, `mt_seed32new`, `mt_seedfull`, `mt_seed`, `mt_goodseed`, `mt_bestseed`, `mt_getstate`, `mt_savestate`, `mt_loadstate`. C++ operators `operator<<` and `operator>>` serialize `mt_prng`.

Control flow: generation checks `stateptr`, refreshes when exhausted, reads reversed state entries, applies tempering macros, and returns 32-bit, 64-bit, or scaled double output. Seeding fills the 624-word state with old or new Knuth recurrence, marks initialization, and often refreshes immediately. Device seeding tries `/dev/urandom` or `/dev/random`, falls back to time, and returns the 32-bit seed. `mts_refresh` computes the MT recurrence in optimized unrolled loops and resets `stateptr`. Save/load writes/reads 624 words plus pointer.

State and persistence: `mt_state` contains 624 32-bit words, `stateptr`, and `initialized`. Global `mt_default_state` supports no-argument APIs. `mt_32_to_double` and `mt_64_to_double` are global conversion constants recalculated on initialization. Save/load persists PRNG state as text.

Dependencies and integration: includes `inttypes.h`, stdio/stdlib, time APIs, and `mtwist.h`. CVAR modules embed `mt_state` in handles and call `mts_goodseed`, `mts_mark_initialized`, and distribution helpers from `randistrs.c`.

Risks: default global state is not thread-safe. `mts_goodseed` may block on `/dev/random`; CVAR allocation uses it per handle. `mts_bestseed` reads a full state from `/dev/random` and can be very slow. Load validates only `stateptr`, not state entropy. `mts_seedfull` aborts on all-zero seed. Text state format is long and unchecked beyond scan success/pointer bounds.

Test signals: `mttest.c` and `mtcctest.cc` compare against reference vectors and exercise save/load and timing. Additional tests should cover device-fallback seeding and invalid state files.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/mtwist.c -->
