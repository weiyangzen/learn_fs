# Research: subset-b-007775

Grouped research for the exact source files assigned to `subset-b-007775`. Each section preserves the source path in its title and is wrapped for reconciliation into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/c-tap-harness/tests/runtests.c -->
## sources/distributed-fs/openafs/src/external/c-tap-harness/tests/runtests.c

Purpose: standalone C TAP Harness runner. It executes a list of test programs, parses a supported subset of TAP from child stdout, suppresses child stderr in normal batch mode, reports per-test-set status, and prints aggregate failure summaries and timing/resource statistics. It supports direct command-line tests, `-l` test-list files, `-o` single-test passthrough, source/build lookup directories, and verbose output via `-v` or `C_TAP_VERBOSE`.

Important APIs/types/functions: `struct testset` is the central mutable state for one test executable: name, argv vector, plan state, expected/current test counts, result table, counters, child exit status, all-skipped reason, and display state. `struct testlist` links testsets. `enum test_status`, `enum test_verbose`, and `enum plan_status` classify result cells, output behavior, and TAP plan lifecycle. Allocation wrappers (`xcalloc`, `xmalloc`, `x_reallocarray`, `xstrdup`, `xstrndup`) fail fast through `sysdie`. `test_start()` forks, pipes stdout, redirects stdin/stderr to `/dev/null`, and uses child-specific exit codes for setup failures. `test_checkline()` parses TAP lines, directives, duplicate numbers, bailouts, and lazy/final plans. `test_run()`, `test_analyze()`, `test_summarize()`, and `test_fail_summary()` drive execution and output. `parse_test_list_line()` understands `valgrind` and `libtool` options through `C_TAP_VALGRIND` and `C_TAP_LIBTOOL`.

Control flow: `main()` parses options, resolves `C_TAP_SOURCE`/`C_TAP_BUILD` and legacy `SOURCE`/`BUILD`, builds or reads a `testlist`, and calls `test_batch()` unless `-o` delegates directly with `execl()`. `test_batch()` computes a display width, runs each test via `test_run()`, collects aggregate counts, retains failed testsets for the failure table, frees all testsets, and returns success only when no failures or aborts occurred. In `test_run()`, output is consumed line-by-line until abort or EOF, each line is optionally echoed in verbose mode, then the remaining output is drained before `waitpid()` and result analysis.

State and persistence: all state is process-local and heap-backed; no persistent files are written. The runner mutates `struct testset` counters and result arrays as TAP lines arrive. Environment variables are installed with `putenv()` using allocated strings and cleared before exit for leak checking. Child process state is external: the child receives source/build environment and has stdin/stderr redirected. IV-like persistence is not relevant here, but display state (`ts->length`) is mutated to update a TTY progress counter.

Dependencies: POSIX process/file APIs (`fork`, `execv`, `pipe`, `dup2`, `waitpid`, `access`, `stat`, `gettimeofday`, `getrusage`, `putenv`, `getopt`) plus standard C string, stdio, errno, and time/resource headers. The source/build defaults can be compile-time macros `C_TAP_SOURCE` and `C_TAP_BUILD`.

Integration points: invoked by build systems as the test-suite driver. Test executables are located in current directory, build directory, then source directory, trying `-t`, `.t`, and no suffix. TAP producers should emit plan and `ok`/`not ok` lines on stdout; diagnostics should be comments. Valgrind integration is list-file driven and intentionally uses a whitespace-only parser, so quoted arguments are not supported.

Risks: TAP support is intentionally partial. Unknown stdout lines are ignored, long non-newline lines are ignored, and only exact `# skip`/`# todo` directives are special. Partial-block result accounting may classify missing tests only after summary. The test-list parser has no quoting and treats unknown options as fatal. `test_start()` silences stderr unless verbose single-test mode is used, so normal failure diagnostics require rerunning with `-o` or `-v`. The allocation overflow checks use `UINT_MAX` for portability rather than `SIZE_MAX`, intentionally limiting very large allocations.

Test signals: strong signals are runner output for multiple TAP scenarios: valid plan before/after tests, plan missing, duplicate numbers, invalid numbers, all-skip plan, `Bail out!`, child non-zero exits, child signal termination, todo/skip directives, valgrind/libtool command expansion, and source/build lookup. The code has built-in output summaries and child error codes that make black-box tests straightforward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/c-tap-harness/tests/runtests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/basic.c -->
## sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/basic.c

Purpose: implementation of the C TAP helper library used by individual tests. It prints TAP plans and assertions, supports lazy planning, skip and bailout behavior, diagnostics, temporary test-file helpers, fatal allocation wrappers, diagnostic log-file draining, and registered cleanup callbacks.

Important APIs/types/functions: exported `testnum` tracks the next TAP test number. Planning APIs are `plan()`, `plan_lazy()`, and `skip_all()`. Assertion APIs include `ok()`, `okv()`, `skip()`, `ok_block()`, `skip_block()`, `is_bool()`, `is_int()`, `is_string()`, `is_hex()`, and `is_blob()`. Error/diagnostic APIs are `bail()`, `sysbail()`, `diag()`, and `sysdiag()`. Memory wrappers are `bcalloc()`, `bmalloc()`, `brealloc()`, `breallocarray()`, `bstrdup()`, and `bstrndup()`. File helpers are `test_file_path()`, `test_tmpdir()`, and corresponding free functions. Cleanup APIs register either legacy two-argument or data-bearing cleanup callbacks.

Control flow: `plan()` or `plan_lazy()` initializes counters, records the primary PID, line-buffers stdout, and registers `finish()` with `atexit()`. Every assertion flushes stderr, drains complete lines from registered diag files, prints the TAP status line, increments `testnum`, and updates `_failed` when appropriate. `finish()` drains diagnostics, closes diagnostic files, calculates success from planned/running/failed counts, invokes cleanup functions in registration order, suppresses summaries in forked children, emits a lazy plan if needed, and prints final TAP diagnostics about count mismatches or failures.

State and persistence: state is static and process-local: `_planned`, `_failed`, `_process`, `_lazy`, `_aborted`, linked lists of cleanup functions, and linked lists of diagnostic files. Diagnostic-file readers persist `FILE *`, a dynamically resized line buffer, and a read position; incomplete lines are rewound until complete. `test_tmpdir()` creates a `tmp` directory under `C_TAP_BUILD` or current directory and `test_tmpdir_free()` attempts to remove it.

Dependencies: standard C/POSIX (`stdio`, `stdlib`, `string`, `errno`, `unistd`, `sys/stat` or Windows aliases), plus `tests/tap/basic.h`. It uses `atexit()`, `getpid()`, `setvbuf()`, `access()`, `mkdir()`, and `rmdir()`.

Integration points: consumed by C tests in the C TAP harness. The runner in `runtests.c` parses the output generated here. `test_file_path()` relies on `C_TAP_BUILD` and `C_TAP_SOURCE`, which the runner sets. Diagnostic file handling lets background helpers log into files while the TAP stream receives ordered `#` diagnostics.

Risks: global counters mean tests are not thread-safe. `atexit()` cleanup is fork-aware for summaries but cleanup functions are still called in non-primary processes with `primary` false, so callbacks must handle that. `bcalloc()` does not normalize zero sizes the same way as the runner's `x_calloc()`. `is_blob()` assumes non-NULL buffers when `len > 0`. Diagnostic-file handling intentionally waits for newline-terminated lines and may defer useful output until a newline appears.

Test signals: output tests should verify plan/lazy plan, failure summaries, diagnostic prefixes, skip lines, bailout exit 255, planned count mismatch diagnostics, cleanup order and primary flag, environment-based file lookup, temporary directory creation/removal, and memory-wrapper bailout behavior under injected allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/basic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/basic.h -->
## sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/basic.h

Purpose: public header for the C TAP basic helper library. It defines declarations, utility macros, compiler attributes, and callback types used by C tests and add-on TAP helpers.

Important APIs/types/functions: exposes `extern unsigned long testnum`, planning APIs (`plan`, `plan_lazy`, `skip_all`), reporting APIs (`ok`, `okv`, `skip`, `ok_block`, `skip_block`), comparison helpers (`is_bool`, `is_int`, `is_string`, `is_hex`, `is_blob`), bailout/diagnostic helpers, diagnostic-file add/remove functions, allocation wrappers, source/build file lookup, temporary directory helpers, and cleanup registration callbacks. Defines `ARRAY_SIZE`, `ARRAY_END`, `bcalloc_type`, and `breallocarray_type`.

Control flow: no executable control flow, but the API contract implies tests call `plan()` or `plan_lazy()` before assertions and may register cleanup functions that run from the implementation's `atexit()` handler.

State and persistence: declares the globally visible `testnum`; the rest of state lives in `basic.c`. Temporary directories and diagnostic files are represented through implementation-owned heap allocations returned to callers for explicit freeing.

Dependencies: includes `<stdarg.h>`, `<stddef.h>`, and `tests/tap/macros.h` for portability attributes and C++ linkage wrappers.

Integration points: this is the include surface for test code. Attribute annotations enable printf-format checking, malloc/alloc-size hints, nonnull checks, and noreturn diagnostics on supporting compilers while remaining portable through macro fallbacks.

Risks: exposes mutable `testnum`, so tests can manually alter numbering. The comment notes `test_cleanup_register()` is a backward-compatible API mistake and the data-bearing variant is preferred. Attribute portability depends on the fallbacks in `macros.h`.

Test signals: compile tests should verify the header works from C and C++, preserves format warnings on GCC/Clang, and that each declaration links against `basic.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/basic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/float.c -->
## sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/float.c

Purpose: optional TAP helper implementation for floating-point comparisons, separated from `basic.c` so projects only need math-library linkage when they use it.

Important APIs/types/functions: `is_double(double left, double right, double epsilon, const char *format, ...)` compares doubles and reports through `okv()`; static `is_equal_infinity()` detects matching signed infinities without relying on `isinf()` sign values.

Control flow: `is_double()` starts a `va_list`, flushes stderr, treats two NaNs as equal, treats equal-signed infinities as equal, otherwise checks `fabs(left - right) <= epsilon`. On failure it prints left/right diagnostics before delegating the failing TAP line to `okv()`.

State and persistence: no persistent or static mutable state. It mutates only the global TAP state inside `okv()` and diagnostic output in `basic.c`.

Dependencies: `<math.h>` for `isnan`, `isinf`, and `fabs`; `<stdarg.h>`/`stdio`; `tests/tap/basic.h` and `tests/tap/float.h`. Defines `_XOPEN_SOURCE 600` in strict/PEDANTIC builds for math macros. Clang warning pragmas suppress known conversion noise around floating macros.

Integration points: linked into tests that need floating comparisons. It relies on `basic.c` for numbering, diagnostics, and TAP output.

Risks: epsilon is caller-provided and no guard prevents a negative epsilon, which would only pass NaN/infinity cases or exact differences satisfying the negative comparison impossibly. Treating NaNs as equal is a test-helper policy choice, not IEEE equality. Requires math support that may need `-lm`.

Test signals: validate equal finite values, within/outside epsilon, positive vs negative infinity, two NaNs, one NaN, negative epsilon behavior, and formatted descriptions propagated through `okv()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/float.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/float.h -->
## sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/float.h

Purpose: public declaration for the floating-point TAP comparison helper.

Important APIs/types/functions: declares `is_double(double, double, double epsilon, const char *format, ...)` with printf-format attribute on the fourth argument. Uses `BEGIN_DECLS`/`END_DECLS` for C++ callers.

Control flow: none; the header communicates that callers pass an expected epsilon and optional TAP description.

State and persistence: no state declared.

Dependencies: includes `tests/tap/macros.h` for compiler attributes and C++ linkage wrappers. The implementation adds the math dependency.

Integration points: included by tests that link `float.c` alongside `basic.c`.

Risks: consumers must remember the extra object/library and possible math-library link flag. The header does not include `basic.h`, so it remains narrow but relies on the implementation for TAP integration.

Test signals: compile/link tests should cover C and C++ inclusion and format-attribute diagnostics where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/float.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/libtap.sh -->
## sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/libtap.sh

Purpose: portable Bourne-shell TAP helper library for shell tests. It mirrors the C helper surface with planning, assertions, block skip/status helpers, program-output checks, diagnostics, bailout, source/build file lookup, and temporary-directory creation.

Important APIs/functions: `plan`, `plan_lazy`, `finish`, `skip_all`, `ok`, `skip`, `ok_block`, `skip_block`, `puts`, `ok_program`, `strip_colon_error`, `bail`, `diag`, `test_file_path`, and `test_tmpdir`. It uses shell globals `count`, `planned`, and `failed`, and `tap_`-prefixed temporaries because Solaris `/bin/sh` lacks `local`.

Control flow: tests source the script, call `plan` or `plan_lazy`, then assertions. `plan*` installs `trap finish 0`. `finish()` calculates the highest test number, emits a lazy plan if needed, and prints TAP diagnostic summaries for count mismatches, failures, or all-success cases. `ok()` shifts off a description and runs the remaining command as the predicate.

State and persistence: state is shell-global in the current process. `test_tmpdir()` creates `$C_TAP_BUILD/tmp` or `./tmp` and returns the path, but this script does not provide a cleanup function. `ok_program()` captures combined stdout/stderr and compares both status and exact output.

Dependencies: POSIX-ish `/bin/sh`, `expr`, `cat`, `sed`, `mkdir`, and standard shell redirection. It intentionally avoids `local` and uses a here-doc in `puts()` for portability.

Integration points: shell tests produce TAP for `runtests.c`. `test_file_path()` integrates with runner-provided `C_TAP_BUILD` and `C_TAP_SOURCE`. `strip_colon_error()` normalizes platform-specific strerror suffixes for portable expected-output tests.

Risks: shell globals can be clobbered by tests. `ok_program()` exact-output comparisons are sensitive to whitespace and shell command substitution trimming. `puts()` comments warn against using it via backticks inside double quotes on Solaris due to escaping behavior. Lazy planning emits a plan even after zero tests unless caller controls flow.

Test signals: run shell tests under a strict `/bin/sh`, including lazy planning, skip-all, failing command predicates, exact output/status comparison, colon-error stripping, source/build lookup precedence, and tmpdir creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/libtap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/macros.h -->
## sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/macros.h

Purpose: portability macro header shared by TAP C headers. It abstracts compiler attributes, unused-parameter annotations, and C++ linkage wrappers.

Important APIs/macros: fallback definition for `__attribute__`, conditional fallback for `__alloc_size__`, fallback for `__warn_unused_result__`, Clang/LLVM diagnostic suppression for unknown attributes, `UNUSED`, `BEGIN_DECLS`, and `END_DECLS`.

Control flow: preprocessor-only logic selects fallbacks based on GCC/Clang/MS-style feature macros. No runtime behavior.

State and persistence: no runtime state.

Dependencies: compiler predefined macros such as `__GNUC__`, `__GNUC_MINOR__`, `__clang__`, `__llvm__`, and `__cplusplus`.

Integration points: included by `basic.h`, `float.h`, and likely other TAP add-ons so public headers can use GCC-style attributes without breaking older compilers or C++ consumers.

Risks: `#pragma GCC diagnostic ignored "-Wattributes"` affects the whole compilation context after inclusion on Clang/LLVM. The feature tests are intentionally broad and may not model every compiler claiming GCC compatibility. Redefining `__attribute__` is common in portable C but can interact poorly with other portability layers if include order differs.

Test signals: compile matrix across old GCC-like, Clang, strict C, and C++ modes; verify public headers remain parsable and format attributes still work when supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/aes.c -->
## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/aes.c

Purpose: OpenSSL-compatible AES wrapper over Heimdal's bundled Rijndael implementation. Provides key setup, single-block encrypt/decrypt, CBC mode, and CFB8 mode.

Important APIs/functions: `AES_set_encrypt_key()` and `AES_set_decrypt_key()` populate `AES_KEY.rounds` and `AES_KEY.key` via `rijndaelKeySetupEnc/Dec`, returning `-1` when the round count is zero. `AES_encrypt()` and `AES_decrypt()` call `rijndaelEncrypt/Decrypt`. `AES_cbc_encrypt()` implements encrypt/decrypt CBC with mutable IV. `AES_cfb8_encrypt()` implements byte-wise CFB8 using AES encryption for both directions.

Control flow: CBC encryption XORs each plaintext block with IV, encrypts, writes ciphertext, and updates IV to ciphertext. Partial final input is handled by XORing available bytes and filling the rest of the block from IV before encrypting a full block. CBC decryption saves the ciphertext block, decrypts, XORs with IV, and updates IV to the saved ciphertext; partial final input decrypts a full temporary block but emits only requested bytes. CFB8 loops one byte at a time, encrypts the IV, XORs the first keystream byte, and shifts either ciphertext input or output into IV depending on direction.

State and persistence: caller-owned `AES_KEY` persists expanded key material. CBC and CFB8 mutate caller-provided `iv` in place, so callers must preserve/reset IV externally for independent messages. No global state or files.

Dependencies: `config.h`, optional `krb5-types.h`, `<string.h>`, `rijndael-alg-fst.h`, and `aes.h`.

Integration points: used directly through the `hc_`-renamed AES symbols and indirectly by `evp-hcrypto.c` EVP cipher descriptors. Matches familiar OpenSSL function names through macros in `aes.h` while avoiding symbol collisions.

Risks: `AES_set_*_key()` does not validate null pointers. CBC partial-block behavior is non-standard for protocols requiring explicit padding; encryption emits a whole final block even when `size` is not a multiple of 16, while decryption emits only `size` bytes. The function signatures use `unsigned long size`, but CFB8 loop uses `int i`, which can overflow/truncate on very large sizes. In-place operation should be reviewed for each mode because some loops read/write advancing pointers.

Test signals: NIST AES known-answer vectors for 128/192/256 keys, CBC round trips with block-aligned and partial lengths, IV mutation checks, CFB8 vectors and encrypt/decrypt symmetry, invalid key-size path returning `-1`, and EVP integration through `EVP_hcrypto_aes_*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/aes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/aes.h -->
## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/aes.h

Purpose: public AES compatibility header for Heimdal hcrypto.

Important APIs/types/macros: symbol-renames OpenSSL-like names to `hc_` symbols. Defines `AES_BLOCK_SIZE`, `AES_MAXNR`, `AES_ENCRYPT`, `AES_DECRYPT`, and `AES_KEY` with `(AES_MAXNR + 1) * 4` 32-bit round-key words plus `rounds`. Declares key setup, block encrypt/decrypt, CBC, and CFB8 APIs.

Control flow: none in the header; mode behavior is implemented in `aes.c`.

State and persistence: `AES_KEY` is caller-allocated persistent key schedule state. IV mutation is implied by non-const IV pointers in mode APIs.

Dependencies: requires `uint32_t` to be available before or through surrounding hcrypto/Kerberos headers. Adds C++ `extern "C"` guards.

Integration points: included by hcrypto EVP provider and any code needing AES primitives without linking OpenSSL symbols.

Risks: macro `#define AES_set_decrypt_key hc_AES_decrypt_key` appears to rename to `hc_AES_decrypt_key`, while the naming pattern and implementation function are `AES_set_decrypt_key`; consumers must rely on build symbol-renaming consistency. Header does not include a fixed-width integer header itself. OpenSSL compatibility is partial and limited to listed APIs.

Test signals: compile/link tests for each renamed symbol, struct size assumptions, and C++ inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/aes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia-ntt.c -->
## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia-ntt.c

Purpose: bundled NTT Camellia block cipher core. It implements key schedule generation and single-block encryption/decryption for 128-, 192-, and 256-bit keys.

Important APIs/functions/macros: public APIs are `Camellia_Ekeygen()`, `Camellia_EncryptBlock()`, and `Camellia_DecryptBlock()`. Internal key schedule functions are `camellia_setup128()`, `camellia_setup192()`, and `camellia_setup256()`. Internal block functions are `camellia_encrypt128()`, `camellia_decrypt128()`, `camellia_encrypt256()`, and `camellia_decrypt256()`, with the 192-bit path using the 256-bit schedule after complement expansion. Macros implement endian load/store (`GETU32`, `PUTU32`), rotations, subkey indexing, F function, FL/FLINV layer, and round operations. Four 256-entry SP tables and six Sigma constants drive the Camellia transforms.

Control flow: `Camellia_Ekeygen()` dispatches by key length and fills a 272-byte/68-word key table. For 128-bit keys, the schedule derives KL and KA subkeys, performs rotations, absorbs whitening keys into subkeys, and applies inverse P-function transforms. For 192-bit keys, it builds a synthetic 256-bit key by appending bitwise complements of the final 64 bits, then calls the 256-bit schedule. For 256-bit keys, it derives KL, KR, KA, and KB dependent subkeys. Encrypt/decrypt APIs load four big-endian words from a 16-byte block, dispatch by key size, then write four big-endian words to output.

State and persistence: no global mutable state. Static SP tables are read-only. Caller-owned `KEY_TABLE_TYPE` persists generated subkeys. Stack temporaries hold sensitive key material during setup and are not explicitly zeroized before return.

Dependencies: `config.h`, `<string.h>`, `<stdlib.h>`, `<krb5-types.h>`, `camellia-ntt.h`, and `roken.h`. The MSVC path uses `_lrotl`/`_lrotr` and unaligned casts; the non-MSVC path performs byte loads/stores.

Integration points: wrapped by `camellia.c`, which exposes OpenSSL-like `CAMELLIA_*` APIs, and by `evp-hcrypto.c` through Camellia CBC EVP ciphers.

Risks: invalid key lengths fall through without error in `Camellia_Ekeygen()`, `Camellia_EncryptBlock()`, and `Camellia_DecryptBlock()`, potentially leaving stale key tables or copying unchanged temporary data. Key setup stack temporaries are not wiped. Table-driven S-box operations are data-dependent memory lookups and may not be constant-time on all platforms. The MSVC `GETU32` path casts input bytes to `u32 *`, which can have alignment/aliasing concerns outside MSVC assumptions.

Test signals: official Camellia known-answer vectors for 128/192/256-bit keys, round-trip block tests, invalid key length behavior tests, big-endian load/store checks on little/big endian platforms, and integration through `CAMELLIA_*` and EVP CBC wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia-ntt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia-ntt.h -->
## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia-ntt.h

Purpose: public header for the bundled NTT Camellia core.

Important APIs/types/macros: defines `CAMELLIA_BLOCK_SIZE`, `CAMELLIA_TABLE_BYTE_LEN`, `CAMELLIA_TABLE_WORD_LEN`, aliases `u32` to `uint32_t` and `u8` to `unsigned char`, defines `KEY_TABLE_TYPE` as a 68-word array, and declares `Camellia_Ekeygen`, `Camellia_EncryptBlock`, and `Camellia_DecryptBlock`.

Control flow: none; callers generate a key table then pass it to block encrypt/decrypt.

State and persistence: `KEY_TABLE_TYPE` is caller-owned persistent expanded key material.

Dependencies: requires `uint32_t` to be available from included context. Provides C++ linkage guards.

Integration points: included by `camellia-ntt.c` and `camellia.c`; acts as the low-level implementation contract below the hcrypto OpenSSL-like wrapper.

Risks: the header does not include a fixed-width integer header. API returns `void`, so invalid key lengths are not reported through the type system. Names can conflict with `camellia.h` because both define block/table macros with the same values.

Test signals: compile/link coverage for C and C++ callers, key table size assertions, and known-answer tests through the low-level API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia-ntt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia.c -->
## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia.c

Purpose: OpenSSL-like Camellia compatibility wrapper over the NTT core.

Important APIs/functions: `CAMELLIA_set_key()` stores the bit length and calls `Camellia_Ekeygen()`. `CAMELLIA_encrypt()` and `CAMELLIA_decrypt()` call block encrypt/decrypt using `key->bits` and `key->key`. `CAMELLIA_cbc_encrypt()` implements CBC encryption/decryption with mutable IV and partial final block handling similar to `aes.c`.

Control flow: set-key expands raw user key into the `CAMELLIA_KEY` key table and returns `1` unconditionally. CBC encryption XORs plaintext with IV, encrypts, stores ciphertext, and updates IV; partial final encryption fills remaining block bytes from IV. CBC decryption saves ciphertext, decrypts, XORs with IV, emits requested bytes, and updates IV to ciphertext.

State and persistence: caller-owned `CAMELLIA_KEY` persists the key length and expanded table. CBC mutates caller IV. No global mutable state.

Dependencies: `config.h`, optional `krb5-types.h`, `<string.h>`, `camellia-ntt.h`, `camellia.h`, and `roken.h`.

Integration points: used by `evp-hcrypto.c` for Camellia CBC ciphers and by callers expecting OpenSSL-like `CAMELLIA_*` functions renamed to `hc_`.

Risks: `CAMELLIA_set_key()` does not validate key size and always returns success, even though the NTT core ignores unsupported bit lengths. Partial-block CBC behavior is not padding-compatible with all protocols. No null-pointer guards. IV mutation means callers must manage IV reset for separate messages.

Test signals: known-answer block tests, CBC round trips for aligned and partial lengths, IV mutation checks, invalid bit-length behavior, and EVP Camellia descriptor tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia.h -->
## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia.h

Purpose: public OpenSSL-like Camellia hcrypto header.

Important APIs/types/macros: symbol-renames `CAMELLIA_*` names to `hc_` symbols, defines block/table sizes and `CAMELLIA_ENCRYPT`/`CAMELLIA_DECRYPT`, declares `CAMELLIA_KEY` with `bits` and a 68-word table, and declares key setup, block encrypt/decrypt, and CBC mode functions.

Control flow: none in the header.

State and persistence: `CAMELLIA_KEY` is persistent caller-owned key schedule state. CBC IV mutation is exposed by non-const IV pointer.

Dependencies: requires `uint32_t` to be defined by the including context. Unlike some neighboring headers, it does not wrap declarations in C++ guards.

Integration points: included by Camellia wrapper implementation and hcrypto EVP provider. It intentionally mirrors OpenSSL naming while renaming symbols to avoid external collisions.

Risks: no explicit include for fixed-width types and no C++ guards may affect standalone consumers. OpenSSL compatibility is partial. Macro names overlap with `camellia-ntt.h`.

Test signals: compile/link tests for renamed symbols and struct sizing, plus C++ inclusion if this header is expected to be usable there.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/des-tables.h -->
## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/des-tables.h

Purpose: generated lookup tables for DES key schedule setup and parity adjustment.

Important APIs/types/data: static arrays `pc1_c_3`, `pc1_c_4`, `pc1_d_3`, `pc1_d_4`, `pc2_c_1` through `pc2_c_4`, `pc2_d_1` through `pc2_d_4`, and `odd_parity[256]`. The PC1/PC2 arrays encode DES key permutation/compression bit patterns used by `DES_set_key_unchecked()`. `odd_parity` maps each byte to an odd-parity-adjusted byte.

Control flow: no functions; `des.c` includes this header directly and indexes the arrays while constructing subkeys and checking/setting key parity.

State and persistence: all arrays are `static` at include site. They are mutable by type except `odd_parity` is also static non-const, but intended as read-only generated data. No persistence outside the process.

Dependencies: none directly, but it assumes inclusion in a C source context where `static int` and `static unsigned char` definitions are valid.

Integration points: tightly coupled to `des.c`; not a standalone public header. The top comment says it is generated from `gen-des.pl` and should not be edited manually.

Risks: because arrays are not `const`, accidental writes in the including translation unit could corrupt DES behavior. Generated-table correctness is critical and opaque to casual review. Including this header in more than one source creates separate static copies.

Test signals: DES key schedule known-answer vectors, parity mapping tests for all 256 byte values, and regeneration comparison against the generator if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/des-tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/des.c -->
## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/des.c

Purpose: Heimdal hcrypto DES implementation with OpenSSL/libdes-compatible APIs. It covers key parity and weak-key checks, DES key schedule generation, single DES, 3DES EDE, CBC/PCBC/CFB64 modes, CBC checksum, legacy string-to-key/password helpers, and an internal IP/FP sanity test.

Important APIs/functions: key APIs include `DES_set_odd_parity`, `DES_check_key_parity`, `DES_is_weak_key`, `DES_set_key`, `DES_set_key_unchecked`, `DES_set_key_checked`, and `DES_key_sched`. Block/mode APIs include `DES_encrypt`, `DES_ecb_encrypt`, `DES_ecb3_encrypt`, `DES_cbc_encrypt`, `DES_pcbc_encrypt`, `DES_ede3_cbc_encrypt`, `DES_cfb64_encrypt`, and `DES_cbc_cksum`. Legacy password/key helpers are `DES_string_to_key` and `DES_read_password`. Internal helpers include `load`, `store`, `IP`, `FP`, `_des3_encrypt`, `desx`, and `bitswap8`.

Control flow: key setup loads the 8-byte key into two 32-bit words, uses generated PC1 tables to split C/D halves, rotates by DES schedule, uses PC2 tables to form 16 pairs of subkey words, and stores them in S-box-friendly order. `DES_encrypt()` applies initial permutation, `desx()` for 16 rounds, and final permutation. CBC/PCBC/3DES modes loop over full blocks and zero-pad partial final blocks; 3DES performs EDE order for encryption and reverse order for decryption. CFB64 maintains byte offset `*num`, encrypts IV as keystream, and updates IV differently for encrypt/decrypt. `DES_string_to_key()` folds password bytes into a key, fixes parity, avoids weak keys, computes a CBC checksum, and fixes parity again.

State and persistence: caller-owned `DES_key_schedule` stores 32 round-key words. IVs for 3DES CBC and CFB64 are persisted back to caller; single DES CBC and PCBC clear local `uiv` but notably do not store final IV back in `DES_cbc_encrypt()`/`DES_pcbc_encrypt()`, whereas `DES_ede3_cbc_encrypt()` does. `DES_cfb64_encrypt()` persists both `iv` and `num`. Weak-key table and S/P boxes are static read-only-by-convention data.

Dependencies: `<config.h>`, `krb5-types.h`, `roken.h` for `ct_memcmp`, `ui.h` for `UI_UTIL_read_pw_string`, and generated `des-tables.h`. Uses standard C library, `assert`, and abort for `_DES_ipfp_test()`.

Integration points: public declarations live in `des.h`; EVP hcrypto provider wraps DES-CBC and DES-EDE3-CBC. Kerberos legacy code may use PCBC, CBC checksum, and string-to-key. Symbol names are renamed through `des.h` to `hc_` names.

Risks: DES and RC4-era APIs are cryptographically legacy; comments warn DES is withdrawn and PCBC/checksum/string-to-key should remain legacy. Table-driven DES and weak-key comparison are not uniformly constant-time except `DES_is_weak_key()` uses `ct_memcmp`. `DES_set_key_unchecked()` skips parity/weak-key validation. Partial-block modes zero-pad silently, which may not match protocol padding. The IV persistence difference between single DES CBC and 3DES CBC is a compatibility subtlety and potential caller surprise. Stack key material is only partially zeroized in some functions.

Test signals: FIPS DES and 3DES known-answer vectors, parity/weak-key checks, key schedule validation, CBC/PCBC/CFB64 round trips including partial blocks and `num` continuation, CBC checksum vectors, string-to-key compatibility vectors, `_DES_ipfp_test()`, and EVP DES integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/des.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/des.h -->
## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/des.h

Purpose: public DES compatibility header for hcrypto.

Important APIs/types/macros: symbol-renames DES APIs to `hc_` names, defines `DES_CBLOCK_LEN`, `DES_KEY_SZ`, `DES_ENCRYPT`, and `DES_DECRYPT`, declares `DES_cblock` and `DES_key_schedule`, and exposes parity/key-schedule, random/deprecated, block/mode, checksum, password, string-to-key, and `_DES_ipfp_test()` functions. Defines `HC_DEPRECATED` for GCC/MSVC or empty fallback.

Control flow: none in the header.

State and persistence: caller-owned `DES_key_schedule`, `DES_cblock`, IVs, and CFB offset pointers are part of the API contract. Deprecated random APIs imply external RNG state in implementations elsewhere or compatibility stubs.

Dependencies: requires `uint32_t` from including context and provides C++ linkage guards.

Integration points: included by `des.c`, hcrypto EVP provider, and legacy Kerberos/OpenSSL-compatible callers. Symbol renaming prevents collisions with system/OpenSSL DES.

Risks: exposes many deprecated or weak cryptographic interfaces. Some declared random/password functions are deprecated or may be implemented outside this file. Header does not include fixed-width integer definitions itself.

Test signals: compile/link all exported symbols expected in a full hcrypto build, deprecation attribute behavior, and C++ inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/des.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-cc.c -->
## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-cc.c

Purpose: Apple CommonCrypto-backed EVP provider for hcrypto. The entire implementation is compiled only under `__APPLE__` and returns EVP cipher/digest descriptors backed by CommonCrypto when the relevant CommonCrypto headers/features are available.

Important APIs/functions: exported provider functions include `EVP_cc_des_ede3_cbc`, `EVP_cc_des_cbc`, AES CBC/CFB8 variants, RC2 CBC variants, RC4/RC4-40, MD2/MD4/MD5/SHA1/SHA256 digests, and Camellia stubs. Internal `struct cc_key` owns a `CCCryptorRef`; `init_cc_key()` creates, resets, or releases/recreates cryptors; `cc_do_cipher()` calls `CCCryptorUpdate`; `cc_do_cfb8_cipher()` manually implements CFB8 on top of AES ECB; `cc_cleanup()` releases the cryptor.

Control flow: descriptor-returning functions return pointers to static `EVP_CIPHER` or `hc_evp_md` structs when compile-time support exists, else `NULL`. CBC/stream initialization calls `init_cc_key()` with selected `CCAlgorithm`, options, key length, and IV. CFB8 initialization copies the IV into the EVP context and creates an AES ECB encryptor regardless of encrypt/decrypt direction; per-byte processing encrypts the IV, XORs one byte, then shifts ciphertext into IV.

State and persistence: each EVP context stores provider state in `ctx->cipher_data` as `struct cc_key`. The cryptor reference persists until cleanup or reinitialization. IV is persisted in `ctx->iv`, especially for manual CFB8. Digest descriptors use CommonCrypto digest context sizes but no provider global mutable state.

Dependencies: Apple-only `CommonCrypto/CommonDigest.h` and `CommonCrypto/CommonCryptor.h`, `evp.h`, and `evp-cc.h`. RC2 support is additionally guarded by `COMMONCRYPTO_SUPPORTS_RC2`.

Integration points: selected by hcrypto's EVP layer on Apple platforms as a provider alternative to built-in implementations. `evp-cc.h` declares this provider surface. Camellia functions intentionally return `NULL` because CommonCrypto does not provide Camellia here.

Risks: non-Apple builds compile no code from this file, so callers must tolerate missing provider functions depending on build configuration. Many functions can return `NULL` at runtime based on feature macros. `cc_do_cipher()` copies input to output before `CCCryptorUpdate()` but then passes original input, making the pre-copy unnecessary and potentially misleading. CFB8 descriptor for AES-256 reports block size as `kCCBlockSizeAES128` rather than `1`, unlike AES-128 CFB8; this may affect EVP buffering semantics. No padding options are set, so CommonCrypto behavior must match hcrypto EVP expectations.

Test signals: Apple build tests for non-NULL providers, CommonCrypto CBC/CFB8 vectors, cryptor reset with new IV and null key, cleanup/reinit leak checks, fallback `NULL` behavior with feature macros disabled, digest known-answer vectors, and Camellia provider null expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-cc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-cc.h -->
## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-cc.h

Purpose: public declarations for Apple CommonCrypto-backed EVP provider functions.

Important APIs/macros: symbol-renames all `EVP_cc_*` names to `hc_EVP_cc_*`. Declares digest providers for MD2, MD4, MD5, SHA1, and SHA256; cipher providers for RC2 variants, RC4 variants, DES-CBC, 3DES-CBC, AES CBC/CFB8 variants, and Camellia CBC variants.

Control flow: none in the header; implementation may return static descriptors or `NULL` depending on platform and feature support.

State and persistence: no state declared. Provider state is allocated by the EVP core according to descriptor `ctx_size` in `evp-cc.c`.

Dependencies: assumes `EVP_MD`, `EVP_CIPHER`, and `HC_CPP_BEGIN/HC_CPP_END` are already defined by included EVP headers. Does not include them itself.

Integration points: included by `evp-cc.c` and provider-selection code that wants CommonCrypto descriptors.

Risks: declarations exist even though implementation is Apple-gated; linking or provider selection must match build conditions. Camellia declarations are present but currently implemented as `NULL` providers. Header depends on include order for EVP types/macros.

Test signals: compile tests with proper EVP include order, symbol-renaming checks, and Apple/non-Apple link configuration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-cc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-hcrypto.c -->
## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-hcrypto.c

Purpose: built-in hcrypto EVP provider. It exposes static `EVP_CIPHER` and `EVP_MD` descriptors backed by Heimdal's AES, DES/3DES, RC2, RC4, Camellia, SHA, MD2, MD4, and MD5 implementations.

Important APIs/functions: AES helpers `aes_init()` and `aes_do_cipher()` support AES CBC and CFB8 descriptors for 128/192/256-bit keys. Digest provider functions return `hc_evp_md` descriptors for SHA256, SHA384, SHA512, SHA1, MD5, MD4, and MD2. DES helpers wrap DES-CBC and 3DES-CBC. RC2 helpers use variable effective key length based on EVP context key length. Camellia helpers wrap CBC descriptors for 128/192/256-bit keys. RC4 helpers expose stream-cipher descriptors for default and 40-bit keys.

Control flow: each exported `EVP_hcrypto_*` returns the address of a static descriptor. During EVP initialization, descriptor `init` callbacks expand keys into context-owned cipher data. During updates, descriptor `do_cipher` callbacks call the primitive mode function using `ctx->iv` and `ctx->encrypt`. Digest descriptors provide init/update/final function pointers and context sizes directly from hash implementations.

State and persistence: no provider global mutable state. EVP context-owned `cipher_data` persists expanded key schedules (`AES_KEY`, `DES_key_schedule`, `struct des_ede3_cbc`, `struct rc2_cbc`, `CAMELLIA_KEY`, `RC4_KEY`). `ctx->iv` is mutated by block modes and CFB8. RC4 key stream state mutates inside `RC4_KEY`.

Dependencies: `evp.h`, `evp-hcrypto.h`, `krb5-types.h`, `des.h`, `camellia.h`, `aes.h`, `rc2.h`, `rc4.h`, `sha.h`, `md2.h`, `md4.h`, and `md5.h`.

Integration points: core provider for hcrypto EVP when platform-specific providers are unavailable or not selected. Depends on primitive wrappers in this subset (`aes.c`, `camellia.c`, `des.c`) and other hcrypto primitives outside this subset.

Risks: initialization callbacks ignore return codes from primitive key setup, so invalid key lengths or setup failures are not propagated. DES-CBC uses `DES_set_key_unchecked()` and does not set parity/weak-key checks; 3DES sets odd parity but also uses unchecked schedules. Legacy algorithms MD2/MD4/MD5/DES/RC2/RC4 are exposed for compatibility and should be policy-gated by callers. The AES CFB8 descriptor block-size choices differ from CommonCrypto's AES-256 CFB8 descriptor, so provider parity should be tested. No cleanup callbacks zeroize context key schedules when EVP frees cipher data.

Test signals: EVP known-answer vectors for every descriptor, encrypt/decrypt round trips with IV mutation checks, variable-length RC2/RC4 key tests, invalid key length behavior, provider equivalence tests against CommonCrypto where available, digest known-answer vectors, and memory cleanup/zeroization review for sensitive contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-hcrypto.c -->
