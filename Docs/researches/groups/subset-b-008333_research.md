# subset-b-008333 Research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/tools.go -->
# sources/security-integrity/fscrypt/tools.go

Purpose: This Go file is build-tagged as `tools`, so it is never compiled into fscrypt binaries. It records development tool dependencies as blank imports so Go module resolution keeps versions for `misspell`, `gocovmerge`, `goimports`, `protoc-gen-go`, and `staticcheck`.

Important APIs and functions: There are no runtime APIs. The only package-level behavior is dependency anchoring through blank imports.

Control flow and state: No control flow executes at runtime and no state is persisted by this file. Its effects are limited to module graph and developer tooling reproducibility.

Dependencies and integration points: It integrates with Go module tooling, CI linting, code generation, and coverage workflows.

Risks and test signals: The main risk is stale tool dependencies causing developer/CI drift. Test signal is indirect: `go mod tidy` should retain these tool modules when the tools build tag is considered.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/tools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/util/errors.go -->
# sources/security-integrity/fscrypt/util/errors.go

Purpose: This utility file centralizes small error-handling helpers for fscrypt, including sticky readers/writers, length validation, system error classification, logic-error panic checks, and integration-test filesystem root discovery.

Important APIs and functions: `ErrReader` wraps `io.Reader` and uses `io.ReadFull` until the first error, then returns the same stored error on later reads. `ErrWriter` mirrors that behavior for writes. `CheckValidLength`, `SystemError`, `NeverError`, `TestRoot`, and `ErrSkipIntegration` are small cross-package helpers.

Control flow and state: `ErrReader` and `ErrWriter` persist only the first error. `TestRoot` reads `TEST_FILESYSTEM_ROOT` and returns `ErrSkipIntegration` if it is unset.

Dependencies and integration points: Used by binary parsing/serialization paths and integration tests; depends on standard `io`, `log`, `os`, and `github.com/pkg/errors`.

Risks and test signals: Sticky read/write helpers simplify call sites but can hide partial-write semantics if callers ignore returned byte counts. Tests should cover first-error retention, short reads via `ReadFull`, valid/invalid lengths, and unset integration-test environment behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/util/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/util/util.go -->
# sources/security-integrity/fscrypt/util/util.go

Purpose: This file provides low-level fscrypt helpers for unsafe pointer conversion, integer slice lookup, user/group resolution, numeric parsing, mount table scanning, path checks, and filesystem-related utilities.

Important APIs and functions: `Ptr`, `ByteSlice`, and `PointerSlice` bridge Go slices and raw pointers for syscall/cgo-style code. `Index`/`Lookup` provide simple table lookup. The user/group helpers parse ids or names and normalize current user information. Other helpers cover line scanning, device/mount metadata, and system calls through `golang.org/x/sys/unix`.

Control flow and state: Most helpers are stateless wrappers that validate input and return derived data or errors. Unsafe slice views intentionally do not own memory and depend on caller lifetime guarantees.

Dependencies and integration points: Integrated across fscrypt packages that invoke kernel ioctls, inspect mountpoints, and resolve users. Depends on `bufio`, `os/user`, `strconv`, `unsafe`, and `unix`.

Risks and test signals: Unsafe pointer helpers are high-risk if callers index beyond valid backing memory. User and mount helpers can vary across OS/user database environments. Tests should target empty-slice pointer behavior, lookup misses, numeric parse errors, and system-call error wrapping.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/util/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/util/util_test.go -->
# sources/security-integrity/fscrypt/util/util_test.go

Purpose: This test file validates the fscrypt `util` package helpers, especially unsafe conversions, lookup utilities, and environment-dependent integration-test behavior.

Important APIs and functions: Tests exercise `Ptr`, `ByteSlice`, `PointerSlice`, `Index`, `Lookup`, `CheckValidLength`, sticky error helpers, and `TestRoot`-style integration gating where applicable.

Control flow and state: Tests construct local slices, pointers, arrays, readers, writers, and environment states, then assert returned values or errors. Any environment mutation must be restored to avoid leaking state to other tests.

Dependencies and integration points: It provides fast unit coverage for helpers used by lower-level ioctl and serialization code. It also documents expected semantics for nil/empty pointer conversion and missing integration roots.

Risks and test signals: The unsafe helpers can pass tests while still being dangerous for caller misuse, so these tests mostly protect helper contract, not all consumers. Strong signals include nil pointer for empty slices, correct lookup index/miss behavior, sticky first-error behavior, and expected integration skip error.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/util/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/.github/workflows/ci.yml -->
# sources/security-integrity/fsverity-utils/.github/workflows/ci.yml

Purpose: This GitHub Actions workflow builds and tests fsverity-utils across compiler, crypto-library, architecture, and packaging combinations.

Important APIs and jobs: The workflow defines CI jobs for Linux builds, test execution, sparse/static analysis, cross or alternate compiler coverage, dependency setup, and artifact/package checks. It drives `make`, project test scripts, and package manager installs.

Control flow and state: Jobs are event-triggered and mostly stateless, with state limited to the checked-out tree, installed packages, build outputs, and workflow caches if configured. Matrix expansion is the main control-flow mechanism.

Dependencies and integration points: Integrates with the Makefile, `scripts/run-tests.sh`, `scripts/run-sparse.sh`, OpenSSL/BoringSSL or libcrypto variants, Linux headers, and GitHub Actions runners.

Risks and test signals: CI risk centers on host package availability, kernel/fs-verity feature availability, and matrix drift. Signals include successful compile, library tests, CLI tests, sparse checks, and build modes that omit optional OpenSSL features.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/Makefile -->
# sources/security-integrity/fsverity-utils/Makefile

Purpose: The Makefile is the main build, install, test, clean, and release orchestration for fsverity-utils. It builds the `fsverity` CLI, `libfsverity`, tests, headers, pkg-config metadata, and optional documentation.

Important APIs and targets: Key targets include default build, `install`, `uninstall`, `check`/tests, `clean`, static/shared library outputs, program objects, and generated `libfsverity.pc`. Variables configure `CC`, `CFLAGS`, `LDFLAGS`, prefix/libdir/include paths, OpenSSL/libcrypto support, and versioning.

Control flow and state: It compiles C sources into object files, links programs and libraries, stages installation paths, and writes generated pkg-config data. Build state is object files, libraries, binaries, and generated metadata.

Dependencies and integration points: Integrates with `common/`, `lib/`, `programs/`, `scripts/run-tests.sh`, pkg-config, Linux headers, and OpenSSL-compatible crypto libraries.

Risks and test signals: Build flags must stay ABI-compatible for `libfsverity`. Risks include platform-specific linker flags, library soname/version errors, and optional crypto backend differences. Signals are clean rebuilds, installed header/library layout, pkg-config correctness, and test target success.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/common/common_defs.h -->
# sources/security-integrity/fsverity-utils/common/common_defs.h

Purpose: This shared header defines common types, macros, endian helpers, array/rounding utilities, compile annotations, and compatibility glue used by both the fsverity library and CLI.

Important APIs and types: It provides fixed-width aliases such as `u8`, `u16`, `u32`, `u64`, helpers like `ARRAY_SIZE`, `DIV_ROUND_UP`, `roundup`, `min`, `max`, `is_power_of_2`, `ilog2`, endian conversion wrappers, and assertion/warning-style macros.

Control flow and state: The file contains macro-time logic only. It persists no state, but influences generated code, layout validation, and portability behavior.

Dependencies and integration points: Included by `lib_private.h`, `fsverity.h`, command implementations, and UAPI wrappers. It bridges Linux conventions into userspace project code.

Risks and test signals: Macro errors can silently affect hash tree layout, descriptor encoding, and ioctl structure interpretation. Test signals include digest vector stability, compile success under multiple platforms, and static-analysis coverage for integer conversions.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/common/common_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/common/fsverity_uapi.h -->
# sources/security-integrity/fsverity-utils/common/fsverity_uapi.h

Purpose: This header vendors the userspace ABI definitions for Linux fs-verity ioctls, metadata types, hash algorithms, descriptor structures, and enable/read/measure argument layouts.

Important APIs and types: It defines `FS_IOC_ENABLE_VERITY`, `FS_IOC_MEASURE_VERITY`, `FS_IOC_READ_VERITY_METADATA`, `struct fsverity_enable_arg`, `struct fsverity_digest`, `struct fsverity_descriptor`, `struct fsverity_read_metadata_arg`, and metadata/hash constants.

Control flow and state: There is no executable flow. The persistent contract is binary structure layout shared with the kernel, so field sizes, reserved fields, and little-endian encodings are compatibility-critical.

Dependencies and integration points: Used by CLI commands, `lib/enable.c`, digest computation, metadata dump, and tests. It must track kernel UAPI without breaking older build hosts.

Risks and test signals: ABI drift is the primary risk. Misaligned structures or wrong ioctl numbers break kernel interactions. Signals include compile-time structure availability, ioctl success/failure behavior in integration tests, and digest/descriptor vector agreement with kernel expectations.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/common/fsverity_uapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/common/win32_defs.h -->
# sources/security-integrity/fsverity-utils/common/win32_defs.h

Purpose: This compatibility header supplies Windows or non-POSIX definitions needed to compile shared code paths where Linux/GNU symbols are unavailable.

Important APIs and macros: It defines fallback `O_BINARY`, `ENOPKG`, cold/printf attributes, fixed-format integer macros, and minimal compatibility types or annotations under `_WIN32`.

Control flow and state: All behavior is preprocessor controlled. No runtime state is stored.

Dependencies and integration points: Included by common project headers to keep library portions buildable in non-Linux userspace contexts, especially tooling that computes or signs digests without kernel ioctls.

Risks and test signals: Risk lies in masking platform limitations: digest/signing can be portable, but enable/measure ioctls remain Linux-specific. Compile-only CI on Windows-like toolchains and absence of attribute-related warnings are the main signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/common/win32_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/include/libfsverity.h -->
# sources/security-integrity/fsverity-utils/include/libfsverity.h

Purpose: This is the public C API for `libfsverity`, exposing digest computation, PKCS#7 signing, fs-verity enablement, and hash algorithm lookup to external callers.

Important APIs and types: It defines version macros, hash constants, `struct libfsverity_merkle_tree_params`, `struct libfsverity_digest`, `struct libfsverity_signature_params`, metadata callbacks, `libfsverity_read_fn_t`, `libfsverity_compute_digest`, `libfsverity_sign_digest`, `libfsverity_enable`, `libfsverity_enable_with_sig`, `libfsverity_find_hash_alg_by_name`, and digest-size lookup.

Control flow and state: Callers provide zero-initialized parameter structs. The library allocates returned digest/signature buffers, and callers free them. Reserved fields are part of forward-compatibility validation.

Dependencies and integration points: Used by CLI commands, tests, downstream applications, pkg-config consumers, and kernel-compatible metadata tooling.

Risks and test signals: ABI stability is critical. Reserved fields, version checks, ownership rules, and nullable callback semantics must remain stable. Signals include public header compile tests, digest vector tests, signing tests, and pkg-config installation checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/include/libfsverity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/lib/compute_digest.c -->
# sources/security-integrity/fsverity-utils/lib/compute_digest.c

Purpose: This file implements `libfsverity_compute_digest()`, including Merkle tree construction, fs-verity descriptor generation, metadata callback reporting, and final file digest hashing.

Important APIs and functions: Internal helpers include `hash_one_block`, `block_is_full`, `report_merkle_tree_size`, `report_merkle_tree_block`, `report_descriptor`, and `compute_root_hash`. The exported function validates `libfsverity_merkle_tree_params`, selects the hash algorithm, constructs `struct fsverity_descriptor`, computes the root hash, and returns `struct libfsverity_digest`.

Control flow and state: Data is read incrementally through caller-supplied `read_fn`. Pending data/tree blocks are buffered per level, salted and zero-padded before hashing, and optional callbacks receive tree size, tree blocks, and descriptor. Empty files get an all-zero root hash.

Dependencies and integration points: Depends on `lib_private.h`, hash algorithm backends, UAPI descriptor layout, and public callbacks. The CLI `digest`, `sign`, `enable`, and tests rely on this exact digest format.

Risks and test signals: Risks include off-by-one tree levels, block-size validation, salt padding, callback ordering, and descriptor endian encoding. Strong signals are known-answer digest tests, metadata callback tests, empty-file vectors, and error propagation from read/callback failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/lib/compute_digest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/lib/enable.c -->
# sources/security-integrity/fsverity-utils/lib/enable.c

Purpose: This library file wraps the Linux `FS_IOC_ENABLE_VERITY` ioctl for enabling fs-verity on an open file, optionally with a built-in signature.

Important APIs and functions: `libfsverity_enable()` delegates to `libfsverity_enable_with_sig()` with no signature. `libfsverity_enable_with_sig()` validates params, applies default hash algorithm and block size, fills `struct fsverity_enable_arg`, attaches optional signature pointer/size, and invokes `ioctl`.

Control flow and state: The function does not persist user-space state. Kernel state changes when the ioctl succeeds: the target file becomes fs-verity protected and immutable for content changes.

Dependencies and integration points: Integrates public parameters with `fsverity_uapi.h`, kernel fs-verity support, and CLI `enable`.

Risks and test signals: Argument validation must match kernel expectations without rejecting valid future callers. Risks include pointer-size casting, invalid block sizes, unsupported kernels, and signature size overflow. Signals are ioctl integration tests, expected negative errno returns, and CLI enable behavior on supported filesystems.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/lib/enable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/lib/hash_algs.c -->
# sources/security-integrity/fsverity-utils/lib/hash_algs.c

Purpose: This file defines supported fs-verity hash algorithms and OpenSSL-backed hash context operations.

Important APIs and functions: It maintains algorithm descriptors for SHA-256 and SHA-512, provides context creation, init/update/final/full-hash helpers, frees hash contexts, and exports lookup helpers by algorithm number or name plus digest-size queries.

Control flow and state: Hash contexts hold per-operation crypto state and refer to immutable algorithm descriptors. Lookup scans the supported algorithm table and returns zero/null for unknown algorithms.

Dependencies and integration points: Used by digest computation, signing validation, CLI hash-alg parsing, and tests. Depends on OpenSSL-compatible EVP APIs and common type definitions.

Risks and test signals: Risks include OpenSSL API compatibility, digest-size mismatch with UAPI constants, and accepting aliases inconsistently. Signals include test vectors, hash lookup tests, SHA-256/SHA-512 digest size assertions, and builds against supported crypto libraries.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/lib/hash_algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/lib/lib_private.h -->
# sources/security-integrity/fsverity-utils/lib/lib_private.h

Purpose: This private library header shares internal declarations, exported-symbol annotations, allocation helpers, hash algorithm structures, error reporting, and utility prototypes across `libfsverity` implementation files.

Important APIs and types: It defines `struct fsverity_hash_alg`, `struct hash_ctx`, `LIBEXPORT`, allocation wrappers such as `libfsverity_zalloc`, error-message helpers, memory-zero checks, hash helpers, and internal algorithm lookup by number.

Control flow and state: No runtime control flow exists in the header, but its declarations define how implementation files exchange state and callbacks.

Dependencies and integration points: Included by digest, signing, enabling, hash, and utils implementations. It is intentionally not public ABI, unlike `include/libfsverity.h`.

Risks and test signals: Internal API drift can break implementation consistency without downstream ABI changes. Visibility macros are sensitive for shared-library exports. Signals include clean shared/static library builds and symbol export checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/lib/lib_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/lib/libfsverity.pc.in -->
# sources/security-integrity/fsverity-utils/lib/libfsverity.pc.in

Purpose: This pkg-config template describes installed `libfsverity` compiler and linker flags for downstream consumers.

Important APIs and fields: It contains template variables for prefix, exec prefix, libdir, includedir, package name, description, version, `Libs`, and `Cflags`.

Control flow and state: The Makefile substitutes variables during build/install. The generated `.pc` file persists installation metadata.

Dependencies and integration points: Used by package managers, application builds, and CI installation checks. It must align with installed header and library paths.

Risks and test signals: Incorrect paths or missing linker flags make downstream builds fail. Signals include `pkg-config --cflags --libs libfsverity` after install and compiling a small consumer against the installed package.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/lib/libfsverity.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/lib/sign_digest.c -->
# sources/security-integrity/fsverity-utils/lib/sign_digest.c

Purpose: This file implements `libfsverity_sign_digest()`, producing Linux fs-verity-compatible PKCS#7 DER signatures over computed file digests.

Important APIs and functions: It validates `libfsverity_digest` and `libfsverity_signature_params`, loads certificates and private keys from PEM files or optional PKCS#11 engine/module/key id settings, constructs the signed data, serializes PKCS#7 DER, and reports OpenSSL errors. It contains engine setup and cleanup paths when OpenSSL engines are available.

Control flow and state: The function allocates output signature memory for the caller, opens crypto/key resources, performs signing, and frees OpenSSL objects on exit. PKCS#11 state is transient but external token configuration influences behavior.

Dependencies and integration points: Depends on OpenSSL/BoringSSL-compatible APIs, public digest structs, CLI `sign`, CLI `enable --signature`, and tests with known certificates/keys.

Risks and test signals: Risks include invalid cert/key handling, PKCS#11 backend availability, OpenSSL API version differences, DER allocation ownership, and leaking sensitive key material. Signals include successful signing tests, invalid key/cert negative tests, and kernel/userspace signature verification compatibility.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/lib/sign_digest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/lib/utils.c -->
# sources/security-integrity/fsverity-utils/lib/utils.c

Purpose: This file implements small internal utility functions used by `libfsverity`, chiefly allocation, zeroing, error reporting, and memory inspection helpers.

Important APIs and functions: It provides `libfsverity_zalloc`, error print helpers, OpenSSL-independent memory-zero checks such as `libfsverity_mem_is_zeroed`, and other private support routines declared in `lib_private.h`.

Control flow and state: Functions are stateless except for emitting diagnostics to stderr/logging targets. Allocation returns zero-initialized memory to callers, which own and free it.

Dependencies and integration points: Used by digest, signing, and enable code. It underpins reserved-field validation and output buffer allocation for public APIs.

Risks and test signals: Allocation overflow or nonzero reserved-field checks can cause security or compatibility defects. Signals include parameter validation tests, memory sanitizer runs, and expected diagnostic paths for invalid inputs.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/lib/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/cmd_digest.c -->
# sources/security-integrity/fsverity-utils/programs/cmd_digest.c

Purpose: This CLI command computes and prints the fs-verity digest of a file, optionally using custom hash algorithm, block size, salt, compact output, and metadata side outputs.

Important APIs and functions: `fsverity_cmd_digest()` parses long options, opens the input file, fills `libfsverity_merkle_tree_params`, calls `libfsverity_compute_digest`, and prints hex digest information. It uses shared CLI parsing helpers for tree parameters and file I/O.

Control flow and state: Command state is option flags, opened file descriptor, allocated digest, and optional metadata callback context. It exits with usage status for invalid arguments and error status for I/O or digest failures.

Dependencies and integration points: Bridges the public library digest API with `programs/utils.c`, hash-alg parsing, and test programs.

Risks and test signals: Risks include salt parsing, output format stability, duplicate options, and file-size/read errors. Signals include command-line tests with known digest vectors and invalid-argument cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/cmd_digest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/cmd_dump_metadata.c -->
# sources/security-integrity/fsverity-utils/programs/cmd_dump_metadata.c

Purpose: This CLI command dumps fs-verity metadata from a verity-enabled file using the kernel `FS_IOC_READ_VERITY_METADATA` ioctl.

Important APIs and functions: `parse_metadata_type()` maps names `merkle_tree`, `descriptor`, and `signature` to UAPI constants. `fsverity_cmd_dump_metadata()` parses optional `--offset` and `--length`, opens the file, repeatedly calls the ioctl, and writes raw metadata to stdout.

Control flow and state: Without explicit offset/length, the command loops until ioctl returns zero bytes. With offset/length, it performs one bounded read. State is limited to the ioctl arg, buffer, file descriptor, and stdout descriptor wrapper.

Dependencies and integration points: Uses `fsverity_uapi.h`, shared `open_file`, `full_write`, and command dispatch.

Risks and test signals: Risks include raw binary stdout handling, offset/length validation, and kernel support differences. Signals include successful descriptor/tree/signature dumps and usage errors for malformed metadata type or incomplete offset/length pairs.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/cmd_dump_metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/cmd_enable.c -->
# sources/security-integrity/fsverity-utils/programs/cmd_enable.c

Purpose: This CLI command enables fs-verity on a target file, optionally setting hash algorithm, block size, salt, and a detached signature.

Important APIs and functions: `read_signature()` loads a nonempty signature file with a maximum size guard. `fsverity_cmd_enable()` parses tree parameters and `--signature`, opens the target file read-only, and calls `libfsverity_enable_with_sig`.

Control flow and state: Parsed options populate `libfsverity_merkle_tree_params`; optional signature bytes are allocated then freed after ioctl. Successful execution persists kernel fs-verity state on the file.

Dependencies and integration points: Integrates CLI parsing, library enable wrapper, Linux ioctl UAPI, and signatures created by `cmd_sign`.

Risks and test signals: Risks include irreversible enablement, signature file size constraints, hash parameter mismatch with precomputed signatures, and filesystem/kernel support. Signals include ioctl success, proper errno diagnostics, and usage failures for duplicate or invalid options.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/cmd_enable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/cmd_measure.c -->
# sources/security-integrity/fsverity-utils/programs/cmd_measure.c

Purpose: This command asks the kernel to measure a verity-enabled file and prints the kernel-reported digest.

Important APIs and functions: `fsverity_cmd_measure()` opens the file, prepares `struct fsverity_digest`, calls `FS_IOC_MEASURE_VERITY`, and formats the digest algorithm and bytes for output.

Control flow and state: It has a simple parse/open/ioctl/print flow. Runtime state is the opened file and digest buffer; persistent state is read-only kernel metadata on the file.

Dependencies and integration points: Used to compare kernel-measured digests with `cmd_digest`/library-computed digests. Depends on fs-verity UAPI and shared CLI utilities.

Risks and test signals: Kernel support and file state dominate failures. The command must handle unsupported files, digest buffer sizing, and output format compatibility. Signals include matching computed and measured digest for enabled files and expected errors for non-verity files.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/cmd_measure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/cmd_sign.c -->
# sources/security-integrity/fsverity-utils/programs/cmd_sign.c

Purpose: This CLI command computes a file digest and writes a PKCS#7 fs-verity signature suitable for kernel built-in verification.

Important APIs and functions: `fsverity_cmd_sign()` parses digest tree options plus certificate/key or PKCS#11 parameters, computes the digest with `libfsverity_compute_digest`, signs it with `libfsverity_sign_digest`, and writes DER bytes to the output file.

Control flow and state: Command state includes tree params, signature params, opened file descriptors, allocated digest, allocated signature, and output write status. It enforces argument validity before expensive crypto operations.

Dependencies and integration points: Connects digest computation, OpenSSL signing, CLI parameter parsing, and later `cmd_enable --signature` use.

Risks and test signals: Risks include mismatched digest params between signing and enabling, sensitive key handling, PKCS#11 availability, and output file overwrite semantics. Signals include sign/verify known-key tests and negative cases for missing cert/key.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/cmd_sign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/fsverity.c -->
# sources/security-integrity/fsverity-utils/programs/fsverity.c

Purpose: This is the main entrypoint and command dispatcher for the `fsverity` CLI.

Important APIs and functions: It defines the command table, help/usage rendering, option dispatch, version behavior, and main argument routing to `digest`, `enable`, `measure`, `sign`, and `dump_metadata` command handlers.

Control flow and state: `main()` identifies the subcommand, adjusts argc/argv, invokes the selected handler, and returns its status. Global state is limited to command metadata and process-level error output behavior.

Dependencies and integration points: Integrates all `programs/cmd_*.c` files, shared CLI utilities, version constants, and build-time feature availability.

Risks and test signals: Risks include command-name compatibility, usage text drift, and return-code conventions. Signals include `fsverity --help`, subcommand usage tests, unknown command errors, and version output checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/fsverity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/fsverity.h -->
# sources/security-integrity/fsverity-utils/programs/fsverity.h

Purpose: This private CLI header declares command structures, option constants, shared utility prototypes, and interfaces between the main dispatcher and subcommands.

Important APIs and types: It defines `struct fsverity_command`, command handler prototypes, file descriptor wrappers, option enum values, usage/error helpers, parsing helpers, and full-read/write/open utilities.

Control flow and state: No runtime state exists in the header, but it defines shared conventions for status codes, option parsing, and resource cleanup.

Dependencies and integration points: Included by every program command source and shared `programs/utils.c`.

Risks and test signals: Misdeclared handler signatures or option constants can break dispatch or parsing. Signals are successful compile, subcommand invocation, and common utility tests through CLI workflows.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/fsverity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/test_compute_digest.c -->
# sources/security-integrity/fsverity-utils/programs/test_compute_digest.c

Purpose: This test program validates `libfsverity_compute_digest()` against known data, edge cases, metadata callback behavior, and invalid parameter handling.

Important APIs and functions: It supplies read callbacks, known file contents or synthetic buffers, expected digest vectors, and callback implementations for Merkle tree size, tree blocks, and descriptor reporting.

Control flow and state: Tests construct parameter structs, call the library, compare returned digest bytes and callback records, and check negative errno results for invalid inputs. State is local test buffers and allocated digest objects.

Dependencies and integration points: Exercises public library API, hash algorithms, descriptor layout, and metadata callbacks without requiring kernel fs-verity support.

Risks and test signals: This is a high-value compatibility suite because digest changes affect every fs-verity consumer. Signals include exact known-answer hashes, empty-file behavior, salt/block-size variants, callback offsets, and validation failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/test_compute_digest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/test_hash_algs.c -->
# sources/security-integrity/fsverity-utils/programs/test_hash_algs.c

Purpose: This test program verifies public hash algorithm lookup and digest-size APIs.

Important APIs and functions: It calls `libfsverity_find_hash_alg_by_name()` and `libfsverity_get_digest_size()` for supported algorithms such as SHA-256 and SHA-512, plus unknown names/numbers.

Control flow and state: Tests are simple assertions over immutable algorithm metadata. There is no persistent state.

Dependencies and integration points: Protects CLI `--hash-alg` parsing, library parameter validation, and digest-size allocation behavior.

Risks and test signals: Risk is low but important: changing names, numbers, or digest sizes would break ABI and vectors. Signals are exact algorithm number and digest-size matches and zero results for unknown algorithms.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/test_hash_algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/test_sign_digest.c -->
# sources/security-integrity/fsverity-utils/programs/test_sign_digest.c

Purpose: This test program validates `libfsverity_sign_digest()` with fixture digests, certificate/key inputs, and invalid parameter cases.

Important APIs and functions: It constructs `libfsverity_digest` and `libfsverity_signature_params`, invokes signing, checks signature allocation/size, and verifies expected failures for missing or malformed inputs.

Control flow and state: Each test signs or rejects local fixture data. Allocated DER signature buffers are freed by the test. No kernel state is required.

Dependencies and integration points: Depends on OpenSSL-enabled builds and certificate/key test fixtures. It protects CLI `sign` and `enable --signature` interoperability.

Risks and test signals: Crypto backend differences may affect availability or DER details. Signals include nonempty DER output, correct negative errno classes, and clean behavior when optional PKCS#11 support is absent.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/test_sign_digest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/utils.c -->
# sources/security-integrity/fsverity-utils/programs/utils.c

Purpose: This file implements shared CLI utilities for error reporting, safe allocation, file open/close wrappers, full reads/writes, file size queries, hex parsing/printing, and tree parameter parsing.

Important APIs and functions: It provides `error_msg`, `error_msg_errno`, `xzalloc`/`xmalloc`, `open_file`, `filedes_close`, `full_read`, `full_write`, `get_file_size`, salt/hex helpers, hash-alg/block-size parsing, and common `parse_tree_param` behavior.

Control flow and state: Helpers maintain small resource state in `struct filedes` and otherwise operate statelessly. Full I/O helpers loop until requested bytes are processed or errors occur.

Dependencies and integration points: Used by all CLI subcommands and test utilities. It bridges libc file descriptors, libfsverity public params, and user-facing diagnostics.

Risks and test signals: Risks include partial I/O handling, numeric overflow, duplicate/invalid option reporting, and file descriptor cleanup. Signals are CLI tests for malformed options, full binary stdout writes, and reliable cleanup on errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/utils.h -->
# sources/security-integrity/fsverity-utils/programs/utils.h

Purpose: This header declares utility functions and resource wrappers shared by fsverity CLI command implementations.

Important APIs and types: It exposes `struct filedes`, allocation helpers, error printers, full I/O functions, file sizing, hex helpers, and tree-parameter parsing used by digest/sign/enable commands.

Control flow and state: No executable flow exists, but the header standardizes ownership and cleanup expectations for opened file descriptors and allocated buffers.

Dependencies and integration points: Included by command and test sources. It must remain consistent with `programs/utils.c`.

Risks and test signals: Header/implementation mismatch causes compile failures or subtle ABI issues within the program. Signals include all subcommands building and shared helper behavior covered through command tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/programs/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/scripts/do-release.sh -->
# sources/security-integrity/fsverity-utils/scripts/do-release.sh

Purpose: This release script automates fsverity-utils versioned release preparation, packaging, tagging, or verification steps for maintainers.

Important APIs and steps: It checks repository state, derives version information, builds distribution artifacts, may run tests, and coordinates signing or upload-ready outputs depending on project conventions.

Control flow and state: Shell control flow validates prerequisites before mutating release artifacts. Persistent state can include generated tarballs, tags, checksums, and temporary version files.

Dependencies and integration points: Integrates with `make`, git, release signing tools, and generated documentation or package metadata.

Risks and test signals: Release scripts are high-risk because they can publish incorrect versions or artifacts from dirty trees. Signals include dry-run/manual review, clean tree checks, reproducible archive contents, and successful build/test before release.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/scripts/do-release.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/scripts/run-sparse.sh -->
# sources/security-integrity/fsverity-utils/scripts/run-sparse.sh

Purpose: This script runs the Sparse static analyzer over fsverity-utils C sources with project include paths and build defines.

Important APIs and steps: It invokes `sparse` on library and program sources, supplying headers and flags needed to parse Linux-style annotations and UAPI structures.

Control flow and state: The script is stateless apart from analyzer output and process status. CI treats nonzero exit as failure.

Dependencies and integration points: Called by the GitHub Actions workflow and developer checks. Depends on the `sparse` binary, C headers, and Makefile-compatible flags.

Risks and test signals: Sparse availability and flag drift can create false negatives or false positives. Signals are clean analyzer runs and caught address-space/type warnings before runtime tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/scripts/run-sparse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fsverity-utils/scripts/run-tests.sh -->
# sources/security-integrity/fsverity-utils/scripts/run-tests.sh

Purpose: This shell script runs the fsverity-utils test suite, including library unit tests, CLI command checks, and optional kernel/filesystem integration tests.

Important APIs and steps: It builds or invokes test binaries, creates temporary files, computes/signs/enables/verifies digests, checks command output, and skips or adapts when kernel fs-verity support is unavailable.

Control flow and state: The script creates temporary directories and files, runs commands with expected statuses, and cleans up. Successful ioctl tests persist fs-verity metadata on temporary files only.

Dependencies and integration points: Integrates `fsverity` CLI, library test binaries, OpenSSL fixtures, Linux fs-verity support, and CI.

Risks and test signals: Integration tests are environment-sensitive due to filesystem/kernel requirements. Signals include deterministic digest vectors, signing tests, command usage checks, and clear skips when prerequisites are missing.
<!-- END_FILE_RESEARCH: sources/security-integrity/fsverity-utils/scripts/run-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/.github/dependabot.yml -->
# sources/security-integrity/gocryptfs/.github/dependabot.yml

Purpose: This Dependabot configuration keeps gocryptfs dependency metadata current, primarily for Go modules and GitHub Actions.

Important APIs and fields: It defines update ecosystems, directories, schedules, and possibly grouping or reviewer settings.

Control flow and state: Dependabot periodically opens pull requests; no repository runtime state is changed by the file itself.

Dependencies and integration points: Integrates with GitHub dependency scanning, `go.mod`, and workflow action versions.

Risks and test signals: Risks include noisy updates or missed security patches if schedules/directories drift. Signals are Dependabot PRs that pass CI and keep module/action versions current.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/.github/workflows/ci.yml -->
# sources/security-integrity/gocryptfs/.github/workflows/ci.yml

Purpose: This GitHub Actions workflow builds, tests, and statically checks gocryptfs across supported Go and platform configurations.

Important APIs and jobs: Jobs check out the repository, install dependencies, run build scripts, run Go tests, lint or static-check code, and exercise OpenSSL/non-OpenSSL build variants.

Control flow and state: Triggered by pushes and pull requests; matrix jobs create independent build/test state in GitHub runners.

Dependencies and integration points: Integrates `build.bash`, `build-without-openssl.bash`, `test.bash`, Go modules, FUSE/kernel prerequisites where available, and action-version management.

Risks and test signals: FUSE tests can be runner-sensitive, while pure Go tests should be deterministic. Signals include successful default and no-OpenSSL builds, unit tests, static analysis, and shell/script checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/Documentation/MANPAGE-render.bash -->
# sources/security-integrity/gocryptfs/Documentation/MANPAGE-render.bash

Purpose: This script renders gocryptfs manual pages from documentation sources into distributable manpage files.

Important APIs and steps: It likely invokes `pandoc` or compatible tooling for `gocryptfs.1` and `gocryptfs-xray.1`, ensuring release tarballs include pre-rendered manpages.

Control flow and state: It runs in the documentation directory context and writes generated manpage outputs. Persistent state is generated `.1` files.

Dependencies and integration points: Used by release packaging scripts and build/install workflows that avoid requiring documentation tools on end-user systems.

Risks and test signals: Tool-version drift can alter output formatting. Signals include successful rendering during packaging and generated manpages included in release artifacts.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/Documentation/MANPAGE-render.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/Makefile -->
# sources/security-integrity/gocryptfs/Makefile

Purpose: This Makefile wraps common gocryptfs build, install, uninstall, test, clean, and manpage operations.

Important APIs and targets: It delegates to Go build scripts, installs `gocryptfs`, `gocryptfs-xray`, documentation, and auxiliary files under configurable prefix paths, and exposes test/clean targets.

Control flow and state: Targets create binaries, install files, and remove build artifacts. Persistent state is generated binaries and installed filesystem paths.

Dependencies and integration points: Integrates shell build scripts, Go modules, documentation rendering, and packaging conventions.

Risks and test signals: Risks include install path mistakes, missing xray binary, stale manpages, and mismatch with shell scripts. Signals include `make`, `make test`, and staged install checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/benchmark-reverse.bash -->
# sources/security-integrity/gocryptfs/benchmark-reverse.bash

Purpose: This script benchmarks gocryptfs reverse mode, where a plaintext tree is exposed as an encrypted view.

Important APIs and steps: It sets up temporary directories, initializes or mounts reverse-mode filesystems, runs throughput or filesystem operation benchmarks, and records timings for comparison.

Control flow and state: The script creates temporary plaintext/cipher/mount paths, runs commands, unmounts, and cleans up. State is benchmark data and temporary filesystem contents.

Dependencies and integration points: Integrates the built `gocryptfs` binary, FUSE unmount helpers, shell tools, and benchmark documentation.

Risks and test signals: Benchmarks are environment-sensitive and can leave mounts behind on failure. Signals are successful mount/unmount, repeatable benchmark phases, and cleanup of temporary mounts.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/benchmark-reverse.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/benchmark.bash -->
# sources/security-integrity/gocryptfs/benchmark.bash

Purpose: This benchmark runner measures canonical gocryptfs performance scenarios, optionally comparing EncFS, loopback, OpenSSL on/off, dd-only modes, and XChaCha variants.

Important APIs and steps: It parses options, prepares temporary directories, initializes encrypted filesystems, mounts with selected flags, runs file creation/copy/read/write benchmarks, and prints comparable results.

Control flow and state: Option parsing controls benchmark modes. The script creates mount/cipher/plain paths, invokes external tools, and must unmount and clean up at exit.

Dependencies and integration points: Depends on the local `gocryptfs` binary, optional EncFS, FUSE support, dd/coreutils, and project comparison documentation.

Risks and test signals: Results are hardware/cache sensitive and not unit-test stable. Main signals are successful command execution, no leftover mounts, and sane option validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/benchmark.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/build-without-openssl.bash -->
# sources/security-integrity/gocryptfs/build-without-openssl.bash

Purpose: This script builds gocryptfs without OpenSSL support, forcing the pure-Go crypto path.

Important APIs and steps: It sets `CGO_ENABLED=0` and sources or invokes `build.bash`, causing build tags and backend selection to exclude OpenSSL-dependent code.

Control flow and state: The script is a thin environment wrapper. Persistent state is the resulting static or pure-Go binary.

Dependencies and integration points: Used by CI, release packaging, and portability checks. It validates that gocryptfs remains buildable without C toolchains or OpenSSL libraries.

Risks and test signals: Risks include accidental cgo dependency or build-script behavior that ignores `CGO_ENABLED`. Signals are successful no-OpenSSL build and tests using Go crypto backends.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/build-without-openssl.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/build.bash -->
# sources/security-integrity/gocryptfs/build.bash

Purpose: This is the main gocryptfs build script for producing `gocryptfs` and related binaries with version metadata.

Important APIs and steps: It determines git version information, configures Go build flags/ldflags, compiles the main binary and `gocryptfs-xray`, and may report binary backend information.

Control flow and state: It exits on build errors and writes binaries into the source tree. Version strings are derived from git or fallback files.

Dependencies and integration points: Used by Makefile, CI, release packaging, benchmarks, and no-OpenSSL wrapper.

Risks and test signals: Risks include dirty-tree version ambiguity, missing Go environment, or OpenSSL/cgo incompatibility. Signals are successful binary builds and version output matching expected git/version metadata.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/build.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/cli_args.go -->
# sources/security-integrity/gocryptfs/cli_args.go

Purpose: This file defines gocryptfs command-line option parsing and stores parsed options in `argContainer`.

Important APIs and functions: `argContainer` contains operation flags, mount flags, crypto flags, profiling paths, FIDO2 options, exclusion rules, config overrides, and internal parsed state. `prefixOArgs` converts mount-style `-o a,b` options into normal flags. `convertToDoubleDash` preserves compatibility after moving to `pflag`. `parseCliOpts`, `prettyArgs`, `countOpFlags`, and `isFlagPassed` implement parsing and validation.

Control flow and state: Parsing preprocesses args, registers all flags, handles tri-state OpenSSL auto mode, rejects incompatible password/master-key/FIDO options, validates badname globs and long-name thresholds, and records explicitly passed scrypt cost.

Dependencies and integration points: Feeds main init/mount/passwd/info/fsck control flow, configfile creation, crypto backend selection, FUSE mount options, and reverse-mode exclusions.

Risks and test signals: CLI compatibility is high-risk. Known dash-duplication behavior around `-extpass -X` is documented. Signals include parsing tests for `-o`, single/double dash conversion, option conflicts, OpenSSL auto selection, and operation flag counts.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/cli_args.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/cli_args_test.go -->
# sources/security-integrity/gocryptfs/cli_args_test.go

Purpose: This test file locks down gocryptfs command-line parsing compatibility.

Important APIs and functions: `TestPrefixOArgs` verifies `-o` and `-o=` expansion, ordering, empty entries, and error handling. `TestConvertToDoubleDash` checks conversion from old single-dash long flags to pflag-style double dash while preserving `-h` and `--`. `TestParseCliOpts` checks selected parsed fields.

Control flow and state: Tests are table-driven and compare full argument slices or parsed `argContainer` values. They may depend on crypto backend preference helpers for OpenSSL defaults.

Dependencies and integration points: Protects user-facing CLI behavior and mount/fstab compatibility after parser changes.

Risks and test signals: The tests intentionally encode compatibility quirks, so changing behavior can be a regression even if pflag would parse it differently. Strong signals are exact transformed argument slices and expected parsed options.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/cli_args_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/codelingo.yaml -->
# sources/security-integrity/gocryptfs/codelingo.yaml

Purpose: This small configuration file defines CodeLingo/static-review tenets for the gocryptfs repository.

Important APIs and fields: It contains a `tenets` list that points external analysis tooling at selected rule sets.

Control flow and state: It has no runtime control flow. Its only state is analyzer configuration.

Dependencies and integration points: Integrates with CodeLingo or similar code-review automation, not the gocryptfs binary.

Risks and test signals: Stale analyzer config may silently stop running useful checks. Signal is external service recognition and no configuration parse errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/codelingo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/atomicrename/main.go -->
# sources/security-integrity/gocryptfs/contrib/atomicrename/main.go

Purpose: This contrib tool stress-tests atomic rename behavior, useful for filesystems and FUSE implementations.

Important APIs and functions: The program creates/writes files, repeatedly renames between paths, and likely checks visible content or existence invariants using Go `os` operations.

Control flow and state: It runs a loop over temporary or user-supplied paths, mutating filesystem namespace state through rename operations. State is on-disk test files.

Dependencies and integration points: Used manually against gocryptfs mounts or backing filesystems to observe rename atomicity and crash/visibility behavior.

Risks and test signals: As a contrib diagnostic, it may be destructive in the target directory if used carelessly. Signals are absence of inconsistent intermediate states, failed renames, or unexpected file contents.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/atomicrename/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/cleanup-tmp-mounts.sh -->
# sources/security-integrity/gocryptfs/contrib/cleanup-tmp-mounts.sh

Purpose: This helper script cleans up leftover temporary gocryptfs/FUSE mounts from tests or manual runs.

Important APIs and steps: It scans mount output for project test paths and invokes unmount helpers such as `fusermount`, `umount`, or project scripts.

Control flow and state: It mutates system mount state by unmounting matching paths. No persistent repository state is written.

Dependencies and integration points: Used by developers and test wrappers to recover from interrupted FUSE tests.

Risks and test signals: Mount matching must be conservative to avoid unmounting unrelated filesystems. Signal is successful removal of stale project mounts without affecting unrelated mounts.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/cleanup-tmp-mounts.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/findholes/holes/holes.go -->
# sources/security-integrity/gocryptfs/contrib/findholes/holes/holes.go

Purpose: This package inspects sparse-file hole/data layout using `SEEK_DATA` and `SEEK_HOLE`.

Important APIs and functions: It defines `Segment`, `SegmentType`, `Whence`, string/pretty-print helpers, `Find(fd)` to discover alternating data/hole ranges, `Verify(fd, segments)` to validate seek behavior at every offset, and `Create(path)` to generate a sparse test file.

Control flow and state: `Find` starts by identifying whether offset zero is data or hole, then alternates `SEEK_HOLE` and `SEEK_DATA` until ENXIO signals no more data. `Create` writes bytes at random offsets and may truncate to force trailing holes.

Dependencies and integration points: Used by the contrib `findholes` CLI to test sparse-file behavior through gocryptfs mounts.

Risks and test signals: `SEEK_DATA` semantics vary across filesystems. `Verify` can be expensive because it checks each offset. Signals include coherent segment sequences ending in EOF and no seek-loop errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/findholes/holes/holes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/findholes/main.go -->
# sources/security-integrity/gocryptfs/contrib/findholes/main.go

Purpose: This CLI wraps the `holes` package to create, inspect, print, and verify sparse-file hole maps.

Important APIs and functions: It parses command-line arguments, opens the target file, optionally creates a sparse fixture, calls `holes.Find`, prints `holes.PrettyPrint`, and invokes verification.

Control flow and state: The command mutates a file only in create mode; otherwise it reads seek metadata from an opened descriptor. Exit status reflects open/find/verify errors.

Dependencies and integration points: Used manually against gocryptfs and underlying filesystems to compare sparse-file support.

Risks and test signals: Filesystem-dependent semantics may look like failures. Signals are stable hole/data segment output and successful verification over the same file descriptor.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/findholes/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/getdents-debug/getdents/getdents.go -->
# sources/security-integrity/gocryptfs/contrib/getdents-debug/getdents/getdents.go

Purpose: This Go diagnostic repeatedly calls the Linux `getdents` syscall on a directory to debug directory entry behavior.

Important APIs and functions: It opens a directory with `unix.Open`, allocates a buffer, calls `unix.Getdents`, prints byte counts and errors, closes the descriptor, and sleeps between iterations.

Control flow and state: The command loops indefinitely or until error/interrupt, repeatedly observing directory stream state. It does not persist repository state.

Dependencies and integration points: Used to debug gocryptfs/FUSE directory listing behavior, especially low-level `getdents` quirks.

Risks and test signals: Linux-specific and diagnostic only. Signals are consistent total bytes read and surfaced syscall errors while directory contents change or remain stable.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/getdents-debug/getdents/getdents.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/getdents-debug/getdents_c/Makefile -->
# sources/security-integrity/gocryptfs/contrib/getdents-debug/getdents_c/Makefile

Purpose: This tiny Makefile builds the C `getdents` diagnostic binary.

Important APIs and targets: The `getdents_c` target compiles `getdents.c` with `gcc`.

Control flow and state: It creates one local executable as build state.

Dependencies and integration points: Complements the Go getdents diagnostic with a direct C syscall implementation.

Risks and test signals: Requires `gcc` and Linux syscall headers. Signal is successful compilation and executable behavior against test directories.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/getdents-debug/getdents_c/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/getdents-debug/getdents_c/getdents.c -->
# sources/security-integrity/gocryptfs/contrib/getdents-debug/getdents_c/getdents.c

Purpose: This C diagnostic directly invokes the Linux `getdents` syscall to inspect directory entry bytes and errors.

Important APIs and functions: `main` opens a directory, calls `syscall(SYS_getdents, ...)` with a raw buffer, prints results, closes the descriptor, and repeats or exits depending on errors.

Control flow and state: Runtime state is a file descriptor, buffer, byte counters, and errno. It reads directory metadata but does not write files.

Dependencies and integration points: Used alongside the Go version to separate gocryptfs/FUSE issues from Go runtime or x/sys wrapper behavior.

Risks and test signals: Linux-specific syscall layout and buffer parsing can vary. Signals include reproducible byte counts and errno values compared with the Go diagnostic.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/getdents-debug/getdents_c/getdents.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/getdents-debug/readdirnames/readdirnames.go -->
# sources/security-integrity/gocryptfs/contrib/getdents-debug/readdirnames/readdirnames.go

Purpose: This diagnostic uses higher-level Go directory APIs to repeatedly read entry names from a directory.

Important APIs and functions: It opens a path, calls `Readdirnames` or equivalent, prints names/errors, closes, and repeats after a short sleep.

Control flow and state: It observes directory listing behavior without mutating files. Runtime state is the open directory and returned name slice.

Dependencies and integration points: Complements raw getdents tools by showing behavior through Go's `os.File` directory abstraction over gocryptfs/FUSE mounts.

Risks and test signals: Output depends on directory contents and Go runtime directory buffering. Signals are consistent names and error behavior compared with raw syscall diagnostics.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/getdents-debug/readdirnames/readdirnames.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/gocryptfs-maybe.bash -->
# sources/security-integrity/gocryptfs/contrib/gocryptfs-maybe.bash

Purpose: This convenience wrapper conditionally mounts or uses gocryptfs depending on whether a target appears already mounted or available.

Important APIs and steps: It parses shell arguments, checks mount/path state, and invokes `gocryptfs` only when needed.

Control flow and state: The script branches on filesystem/mount status and may create a FUSE mount. Persistent state is the resulting mount if it runs gocryptfs.

Dependencies and integration points: Used manually in workflows where encrypted directories should be mounted on demand.

Risks and test signals: Mount detection must be reliable to avoid duplicate mounts or missed mounts. Signals are idempotent repeated invocation and correct pass-through of gocryptfs arguments.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/gocryptfs-maybe.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/gocryptfssh -->
# sources/security-integrity/gocryptfs/contrib/gocryptfssh

Purpose: This script integrates gocryptfs with SSH-style remote access, likely mounting encrypted storage over an SSH transport or exposing a helper command for remote encrypted home/work directories.

Important APIs and steps: It parses shell options, invokes `ssh`, `sshfs`, or gocryptfs-related commands, and coordinates mount paths.

Control flow and state: Runtime control flow validates arguments, establishes remote/local mounts, and exits on command failures. Persistent state can include active SSH/FUSE mounts.

Dependencies and integration points: Contrib-level integration with gocryptfs, SSH tooling, and FUSE mount helpers.

Risks and test signals: Risks include quoting of remote paths, credential prompts, stale mounts, and shell injection if paths are not quoted. Signals are successful mount/session setup and cleanup under paths with spaces or unusual characters.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/gocryptfssh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/maxlen.bash -->
# sources/security-integrity/gocryptfs/contrib/maxlen.bash

Purpose: This script probes maximum filename or path lengths through gocryptfs and backing filesystems.

Important APIs and steps: It creates progressively longer names, observes success/failure, and reports limits, often relevant to encrypted name expansion and long-name hashing.

Control flow and state: It mutates a temporary directory by creating/removing files with candidate names. Persistent state should be cleaned up after probing.

Dependencies and integration points: Supports validation of `-longnames`, `-longnamemax`, encrypted filename encoding, and filesystem limits.

Risks and test signals: Must avoid leaving extreme-name files behind. Signals are detected length boundaries and expected behavior on mounted encrypted filesystems.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/maxlen.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/mount-ext4-ramdisk.sh -->
# sources/security-integrity/gocryptfs/contrib/mount-ext4-ramdisk.sh

Purpose: This helper creates and mounts an ext4 ramdisk for fast testing or benchmarking.

Important APIs and steps: It allocates a tmpfs/loop or ram-backed block image, formats ext4, creates a mountpoint, and mounts it.

Control flow and state: The script mutates system mount and block-device state and requires cleanup/unmount after use.

Dependencies and integration points: Used for gocryptfs benchmarks/tests that need a fast disposable ext4 backing filesystem.

Risks and test signals: Requires elevated privileges and can consume RAM. Signals include successful ext4 mount and clear cleanup instructions or behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/mount-ext4-ramdisk.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/statfs/statfs.go -->
# sources/security-integrity/gocryptfs/contrib/statfs/statfs.go

Purpose: This small diagnostic prints `statfs` information for a path as JSON.

Important APIs and functions: `main` parses exactly one path, calls `unix.Statfs`, marshals `unix.Statfs_t` with `json.MarshalIndent`, and prints it.

Control flow and state: The command is read-only and exits with usage or syscall errors. It persists no state.

Dependencies and integration points: Useful for inspecting gocryptfs/FUSE filesystem statfs passthrough and comparing with backing filesystems.

Risks and test signals: Linux/Go struct fields can vary by platform. Signals are successful JSON output and meaningful syscall errors for invalid paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/statfs/statfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/statvsfstat/statvsfstat.go -->
# sources/security-integrity/gocryptfs/contrib/statvsfstat/statvsfstat.go

Purpose: This diagnostic compares metadata returned by path-based `stat` and descriptor-based `fstat`.

Important APIs and functions: It opens a path, calls `unix.Stat` and `unix.Fstat`, and prints or compares the returned `Stat_t` values.

Control flow and state: The command observes filesystem metadata and does not mutate files beyond opening descriptors.

Dependencies and integration points: Used to debug FUSE consistency in gocryptfs between lookup/path and open-file metadata paths.

Risks and test signals: Metadata can legitimately change between calls on active files. Signals are matching stable fields for unchanged files and clear display of differences.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/contrib/statvsfstat/statvsfstat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/crossbuild.bash -->
# sources/security-integrity/gocryptfs/crossbuild.bash

Purpose: This script verifies gocryptfs builds across supported `GOOS`/`GOARCH` combinations.

Important APIs and steps: It defines a build helper that compiles with `without_openssl`, runs package test compilation where appropriate, and invokes it for Linux, Darwin, and FreeBSD architectures including ARM variants.

Control flow and state: It sets environment variables per target and discards binaries to `/dev/null`. State is limited to Go build cache and test compilation artifacts.

Dependencies and integration points: Used by maintainers/CI to prevent portability regressions in pure-Go paths.

Risks and test signals: Cross-compilation can miss runtime FUSE/platform issues but catches compile-time portability. Signals are successful builds for all listed targets and selected test compilation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/crossbuild.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/ctlsock/ctlsock.go -->
# sources/security-integrity/gocryptfs/ctlsock/ctlsock.go

Purpose: This package provides a Go client for gocryptfs control sockets.

Important APIs and functions: `CtlSock` wraps a Unix-domain socket connection. `New(socketPath)` connects with timeout behavior, `Query(req)` JSON-encodes a `RequestStruct`, reads and decodes a `ResponseStruct`, returns server-reported errors through `ResponseStruct.Error`, and `Close` closes the connection.

Control flow and state: A `CtlSock` instance owns one socket connection. Query is request/response over JSON and applies a 10-second timeout to avoid hangs.

Dependencies and integration points: Used by `gocryptfs-xray` and external tools to encrypt/decrypt paths through a mounted filesystem's control socket.

Risks and test signals: Risks include socket timeout tuning, JSON compatibility, and propagating server errors cleanly. Signals are round-trip path encrypt/decrypt queries and connection failure handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/ctlsock/ctlsock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/ctlsock/json_abi.go -->
# sources/security-integrity/gocryptfs/ctlsock/json_abi.go

Purpose: This file defines the stable JSON request/response ABI for the gocryptfs control socket.

Important APIs and types: `RequestStruct` carries either encryption or decryption path requests and must not request both at once. `ResponseStruct` carries encrypted/decrypted paths and an error string.

Control flow and state: No executable logic except methods in companion files; the struct field names and JSON encoding form the wire contract.

Dependencies and integration points: Shared by the client package, control socket server, and `gocryptfs-xray`.

Risks and test signals: ABI changes can break external tools. Signals include JSON round-trip tests and compatibility with older mounted gocryptfs instances.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/ctlsock/json_abi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/daemonize.go -->
# sources/security-integrity/gocryptfs/daemonize.go

Purpose: This file implements gocryptfs foreground/background daemonization behavior in Go.

Important APIs and functions: `exitOnUsr1` waits for mount-success notification. `forkChild` re-executes the current binary with `-fg`, wires notification through `-notifypid`, and returns success/failure based on signal or child exit. `redirectStdFds` redirects stdin/stdout/stderr for background operation and syslog behavior.

Control flow and state: Parent process waits for SIGUSR1 from the child mount process, then exits. The child becomes the foreground mount process. Process arguments and file descriptors are mutated.

Dependencies and integration points: Integrates with CLI flags, FUSE mount startup, syslog logging, and service managers.

Risks and test signals: Re-exec and signal timing are fragile. Risks include lost notifications, bad fd redirection, and incorrect exit code propagation. Signals are successful background mount notification and clean failure when child exits early.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/daemonize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/fsck.go -->
# sources/security-integrity/gocryptfs/fsck.go

Purpose: This file implements gocryptfs filesystem checking over encrypted storage, detecting corrupt filenames, unreadable files, xattr errors, symlink issues, and mitigated corruption warnings.

Important APIs and functions: `fsckObj` carries counters, root paths, crypto/name transformers, and options. Methods include `markCorrupt`, `markSkipped`, `abs`, `dir`, `file`, `symlink`, `xattrs`, and watcher helpers for mitigated corruptions during open/read/listxattr. `fsck(args)` is the main entrypoint.

Control flow and state: `fsck` loads config, initializes crypto, walks directories recursively, optionally respects one-filesystem boundaries, decrypts names, reads file blocks through gocryptfs logic, checks symlink targets, and tallies corrupt/skipped entries. It persists no repairs, only diagnostics and exit code.

Dependencies and integration points: Integrates configfile, content encryption, name encryption, syscall compatibility, FUSE-like read paths, xattr handling, and CLI flags.

Risks and test signals: Corruption checks can trigger reads over large trees and must avoid crossing filesystems when requested. Signals include expected exit codes, corrupt/skipped counters, and fixture tests with damaged names/data/xattrs.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/fsck.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/gocryptfs-xray/paths_ctlsock.go -->
# sources/security-integrity/gocryptfs/gocryptfs-xray/paths_ctlsock.go

Purpose: This xray helper resolves encrypted/plain path translations through a running gocryptfs control socket.

Important APIs and functions: It opens a `ctlsock.CtlSock`, builds `RequestStruct` values for encrypt or decrypt path operations, sends queries, handles `ResponseStruct` errors, and prints or returns translated paths.

Control flow and state: Runtime state is the socket connection and request/response JSON. No filesystem state is changed except socket communication.

Dependencies and integration points: Connects `gocryptfs-xray` CLI modes with mounted gocryptfs instances that expose `-ctlsock`.

Risks and test signals: Requires a live matching mount and correct ABI. Signals are xray tests that map known plaintext/ciphertext names and graceful errors for missing sockets.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/gocryptfs-xray/paths_ctlsock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/gocryptfs-xray/xray_main.go -->
# sources/security-integrity/gocryptfs/gocryptfs-xray/xray_main.go

Purpose: This is the main program for `gocryptfs-xray`, a diagnostic tool for inspecting gocryptfs config files, encrypted names, master keys, and path mappings.

Important APIs and functions: It parses flags, loads config files, decrypts master keys when credentials are supplied, prints config/feature information, decodes encrypted filenames, and delegates control-socket path conversion.

Control flow and state: Depending on flags, it performs read-only config inspection, key derivation/decryption, or socket queries. It does not mount filesystems.

Dependencies and integration points: Integrates configfile, password reading, name/content crypto helpers, ctlsock, and fixture tests under `xray_tests`.

Risks and test signals: It can expose sensitive master-key/config information, so output handling matters. Signals include tests over AES-GCM and AES-SIV fixture filesystems and expected decode results.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/gocryptfs-xray/xray_main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/gocryptfs-xray/xray_tests/aesgcm_fs/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/gocryptfs-xray/xray_tests/aesgcm_fs/gocryptfs.conf

Purpose: This fixture config represents a small AES-GCM gocryptfs filesystem used by xray tests.

Important fields: It contains creator/version metadata, feature flags such as HKDF/GCM IV/name encryption settings, scrypt parameters, and encrypted master key data.

Control flow and state: It is static JSON-like persistent filesystem configuration. Tests read and decrypt it with known credentials.

Dependencies and integration points: Used by `xray_test.go` and configfile loading/decryption code to verify AES-GCM fixture behavior.

Risks and test signals: Fixture drift can break expected vectors. Signals are successful config parse, expected feature flags, and reproducible xray output.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/gocryptfs-xray/xray_tests/aesgcm_fs/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/gocryptfs-xray/xray_tests/aessiv_fs/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/gocryptfs-xray/xray_tests/aessiv_fs/gocryptfs.conf

Purpose: This fixture config represents an AES-SIV gocryptfs filesystem for xray tests.

Important fields: It stores version/creator metadata, feature flags including AES-SIV-related behavior, scrypt KDF settings, and encrypted master key bytes.

Control flow and state: Static persistent configuration only. Tests load it to verify alternate content/name crypto paths.

Dependencies and integration points: Used by `gocryptfs-xray` tests and configfile/content encryption selection logic.

Risks and test signals: The fixture must remain aligned with known password and expected output. Signals include config parse/decrypt success and xray recognition of AES-SIV mode.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/gocryptfs-xray/xray_tests/aessiv_fs/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/gocryptfs-xray/xray_tests/xray_test.go -->
# sources/security-integrity/gocryptfs/gocryptfs-xray/xray_tests/xray_test.go

Purpose: This test suite validates `gocryptfs-xray` against bundled AES-GCM and AES-SIV fixture filesystems.

Important APIs and functions: Tests execute or call xray functionality to inspect configs, decrypt known data, translate names, and verify expected output for fixture directories.

Control flow and state: Tests read static fixture config/files and compare output. They should avoid mutating fixtures.

Dependencies and integration points: Covers xray main logic, configfile parsing, content/name crypto setup, and ctlsock-independent fixture inspection.

Risks and test signals: Fixture tests can become brittle when output text changes. Strong signals are exact expected fields, decrypted names, and mode-specific behavior for AES-GCM versus AES-SIV.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/gocryptfs-xray/xray_tests/xray_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/help.go -->
# sources/security-integrity/gocryptfs/help.go

Purpose: This file renders short and long command-line help for gocryptfs.

Important APIs and functions: `tUsage` contains the usage template. `helpShort()` prints concise syntax and common options. `helpLong()` prints extended option descriptions, notes, and compatibility guidance.

Control flow and state: Help functions write to stdout/stderr and exit behavior is controlled by callers in CLI parsing. No persistent state is changed.

Dependencies and integration points: Integrated with `parseCliOpts`, `-h`, `-hh`, and syntax-error paths. Text must stay aligned with registered flags in `cli_args.go`.

Risks and test signals: Drift between help text and actual flags confuses users. Signals include help-output tests or manual checks after CLI changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/help.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/info.go -->
# sources/security-integrity/gocryptfs/info.go

Purpose: This file implements the `-info` operation, pretty-printing a gocryptfs config file for humans while hiding sensitive fields.

Important APIs and functions: `info(filename)` loads the config, strips or redacts encrypted key material and sensitive FIDO2 values, marshals remaining metadata, and prints it.

Control flow and state: It reads a config file, transforms an in-memory representation, and writes output. It does not modify the config on disk.

Dependencies and integration points: Uses `internal/configfile`, JSON formatting, logging, and CLI operation dispatch.

Risks and test signals: Sensitive fields must remain redacted. Signals include `-info` output containing version/feature flags but not raw encrypted key or secret token material.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/init_dir.go -->
# sources/security-integrity/gocryptfs/init_dir.go

Purpose: This file implements `gocryptfs -init` for forward and reverse mode filesystem initialization.

Important APIs and functions: `isEmptyDir` verifies an existing empty directory, `isDir` validates reverse-mode source directories, and `initDir(args)` creates config files and forward-mode `gocryptfs.diriv` as needed.

Control flow and state: Forward mode requires an empty cipherdir, obtains/generates credentials, creates `gocryptfs.conf`, writes initial directory IV when names are encrypted, and handles custom config paths. Reverse mode uses `.gocryptfs.reverse.conf` next to plaintext data and does not require emptiness.

Dependencies and integration points: Integrates CLI args, password/master-key/FIDO2 handling, `configfile.Create`, name encryption diriv generation, and logging.

Risks and test signals: Initialization persists the root trust/config state, so partial failures and unsafe directory selection are high-risk. Signals include created config permissions, correct feature flags, diriv presence/absence, and refusal to initialize nonempty forward dirs.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/init_dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/config_file.go -->
# sources/security-integrity/gocryptfs/internal/configfile/config_file.go

Purpose: This file reads, writes, creates, validates, encrypts, and decrypts `gocryptfs.conf` files, including feature flags and master-key wrapping.

Important APIs and types: `ConfFile`, `FIDO2Params`, and `CreateArgs` model persisted config and creation inputs. `Create`, `Load`, `LoadAndDecrypt`, `DecryptMasterKey`, `EncryptKey`, `WriteFile`, `getKeyEncrypter`, and `ContentEncryption` are core APIs.

Control flow and state: `Create` assembles feature flags, generates or accepts a master key, encrypts it with an scrypt-derived key and content encryption, wipes temporary keys, validates, and atomically writes JSON. `Load` unmarshals and validates. `WriteFile` writes `filename.tmp`, syncs, and renames over the target.

Dependencies and integration points: Integrates content encryption, crypto core, scrypt KDF, FIDO2 metadata, init/passwd/mount/xray flows, and exit-code typed errors.

Risks and test signals: This is security-critical. Risks include secret leakage, wrong feature flags, non-atomic writes, weak KDF parameters, and backward compatibility. Signals include config fixture tests, wrong-password errors, timing/KDF tests, and feature validation tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/config_file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/config_test.go -->
# sources/security-integrity/gocryptfs/internal/configfile/config_test.go

Purpose: This test suite validates config loading, decryption, creation, feature flags, KDF behavior, and compatibility fixtures.

Important APIs and functions: It tests `LoadAndDecrypt`, `Create`, `ContentEncryption`, feature flag recognition, plaintext-name configs, AES-SIV reverse-mode configs, long-name settings, and wrong-password behavior using fixture files.

Control flow and state: Tests load static configs, create temporary config files, check generated feature flags and encrypted key behavior, and assert KDF runtime is not trivially fast.

Dependencies and integration points: Covers configfile integration with content encryption, scrypt, tlog warning control, and fixture configs in `config_test/`.

Risks and test signals: Time-based scrypt minimum checks can be environment-sensitive. Strong signals are v1 rejection, v2 successful decrypt, wrong password failure, generated feature flags, and known/unknown feature handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/config_test/PlaintextNames.conf -->
# sources/security-integrity/gocryptfs/internal/configfile/config_test/PlaintextNames.conf

Purpose: This fixture represents a gocryptfs config with plaintext filename mode enabled.

Important fields: It stores version/creator metadata, encrypted master key, scrypt parameters, and feature flags that include plaintext-name behavior while omitting encrypted-name features such as diriv/longnames.

Control flow and state: Static persistent config fixture only. Tests load/decrypt it with known credentials.

Dependencies and integration points: Used by config tests to verify plaintext-name feature flag interpretation and creation/loading compatibility.

Risks and test signals: Fixture must remain synchronized with expected password and feature assertions. Signals are successful decrypt and correct plaintext-name mode detection.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/config_test/PlaintextNames.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/config_test/StrangeFeature.conf -->
# sources/security-integrity/gocryptfs/internal/configfile/config_test/StrangeFeature.conf

Purpose: This fixture includes an unknown or unsupported feature flag to verify defensive config validation.

Important fields: It resembles a normal config but contains a feature flag not recognized by current code.

Control flow and state: Static fixture; loading should fail validation rather than silently mounting an unsupported format.

Dependencies and integration points: Used by `TestLoadV2StrangeFeature` and feature validation logic.

Risks and test signals: This protects forward compatibility: unknown feature flags must fail closed. Signal is a predictable load error with the deprecated/unsupported filesystem exit classification.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/config_test/StrangeFeature.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/config_test/v1.conf -->
# sources/security-integrity/gocryptfs/internal/configfile/config_test/v1.conf

Purpose: This fixture represents an obsolete v1 gocryptfs config that current code must reject.

Important fields: It contains legacy version/config fields and encrypted key/KDF data in the older format.

Control flow and state: Static test fixture only. Loading attempts should fail validation.

Dependencies and integration points: Used by `TestLoadV1` to protect deprecation behavior and avoid mounting unsupported on-disk formats.

Risks and test signals: Accidentally accepting obsolete formats could expose incompatible crypto or metadata behavior. Signal is deterministic rejection.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/config_test/v1.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/config_test/v2.conf -->
# sources/security-integrity/gocryptfs/internal/configfile/config_test/v2.conf

Purpose: This fixture is a known-good v2 gocryptfs config used to verify successful loading and decryption.

Important fields: It contains version, feature flags, encrypted master key, and scrypt parameters matching the test password.

Control flow and state: Static fixture; tests read and decrypt it but do not modify it.

Dependencies and integration points: Used by config tests for the main supported config path and scrypt runtime check.

Risks and test signals: Fixture drift breaks known-password tests. Signals are successful decrypt, validation pass, and KDF runtime above the brute-force-protection threshold.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/config_test/v2.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/feature_flags.go -->
# sources/security-integrity/gocryptfs/internal/configfile/feature_flags.go

Purpose: This file defines gocryptfs feature flags and helpers for recognizing and querying them in config files.

Important APIs and types: `flagIota` enumerates features such as GCM IV size, HKDF, plaintext names, diriv, EME names, longnames, raw64, AES-SIV, FIDO2, long-name max, deterministic names, XChaCha, and related compatibility flags. `knownFlags`, `isFeatureFlagKnown`, and `ConfFile.IsFeatureFlagSet` implement mapping and lookup.

Control flow and state: Feature flags persist as strings in config JSON. Runtime lookup scans `ConfFile.FeatureFlags`.

Dependencies and integration points: Used by config validation, init, mount crypto selection, name encryption behavior, and xray.

Risks and test signals: Feature flags are the on-disk compatibility gate; unknown flags must fail closed and known flags must not be renamed casually. Signals include known-flag tests and fixture validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/feature_flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/scrypt.go -->
# sources/security-integrity/gocryptfs/internal/configfile/scrypt.go

Purpose: This file implements the scrypt KDF parameter object used to derive config key-encryption keys from passwords.

Important APIs and types: `ScryptKDF` stores salt and parameters. `NewScryptKDF(logN)` creates fresh random salt and configured N/r/p values. `DeriveKey(password)` runs scrypt to produce a key for master-key encryption.

Control flow and state: Salt and cost parameters persist in `gocryptfs.conf`; derived keys are runtime secrets that callers wipe after use. Validation bounds on logN are enforced by config validation and tests.

Dependencies and integration points: Used by `ConfFile.EncryptKey`, `ConfFile.DecryptMasterKey`, init, mount, passwd, and tests.

Risks and test signals: Weak or invalid KDF parameters reduce password security or cause resource exhaustion. Signals include parameter validation tests, wrong-password failures, and minimum runtime checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/scrypt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/scrypt_test.go -->
# sources/security-integrity/gocryptfs/internal/configfile/scrypt_test.go

Purpose: This test file validates scrypt KDF construction, parameter bounds, and derived-key behavior.

Important APIs and functions: Tests cover `NewScryptKDF`, `DeriveKey`, default logN behavior, invalid cost handling, salt presence, and output length or consistency expectations.

Control flow and state: Tests create KDF objects and derive keys from test passwords. No persistent repository files are modified.

Dependencies and integration points: Protects password-to-key derivation used by config encryption/decryption.

Risks and test signals: KDF tests can be time-sensitive if they run expensive settings. Signals include deterministic derivation for same salt/password, different salts producing different keys, and validation of allowed logN range.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/scrypt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/validate.go -->
# sources/security-integrity/gocryptfs/internal/configfile/validate.go

Purpose: This file validates `ConfFile` combinations before loading, using, or writing config files.

Important APIs and functions: `ConfFile.Validate()` checks on-disk version, encrypted key presence/length, scrypt parameters, known feature flags, mutually incompatible feature combinations, required fields such as FIDO2 params, and long-name constraints.

Control flow and state: Validation is read-only over the config object and returns errors for unsupported or inconsistent state. It is called during `Create`, `Load`, `WriteFile`, and `ContentEncryption`.

Dependencies and integration points: Serves as the compatibility/security gate for all config consumers.

Risks and test signals: Overly permissive validation can mount unsupported filesystems; overly strict validation can strand valid users. Signals include fixture tests for v1 rejection, unknown feature rejection, and generated config validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/configfile/validate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/bpool.go -->
# sources/security-integrity/gocryptfs/internal/contentenc/bpool.go

Purpose: This file implements a fixed-size byte-slice pool used by content encryption to reduce allocations on hot read/write paths.

Important APIs and types: `bPool` embeds `sync.Pool` and records the required slice length. `newBPool`, `Put`, and `Get` create, return, and retrieve fixed-size buffers.

Control flow and state: `Put` expands slices to capacity and panics if length does not match the pool's configured size. `Get` asserts returned slice length. Pool contents are transient runtime memory.

Dependencies and integration points: Used by `ContentEnc` for ciphertext blocks, plaintext blocks, and request-sized buffers.

Risks and test signals: Returning a wrong-sized or still-referenced buffer can corrupt encryption operations. Panics protect internal misuse. Signals include allocation benchmarks and tests that exercise read/write paths without pool-size panics.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/bpool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/content.go -->
# sources/security-integrity/gocryptfs/internal/contentenc/content.go

Purpose: This file implements block-level encryption and decryption for gocryptfs file contents.

Important APIs and types: `ContentEnc` owns a `cryptocore.CryptoCore`, block sizes, zero-block sentinels, and buffer pools. Key functions include `New`, `PlainBS`, `CipherBS`, `DecryptBlocks`, `DecryptBlock`, `EncryptBlocks`, `EncryptBlock`, `EncryptBlockNonce`, `MergeBlocks`, `Wipe`, `concatAD`, and internal parallel encryption helpers.

Control flow and state: Encryption prepends a random or caller-supplied nonce and authenticates block number plus file ID as associated data. Decryption handles empty blocks, all-zero sparse holes, nonce extraction, all-zero nonce rejection, AEAD open, and pooled buffers. Large writes may be split across goroutines.

Dependencies and integration points: Used by file I/O, config key wrapping, symlink/xattr crypto, fsck, and tests. Depends on FUSE max write size and crypto backends.

Risks and test signals: Security risks include nonce misuse, wrong associated data, buffer reuse bugs, and sparse-hole handling. Signals include encrypt/decrypt round trips, tamper failures, block split/merge tests, and AESSIV nonce restrictions.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/content.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/content_test.go -->
# sources/security-integrity/gocryptfs/internal/contentenc/content_test.go

Purpose: This test file validates content encryption offset/range logic, block splitting, encryption/decryption behavior, and merge semantics.

Important APIs and functions: Tests exercise range splitting helpers, `EncryptBlock`, `DecryptBlock`, `EncryptBlocks`, `DecryptBlocks`, `MergeBlocks`, block overhead/size conversions, and corrupted or special-case inputs.

Control flow and state: Tests create crypto cores/content encoders, encrypt plaintext blocks, decrypt them, compare output, and assert error behavior for tampering or malformed ciphertext.

Dependencies and integration points: Protects the core file data path used by mounted gocryptfs and fsck.

Risks and test signals: These tests are critical because block numbering and file ID AD must match between read and write. Signals include exact plaintext recovery, sparse zero-block behavior, wrong-block or wrong-file authentication failures, and range boundary correctness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/content_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/file_header.go -->
# sources/security-integrity/gocryptfs/internal/contentenc/file_header.go

Purpose: This file defines the per-file content header format used to bind encrypted blocks to a random file ID.

Important APIs and types: Constants define header version, ID length, and total header length. `FileHeader` stores version and ID. `Pack` serializes the header, `ParseHeader` validates and parses bytes, and `RandomHeader` creates a new header with random ID.

Control flow and state: Nonempty encrypted files persist the header before content blocks. Parsing rejects wrong lengths, unsupported versions, all-zero IDs, and all-zero headers where appropriate.

Dependencies and integration points: File IDs feed `content.go` associated data, preventing block swapping across files. Used by file I/O and fsck.

Risks and test signals: Header corruption must be detected cleanly. Risks include accepting zero IDs or version mismatch. Signals are parse/pack round trips, random ID length, and rejection tests for malformed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/file_header.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/intrablock.go -->
# sources/security-integrity/gocryptfs/internal/contentenc/intrablock.go

Purpose: This file implements conversions between plaintext offsets/ranges and cipher block ranges within gocryptfs files.

Important APIs and functions: It provides helpers to split a byte range into block number, intra-block offset, skip, and length components, plus conversions between plaintext and ciphertext sizes/offsets accounting for header and per-block overhead.

Control flow and state: Functions are pure arithmetic over offsets, lengths, block sizes, and overhead. No state is persisted.

Dependencies and integration points: Used by read/write paths, fsck, and tests to map FUSE requests to encrypted block reads/writes.

Risks and test signals: Off-by-one errors can corrupt reads/writes at block boundaries or EOF. Signals include boundary tests for zero length, unaligned ranges, multi-block ranges, and size conversion round trips.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/intrablock.go -->
