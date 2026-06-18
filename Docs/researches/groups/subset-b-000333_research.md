# subset-b-000333 Research

Grouped research for subset `subset-b-000333`. Each section is source-tree aligned and intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/examples/zwrapbench.c -->
# sources/compression/zstd/zlibWrapper/examples/zwrapbench.c

## Purpose
`zwrapbench.c` is a benchmark and validation command-line tool for comparing native Zstandard, native zlib, and the Zstandard zlib wrapper under multiple usage styles. It can benchmark synthetic data or one or more input files, optionally with a dictionary, and reports compression ratio plus compression/decompression speed.

## Important APIs, Types, and Functions
The file defines `blockParam_t` to track each independently compressed block and `BMK_compressor` to select benchmark mode: native `ZSTD_CCtx`, native `ZSTD_CStream`, native zlib, zlib through the wrapper, and context-reuse variants. `BMK_benchMem()` is the central benchmark loop. `BMK_benchCLevel()` runs the selected level range across all implementations. `BMK_loadFiles()`, `BMK_benchFileTable()`, and `BMK_syntheticTest()` prepare inputs. `main()` parses flags including `-D`, `-b`, `-e`, `-i`, `-B`, verbosity, and recursion when file-list support is compiled in.

## Control Flow
`main()` builds the file table, dictionary path, compression level range, block size, and run duration, then calls `BMK_benchFiles()`. File mode loads inputs into a bounded memory buffer; synthetic mode generates random data with `RDG_genBuffer()`. `BMK_benchCLevel()` then iterates through compressor families. `BMK_benchMem()` splits inputs into blocks, allocates compressed and regenerated buffers, repeatedly compresses blocks until the timing window closes, then repeatedly decompresses and checks the regenerated buffer with `XXH64`.

## State and Persistence
Global state controls display level, block size, iteration duration, compressibility, and hidden additional parameters. The benchmark keeps all test data in memory and writes no benchmark outputs other than terminal output. It mutates the wrapper's process-global switches via `ZWRAP_useZSTDcompression()` and `ZWRAP_setDecompressionType()`, so benchmark modes are process-global rather than thread-local.

## Dependencies and Integration Points
The tool depends on Zstandard internals (`ZSTD_STATIC_LINKING_ONLY`), zlib API calls from the wrapper header, `datagen`, `xxhash`, `timefn`, and local utility helpers. It is an integration exercise for `zstd_zlibwrapper.c`: wrapper modes call normal `deflate*()` and `inflate*()` entry points after toggling wrapper behavior.

## Risks
The benchmark assumes in-memory workloads and may reduce input size when memory is unavailable, which can make large-file results less representative. The wrapper toggles are not thread-safe, although this tool is single-threaded. Dictionary reuse paths intentionally change behavior after the first block for wrapper/ZSTD modes, so comparisons should be read as specific API-usage scenarios rather than pure codec comparisons. `while (!cCompleted | !dCompleted)` uses bitwise OR on booleans, which works but is easy to misread.

## Test Signals
The strongest built-in test signal is checksum validation after decompression. It also tests dictionary paths, stream and one-shot ZSTD APIs, zlib and wrapper deflate/inflate APIs, context creation/reset/reuse, block sizing, file loading, and synthetic data generation.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/examples/zwrapbench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzclose.c -->
# sources/compression/zstd/zlibWrapper/gzclose.c

## Purpose
`gzclose.c` provides the public `gzclose()` dispatcher for gzip-style file handles in the zlib wrapper. It is kept separate so programs that explicitly use `gzclose_r()` or `gzclose_w()` can avoid linking unneeded read or write code.

## Important APIs, Types, and Functions
The only exported function is `gzclose(gzFile file)`. It uses the `gz_statep` union from `gzguts.h` to reinterpret the public `gzFile` as internal `gz_state`. Depending on `state.state->mode`, it dispatches to `gzclose_r()` for `GZ_READ` or `gzclose_w()` otherwise, unless `NO_GZCOMPRESS` forces read-only behavior.

## Control Flow
The function rejects `NULL` with `Z_STREAM_ERROR`. With compression enabled, it reads the internal mode and delegates to the read or write close path. With compression disabled, it always calls `gzclose_r()`.

## State and Persistence
This file owns no persistent state. It triggers cleanup in the delegated close routines, including stream finalization, buffer release, path-message release, descriptor close, and `gz_state` free.

## Dependencies and Integration Points
It includes `gzguts.h`, which brings in wrapper-aware zlib declarations and the internal gzip state definition. It integrates the read implementation in `gzread.c` and write implementation in `gzwrite.c`.

## Risks
If a `gzFile` has corrupted mode state or is not actually a wrapper `gz_state`, dispatch can call the wrong close path. The function intentionally treats any non-read mode as write mode when compression is enabled, relying on `gzclose_w()` to validate `GZ_WRITE`.

## Test Signals
Coverage should include closing read handles, write handles, `NULL`, invalid mode handles, and builds with `NO_GZCOMPRESS`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzclose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzcompatibility.h -->
# sources/compression/zstd/zlibWrapper/gzcompatibility.h

## Purpose
`gzcompatibility.h` supplies compatibility declarations and type definitions for older zlib versions used by the wrapper's copied `gz*` implementation.

## Important APIs, Types, and Functions
For zlib versions at or below specific `ZLIB_VERNUM` thresholds, it declares `gzclose_r()`, `gzclose_w()`, `gzbuffer()`, `gzoffset()`, `gzopen_w()`, `gzfread()`, and `gzfwrite()`. It also defines `z_off64_t` where absent and provides the older public `struct gzFile_s` layout with `have`, `next`, and `pos`.

## Control Flow
This header is entirely preprocessor-driven. Feature availability is selected by zlib version and platform macros such as `_WIN32`, `Z_LARGE64`, `Z_SOLO`, `NO_SIZE_T`, and `STDC`.

## State and Persistence
It owns no runtime state. Its declarations affect ABI compatibility and source compilation for the gzip wrapper modules.

## Dependencies and Integration Points
The header is included by `gzguts.h` after `zstd_zlibwrapper.h`. It bridges the wrapper's internal `gz_state` layout to public zlib declarations, especially for versions before zlib 1.2.11 where `z_size_t` and newer `gzf*` APIs may not exist.

## Risks
The primary risk is ABI drift across zlib versions: incorrect conditional declarations could conflict with system zlib headers or expose a mismatched `gzFile_s`. The `z_off64_t` fallback also depends on platform large-file conventions.

## Test Signals
Build matrix coverage against older and newer zlib versions is the key signal. Tests should compile both Windows and non-Windows variants and exercise `gzfread`, `gzfwrite`, wide-path open, offsets, and close variants where provided by compatibility declarations.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzcompatibility.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzguts.h -->
# sources/compression/zstd/zlibWrapper/gzguts.h

## Purpose
`gzguts.h` is the internal header for the wrapper's zlib-derived `gz*` file implementation. It centralizes platform compatibility, gzip state layout, constants, and helper declarations.

## Important APIs, Types, and Functions
The key internal type is `gz_state`, which embeds the public `gzFile_s` fields, file descriptor, path, buffers, direct/copy/decompress state, position, error information, and an in-place `z_stream`. `gz_statep` is a union of `gz_state *` and `gzFile`, a wrapper-specific change to reduce strict-aliasing issues. Constants define modes (`GZ_READ`, `GZ_WRITE`, `GZ_APPEND`) and read states (`LOOK`, `COPY`, `GZIP`). Shared declarations include `gz_error()` and Windows CE `gz_strwinerror()`.

## Control Flow
The header has no runtime flow but shapes all runtime flow in `gzlib.c`, `gzread.c`, `gzwrite.c`, and `gzclose.c`. Platform preprocessor branches select file APIs, large-file seek behavior, Windows wide-char support, snprintf/vsnprintf workarounds, and error-string sources.

## State and Persistence
`gz_state` is the persistent state for each `gzFile`. It tracks both compressed file offset via descriptor and uncompressed position via `x.pos`, pending seeks via `seek` and `skip`, read progression via `how`, `eof`, and `past`, and write behavior via compression `level` and `strategy`.

## Dependencies and Integration Points
Unlike upstream zlib, this header includes `zstd_zlibwrapper.h` instead of `zlib.h`, so `inflate` and `deflate` calls can resolve through wrapper symbols. It also includes `gzcompatibility.h` for older zlib interfaces and system headers for descriptors and errors.

## Risks
The internal state is tightly coupled to zlib's `gzFile` ABI and macro expectations. Any mismatch in `gz_statep` use can produce aliasing or invalid pointer behavior. File offset behavior depends on large-file macros being set before system headers. The direct/copy/gzip state machine must remain synchronized with `gzread.c`.

## Test Signals
Useful signals include builds across zlib versions and platforms, large-file seek/tell/offset tests, transparent reads, gzip/ZSTD reads, write modes, append mode, Windows wide-character paths, and strict-aliasing builds.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzguts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzlib.c -->
# sources/compression/zstd/zlibWrapper/gzlib.c

## Purpose
`gzlib.c` implements gzip file functions common to read and write paths: opening, buffering policy, seeking/telling, offset reporting, EOF/error handling, and shared error-message construction.

## Important APIs, Types, and Functions
Important functions include `gz_open()`, `gzopen()`, `gzopen64()`, `gzdopen()`, optional `gzopen_w()`, `gzbuffer()`, `gzrewind()`, `gzseek64()`, `gzseek()`, `gztell64()`, `gztell()`, `gzoffset64()`, `gzoffset()`, `gzeof()`, `gzerror()`, `gzclearerr()`, and internal `gz_error()`. `gz_reset()` initializes common read/write stream state.

## Control Flow
`gz_open()` validates path input, allocates `gz_state`, parses the mode string, opens a path or accepts an existing descriptor, records the read start offset, and calls `gz_reset()`. `gzseek64()` normalizes seek requests into a forward skip when possible, rewinds for backward reads, performs raw file seeks for transparent reads, and otherwise records a pending skip for the next read/write call. Error accessors read and clear `state.state->err` and `state.state->msg`.

## State and Persistence
The file owns creation and initialization of the per-handle `gz_state`. It records path strings for diagnostics, current uncompressed position, requested buffer size, mode, compression parameters, direct flag, file descriptor, and pending seek. It persists errors as allocated messages prefixed with the path.

## Dependencies and Integration Points
It depends on descriptor APIs (`open`, `lseek`/`lseek64`, `_wopen` on Windows), `gzguts.h`, and the read/write modules that consume initialized state. The wrapper integration is indirect through the included wrapper header and through later `inflate`/`deflate` calls in read/write code.

## Risks
Mode parsing ignores unknown flags, which preserves zlib behavior but can hide user mistakes. `gzbuffer()` must be called before buffer allocation. Seek semantics on compressed streams are implemented by skipping uncompressed data, so backward seeks can be expensive. Error-message allocation can convert an original error into `Z_MEM_ERROR`.

## Test Signals
Tests should cover all open modes, descriptor opens, append offset behavior, buffer sizing before/after initialization, rewind, forward/backward seeks, transparent reads, compressed reads, write seek zero-fill behavior through downstream code, error retrieval, and clearerr behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzread.c -->
# sources/compression/zstd/zlibWrapper/gzread.c

## Purpose
`gzread.c` implements the read side of zlib-style `gzFile` access for the wrapper, including transparent file reads, gzip/ZSTD header detection, decompression, seeking-by-skipping, character reads, line reads, pushback, direct-mode detection, and read-close cleanup.

## Important APIs, Types, and Functions
Internal functions are `gz_load()`, `gz_avail()`, `gz_look()`, `gz_decomp()`, `gz_fetch()`, `gz_skip()`, and `gz_read()`. Public functions include `gzread()`, `gzfread()`, `gzgetc()`, `gzgetc_()`, `gzungetc()`, `gzgets()`, `gzdirect()`, and `gzclose_r()`.

## Control Flow
Reads start with `gz_read()`, which honors pending seeks, copies existing output, fetches more output, or decompresses directly into large user buffers. `gz_fetch()` drives the `LOOK`/`COPY`/`GZIP` state machine. `gz_look()` allocates buffers and initializes an inflate stream on first use, reads enough input to inspect magic bytes, then enters compressed mode for gzip magic `1f 8b` or ZSTD magic prefix `28 b5`, transparent copy mode for plain input, or EOF/trailing-garbage handling. `gz_decomp()` loops through `inflate()`, translating zlib return codes into `gz_error()` state.

## State and Persistence
Read state is stored in `gz_state`: input buffer, double-sized output buffer, `how`, `direct`, `eof`, `past`, `x.have`, `x.next`, `x.pos`, and the embedded `z_stream`. `gzungetc()` mutates output-buffer state and position to allow pushback. `gzclose_r()` frees buffers, ends inflate state, closes the descriptor, and frees the handle.

## Dependencies and Integration Points
Because `gzguts.h` includes `zstd_zlibwrapper.h`, calls to `inflateInit2()`, `inflateReset()`, `inflate()`, and `inflateEnd()` can be wrapper-resolved. `gz_look()` adds a wrapper-specific two-byte ZSTD magic recognition path so `gz*` reads can feed ZSTD frames into the wrapper's inflate implementation.

## Risks
Only the first two bytes of the ZSTD magic are checked at the `gz_look()` level; full confirmation is delegated to wrapper inflate. Partial headers and transparent-mode detection keep upstream zlib tradeoffs, including ambiguity for one-byte gzip-like files. `gzgets()` treats embedded NULs as user responsibility. Direct and compressed state transitions are delicate around concatenated streams and trailing garbage.

## Test Signals
Strong tests include reading gzip, ZSTD, and transparent files; concatenated compressed streams; trailing garbage; short and partial headers; direct reads into large user buffers; `gzgetc`, `gzungetc`, and `gzgets`; seeking forward/backward; EOF and error reporting; and read-close behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzwrite.c -->
# sources/compression/zstd/zlibWrapper/gzwrite.c

## Purpose
`gzwrite.c` implements the write side of `gzFile`, including buffered writes, gzip compression, transparent direct writes, formatted writes, flush/parameter changes, seek-by-zero-fill, and write-close finalization.

## Important APIs, Types, and Functions
Internal functions are `gz_init()`, `gz_comp()`, `gz_zero()`, and `gz_write()`. Public functions include `gzwrite()`, `gzfwrite()`, `gzputc()`, `gzputs()`, `gzvprintf()`, `gzprintf()`, `gzflush()`, `gzsetparams()`, and `gzclose_w()`.

## Control Flow
The first write lazily initializes input and output buffers and, unless transparent mode is requested, initializes `deflateInit2()` with gzip headers (`MAX_WBITS + 16`). `gz_write()` consumes pending seek requests by compressing zero bytes, buffers small writes, and sends large writes directly to `gz_comp()`. `gz_comp()` writes directly when `direct` is true or loops through `deflate()`, flushing full output buffers to the descriptor. `gzclose_w()` handles pending zero-fill, finishes the stream with `Z_FINISH`, frees buffers, ends deflate state, closes the descriptor, and releases the handle.

## State and Persistence
Per-handle write state includes buffers, `x.pos` as the uncompressed offset, compression level/strategy, pending seek/skip, and the embedded `z_stream`. Formatted output uses the double-sized input buffer to reserve room for `vsnprintf()`. There is no on-disk metadata beyond the compressed or direct byte stream written to the descriptor.

## Dependencies and Integration Points
The file uses the wrapper-resolved `deflate*()` family through `gzguts.h`. This means gzip-file writes may use zlib or ZSTD behavior depending on wrapper global compression mode. It also depends on POSIX `write()`/`close()` and the shared `gz_error()`.

## Risks
`gzsetparams()` can call `deflateParams()` after flushing with `Z_BLOCK`; wrapper ZSTD compression reports unsupported block/full flush in its deflate implementation, so changing parameters may behave differently under ZSTD mode. Formatted output has historical zlib compatibility branches with tricky buffer-fit checks. Direct mode bypasses compression but still uses the `gz*` state machine.

## Test Signals
Tests should write compressed and transparent data, close and reopen for verification, exercise small and large writes, `gzputc`, `gzputs`, `gzprintf`, `gzflush`, `gzsetparams`, forward seek zero-fill, write errors, and `gzclose_w()` finalization under both zlib and wrapper-ZSTD modes.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzwrite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/zstd_zlibwrapper.c -->
# sources/compression/zstd/zlibWrapper/zstd_zlibwrapper.c

## Purpose
`zstd_zlibwrapper.c` implements a zlib-compatible API layer that can redirect compression to Zstandard and can auto-detect ZSTD versus zlib streams for decompression. It preserves zlib entry points with a `z_` prefix while delegating unsupported or disabled cases to native zlib.

## Important APIs, Types, and Functions
Compression APIs include `ZWRAP_useZSTDcompression()`, `ZWRAP_isUsingZSTDcompression()`, `z_deflateInit_()`, `z_deflateInit2_()`, `z_deflateSetDictionary()`, `z_deflate()`, `z_deflateEnd()`, `z_deflateBound()`, `z_deflateParams()`, `z_compress()`, `z_compress2()`, and `z_compressBound()`. Decompression APIs include `ZWRAP_setDecompressionType()`, `ZWRAP_getDecompressionType()`, `z_inflateInit_()`, `z_inflateInit2_()`, `z_inflate()`, `z_inflateReset()`, `z_inflateSetDictionary()`, `z_inflateEnd()`, `z_inflateSync()`, and `z_uncompress()`. Internal contexts are `ZWRAP_CCtx` and `ZWRAP_DCtx`.

## Control Flow
Compression is controlled by global `g_ZWRAP_useZSTDcompression`. Disabled mode simply calls zlib. Enabled mode allocates a `ZWRAP_CCtx`, creates a ZSTD stream lazily, initializes parameters from zlib compression level and pledged source size, then maps `deflate()` input/output buffers to `ZSTD_compressStream()`, `ZSTD_flushStream()`, and `ZSTD_endStream()`. Decompression starts in unknown mode unless forced to zlib. `z_inflate()` buffers or inspects the first four bytes; non-ZSTD data initializes native zlib inflate and transfers control, while ZSTD data creates a ZSTD DStream and drives `ZSTD_decompressStream()`.

## State and Persistence
The file maintains process-global switches for compression and decompression mode. Per-stream state is stored in `strm->state` as a wrapper context and decompression stream type is recorded in `strm->reserved`. The compression context tracks `streamEnd`, total input bytes independent of user resets, compression level, pledged size, custom allocator state, ZSTD stream state, and in/out buffers. The decompression context tracks header bytes, error count for dictionary signaling, windowBits/version for zlib fallback, custom memory, and ZSTD stream state.

## Dependencies and Integration Points
It depends on `zlib.h` without `Z_PREFIX` for native fallback and `zstd.h` with `ZSTD_STATIC_LINKING_ONLY` for frame detection, magic numbers, custom memory, and stream parameter APIs. It is the core integration layer used by wrapper consumers and by `gzread.c`/`gzwrite.c`.

## Risks
Global toggles are not thread-safe. Several advanced zlib APIs are unsupported when operating on ZSTD streams and return stream errors with messages. ZSTD decompression returns `Z_NEED_DICT` once on dictionary errors, then errors on repeated failure. The code relies on `z_stream.reserved`, which is not normally application-managed in zlib code. There are debug log format strings that reference a `res` token in arguments where `result` is intended, which would matter if logging macros are enabled. Compression flush modes `Z_FULL_FLUSH`, `Z_BLOCK`, and `Z_TREES` are unsupported in ZSTD mode, affecting consumers that rely on zlib block semantics.

## Test Signals
Essential coverage includes zlib-disabled passthrough, ZSTD-enabled compression, one-shot compress/uncompress, streaming deflate/inflate with small buffers, dictionary set/reset paths, pledged source size, zlib fallback auto-detection, forced-zlib mode, unsupported advanced APIs, custom allocators, and `gz*` integration using ZSTD frames.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/zstd_zlibwrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/zstd_zlibwrapper.h -->
# sources/compression/zstd/zlibWrapper/zstd_zlibwrapper.h

## Purpose
`zstd_zlibwrapper.h` exposes the public control surface for the Zstandard zlib wrapper while including zlib in prefixed mode so wrapper symbols can coexist with native zlib symbols.

## Important APIs, Types, and Functions
The header defines `ZLIB_CONST`, `Z_PREFIX`, and `ZLIB_INTERNAL`, includes `<zlib.h>`, ensures `z_const` and `_Z_OF` compatibility, and declares `zstdVersion()`. Compression controls are `ZWRAP_useZSTDcompression()`, `ZWRAP_isUsingZSTDcompression()`, `ZWRAP_setPledgedSrcSize()`, and `ZWRAP_deflateReset_keepDict()`. Decompression controls include `ZWRAP_decompress_type` with `ZWRAP_FORCE_ZLIB` and `ZWRAP_AUTO`, plus `ZWRAP_setDecompressionType()`, `ZWRAP_getDecompressionType()`, `ZWRAP_isUsingZSTDdecompression()`, and `ZWRAP_inflateReset_keepDict()`.

## Control Flow
The header has no runtime flow, but its macros determine symbol prefixing and internal zlib visibility. Consumers include this header and then call standard zlib-like APIs plus wrapper controls.

## State and Persistence
The header documents that compression and decompression mode controls mutate global runtime state and are not thread-safe. Per-stream effects such as pledged source size and keep-dictionary reset are applied to zlib streams created under wrapper mode.

## Dependencies and Integration Points
It is the public integration point for users of the wrapper, benchmark code, and the copied `gz*` implementation. It depends on zlib types such as `z_streamp` and must be C++ compatible through `extern "C"`.

## Risks
Because `Z_PREFIX` is set before including zlib, callers must understand that symbol names may be prefixed and linked with the wrapper build. `ZLIB_INTERNAL` disables some gz64 functions as a compatibility workaround. Thread-unsafety of global controls is explicitly documented and should be respected by callers.

## Test Signals
Test signals are mostly compile/link coverage: C and C++ inclusion, prefixed zlib symbol resolution, and availability of wrapper control APIs. Runtime tests should verify the documented global switches and stream-specific helper functions.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/zstd_zlibwrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/.github/workflows/build-test-publish.yaml -->
# sources/control-plane/beegfs-csi-driver/.github/workflows/build-test-publish.yaml

## Purpose
This GitHub Actions workflow builds, tests, publishes, signs, end-to-end tests, and cleans up BeeGFS CSI driver and operator container images. It runs on pushes to `master`, version tags, manual dispatch, and pull requests affecting non-documentation paths.

## Important Jobs and Steps
`build-test-and-push-images` checks out the repository, sets up Go, builds multi-arch binaries and `chwrap` tarballs, verifies license notices, runs unit tests, builds/pushes/signs the driver image, installs Operator SDK, builds/tests/generates the operator bundle, builds/pushes/signs the operator image, and publishes a test bundle. `e2e-tests` runs on PRs across Kubernetes 1.29.15 through 1.34.1 and BeeGFS 7.4.6/8.2, deploying direct Kustomize driver manifests and examples. `operator-e2e-tests` runs a similar PR matrix through OLM and a `BeeGFSDriver` custom resource. `cleanup-test-images` prunes old GHCR test packages.

## Control Flow
Image names are selected by event type: PRs publish test images, while non-PR events publish retained images. Docker metadata tags are generated from refs, semver tags, and full commit SHA. Downstream e2e jobs depend on the build job and use the SHA-tagged images. Cleanup runs with `always()` after all test jobs.

## State and Persistence
Persistent state includes GHCR images, image signatures, test bundles, and uploaded scorecard artifacts. The workflow mutates the checked-out deployment overlay during e2e tests to inject secrets, TLS certs, and image replacements. It also creates live Minikube clusters and BeeGFS test deployments during job execution.

## Dependencies and Integration Points
The workflow integrates GitHub Actions, Go, project Makefile targets, release-tools build platform variables, Docker Buildx, GHCR, Cosign secrets, Operator SDK, OLM, Minikube, kubectl, BeeGFS package repositories, test environment YAMLs, examples, and Kubernetes CSI sidecars.

## Risks
Timeouts are tight for multi-arch builds and broad e2e matrices. External dependencies include GHCR, package repositories, Minikube downloads, Operator SDK, OLM, and BeeGFS package availability. Cosign signing depends on configured private key secrets. The cleanup job's bundle package extraction uses `OPERATOR_TEST_IMAGE_NAME` for the bundle variable, which looks like a potential package-name bug because `OPERATOR_TEST_BUNDLE_NAME` exists separately.

## Test Signals
Signals include successful binary builds for amd64/arm64, license and NOTICE verification, Go unit tests, generated-code diff checks, image build/push digest outputs, Cosign signing, direct CSI deployment validation by running example pods, operator scorecard, OLM deployment, and final pod-running checks with debug output on failure.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/.github/workflows/build-test-publish.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/.github/workflows/contributors.yml -->
# sources/control-plane/beegfs-csi-driver/.github/workflows/contributors.yml

## Purpose
This GitHub Actions workflow verifies contributor policy for pull requests. It checks that the PR creator has signed the ThinkParQ CLA and that all commits use approved author and committer names/emails.

## Important Jobs and Steps
The single `verify` job checks out full history, validates the PR user against `vars.APPROVED_CONTRIBUTORS`, and validates commit author/committer identity against `vars.APPROVED_COMMITTERS`, expected as a JSON name-to-email mapping.

## Control Flow
On PR open or synchronize, the workflow fetches the full commit history. It computes commits unique to the PR with `git log origin/$BASE_REF..HEAD`, masks actual author and committer emails, then uses `jq` to look up approved emails by name. Any unknown name or mismatched email sets `EXIT_CODE=1`; after all commits are processed, the job exits with failure if any violation was found.

## State and Persistence
No repository state is persisted. Inputs come from GitHub PR metadata, repository variables, and commit history. Logs emit notices and errors while masking actual commit emails.

## Dependencies and Integration Points
The workflow depends on GitHub Actions checkout, repository variables, Git, and `jq` availability on `ubuntu-latest`. It is a governance gate for PRs before build/test workflows are trusted.

## Risks
The CLA check only validates the PR creator, not all commit authors. The commit identity check indexes by display name, so duplicate approved names would be ambiguous in the JSON map. If `APPROVED_COMMITTERS` is malformed or missing, all lookups fail. Fork PR behavior depends on repository variable availability.

## Test Signals
Useful signals include PRs from allowed and disallowed users, commits with expected and unexpected author/committer pairs, empty PRs, base branch resolution, and log masking behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/.github/workflows/contributors.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/Dockerfile -->
# sources/control-plane/beegfs-csi-driver/Dockerfile

## Purpose
The Dockerfile packages the BeeGFS CSI driver into a minimal distroless static image with prebuilt driver and `chwrap` helper artifacts.

## Important Instructions
It starts from `gcr.io/distroless/static:latest` for the target platform, sets OCI labels, defines `TARGETARCH` and fallback `ARCH`, copies `bin/beegfs-csi-driver$ARCH` to `/beegfs-csi-driver`, adds `bin/chwrap$ARCH.tar` into `/`, prepends `/osutils` to `PATH`, and sets `/beegfs-csi-driver` as the entrypoint.

## Control Flow
There is no build-stage compilation. The Docker build assumes `make all` already created architecture-specific binaries and tarballs under `bin/`. Buildx or release-tools provides the target architecture; the Dockerfile selects the matching prebuilt artifact by suffix.

## State and Persistence
The resulting image contains the driver binary and `/osutils` symlink tree from the tarball. At runtime, `/osutils` commands invoke `chwrap`, which finds and executes host binaries under `/host`.

## Dependencies and Integration Points
This file integrates with the Makefile's `build` and `bin/chwrap.tar` targets, GitHub Actions multi-arch buildx configuration, CSI deployment manifests that mount `/host`, and the `cmd/chwrap` program.

## Risks
Using `distroless/static:latest` makes base-image content time-dependent. A missing or mis-suffixed binary/tarball fails the build. Runtime command behavior depends on `/host` being mounted and `/osutils` being first in `PATH`. The image itself does not include BeeGFS utilities or common system binaries beyond the wrapper symlinks.

## Test Signals
Signals include local and buildx image builds for amd64/arm64, verifying `/beegfs-csi-driver --version`, inspecting `/osutils`, and running deployment smoke tests that require mount, umount, modprobe, lsmod, touch, and BeeGFS utilities through `chwrap`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/Makefile -->
# sources/control-plane/beegfs-csi-driver/Makefile

## Purpose
The Makefile defines project build, packaging, license, and test behavior around Kubernetes CSI release-tools. It adds BeeGFS-specific multi-arch driver builds and `chwrap` tarball packaging.

## Important Targets and Variables
`CMDS` defaults to `beegfs-csi-driver`; `TEST_GO_FILTER_CMD` excludes e2e and operator tests from normal unit tests. `all` runs build, `build-chwrap`, and `bin/chwrap.tar`. `check-go-version` verifies installed Go matches `go.mod`. `generate-notices` and `test-licenses` use `go-licenses`. `build-%` builds a named command for each `BUILD_PLATFORMS` entry. `bin/chwrap.tar` invokes `cmd/chwrap/chwrap.sh` for each platform. `container`, `push`, and `push-multiarch` connect local artifacts to release-tools behavior. The file includes `release-tools/build.make`.

## Control Flow
Multi-platform targets parse semicolon-separated `BUILD_PLATFORMS` rows into OS, architecture, suffix, and image fields. Each row drives `go build` output naming and `chwrap` tar creation. License testing regenerates `NOTICE.md`, runs a policy check with explicit ignores, then fails if `NOTICE.md` has uncommitted changes.

## State and Persistence
Build outputs are written to `bin/`. `generate-notices` rewrites `NOTICE.md`. Release-tools included targets may produce images and other build artifacts. The Makefile itself does not persist configuration outside outputs.

## Dependencies and Integration Points
It depends on Go, `go tool go-licenses`, repository `release-tools/build.make`, `cmd/chwrap/chwrap.sh`, and Docker/release-tools targets. The Dockerfile expects names produced by this Makefile.

## Risks
The custom `build-%` target depends on `check-go-version-go`, likely provided by release-tools; a missing include would break it. `BUILD_PLATFORMS` must be passed explicitly for correct multi-arch suffixes. License exceptions are policy-sensitive. Unit testing deliberately skips e2e and operator packages, so CI must run those elsewhere.

## Test Signals
Signals include `make check-go-version`, `make all` with single and multi-platform settings, `make test-licenses`, normal `make test`, image build targets, and CI generated-code/notice checks.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/cmd/beegfs-csi-driver/main.go -->
# sources/control-plane/beegfs-csi-driver/cmd/beegfs-csi-driver/main.go

## Purpose
This is the executable entry point for the BeeGFS CSI driver process. It parses command-line flags, prints version information when requested, constructs the driver, and starts it.

## Important APIs, Types, and Functions
Flags configure connection auth path, TLS cert path, plugin config path, controller-service data directory, CSI driver name, CSI endpoint, node ID, version output, client config template path, and node-unstage timeout. `main()` initializes klog, sets `logtostderr`, parses flags, handles `--version`, and delegates to `handle()`. `handle()` calls `beegfs.NewBeegfsDriver()` and then `driver.Run()`.

## Control Flow
Startup is linear. Failure to set klog flags or initialize the driver exits through `beegfs.LogFatal()`. Successful initialization blocks in `driver.Run()`. Version mode prints the executable basename and build-provided version string, then returns without starting the driver.

## State and Persistence
The file itself persists no state. It passes `cs-data-dir` to the driver, which is used by controller service logic for client configuration and mounts. The build process injects `version`.

## Dependencies and Integration Points
It depends on `github.com/netapp/beegfs-csi-driver/pkg/beegfs`, standard flags, and klog. Kubernetes manifests pass these flags to controller and node containers, and the Makefile injects linker flags through release-tools.

## Risks
Default endpoint is `unix://tmp/csi.sock`, while deployment manifests override it with `/csi/csi.sock`; local runs must set an appropriate endpoint. Empty `node-id` may be invalid for node service behavior depending on driver internals. Fatal logging makes startup errors process-terminating.

## Test Signals
Signals include `--version`, flag parsing, `NewBeegfsDriver()` construction tests in package code, deployment smoke tests that verify the CSI socket is created, and Kubernetes sidecar connectivity.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/cmd/beegfs-csi-driver/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/cmd/chwrap/chwrap.sh -->
# sources/control-plane/beegfs-csi-driver/cmd/chwrap/chwrap.sh

## Purpose
`chwrap.sh` builds a tarball containing the `chwrap` binary plus symlinks for host commands that the driver may need inside the container.

## Important APIs, Types, and Functions
This shell script expects three arguments: the source `chwrap` binary, output tar path, and destination directory name. It creates a temporary prefix with `uuidgen`, copies the binary as `$3/chwrap`, symlinks `beegfs`, `beegfs-ctl`, `lsmod`, `modprobe`, `mount`, `touch`, and `umount` to `chwrap`, archives the directory with root owner/group, and removes the temporary tree.

## Control Flow
The script exits immediately on errors (`#!/bin/sh -e`) and rejects missing arguments. It performs create/copy/link/tar/cleanup in sequence.

## State and Persistence
Persistent output is only the requested tarball. Temporary state is created under `/tmp/<uuid>` and removed at the end on the normal path.

## Dependencies and Integration Points
It depends on `uuidgen`, `mkdir`, `cp`, `ln`, `tar`, and `rm`. The Makefile calls it to create `bin/chwrap*.tar`, and the Dockerfile adds that tarball into the image so `/osutils` contains the symlinked commands.

## Risks
If any command fails before cleanup, the temporary directory may remain because there is no trap. The symlink list must stay aligned with driver runtime needs. Argument values are unquoted in a few path positions (`$PREFIX/$3`), so unusual destination names with spaces would be unsafe, though Makefile usage uses `osutils`.

## Test Signals
Signals include invoking the script with a built `chwrap`, inspecting the tar contents and ownership, extracting into a test root, and confirming each symlink resolves to `chwrap`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/cmd/chwrap/chwrap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/cmd/chwrap/main.go -->
# sources/control-plane/beegfs-csi-driver/cmd/chwrap/main.go

## Purpose
`chwrap` is a small helper executable used through symlinks inside the CSI driver container to execute host-installed commands from a `/host` chroot.

## Important APIs, Types, and Functions
`validBinary()` uses `unix.Lstat()` to accept readable/executable regular files or symlinks. `findBinary()` searches host paths for the invoked binary, prioritizing plugin-owned BeeGFS client utilities under `/var/lib/kubelet/plugins/beegfs.csi.netapp.com/client/`, then `/usr/local`, `/usr`, and root-level `sbin`/`bin`. `modifyEnv()` replaces `PATH` with a host-appropriate path. `main()` derives the command name from `argv[0]`, locates it under `/host`, chroots to `/host`, changes directory to `/`, and `exec`s the host command.

## Control Flow
The program is normally invoked as a symlink named `mount`, `umount`, `beegfs`, or similar. It strips path prefixes from `argv[0]`, searches `/host`, exits 127 if not found, performs `chroot("/host")`, `chdir("/")`, and then replaces itself with the intended host command using the original argv.

## State and Persistence
It persists no state. It changes process root and environment before exec. The host command may persist state depending on the command invoked.

## Dependencies and Integration Points
It depends on `golang.org/x/sys/unix`, the container having `/host` mounted to the node filesystem, and the Dockerfile placing symlinked commands earlier in `PATH`. CSI controller and node manifests mount `/host` and use privileged containers to make this possible.

## Risks
The wrapper intentionally executes host binaries from a privileged container, so path search order is security-sensitive. `validBinary()` accepts symlinks if readable/executable bits allow, which is needed for absolute host symlinks but expands trust to host filesystem links. `panic()` on chroot/chdir/exec failure can expose stack traces.

## Test Signals
Tests should cover binary search order, symlink handling via `Lstat`, PATH replacement, command-not-found exit code 127, and integration in a container with `/host` mounted.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/cmd/chwrap/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-controller.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-controller.yaml

## Purpose
This base manifest defines the controller-service `StatefulSet` for the BeeGFS CSI driver deployment.

## Important Objects and Fields
The `StatefulSet` is named `csi-beegfs-controller`, has one replica, uses service account `csi-beegfs-controller-sa`, runs on host networking, tolerates master scheduling, and contains `csi-provisioner`, `csi-resizer`, and `beegfs` containers. The driver args specify driver name, node ID from `spec.nodeName`, CSI socket endpoint, controller data directory, config/connauth/TLS file paths, node-unstage timeout, and log level.

## Control Flow
At runtime sidecars connect to `/csi/csi.sock` exposed by the privileged `beegfs` container. The controller container mounts config and secret projections, `/host` read-only with bidirectional propagation for wrapped commands, and the plugin directory with host-to-container propagation for mountpoint inspection.

## State and Persistence
Persistent host state is under `/var/lib/kubelet/plugins/beegfs.csi.netapp.com`, shared with node service semantics. The StatefulSet uses `emptyDir` for the controller socket directory and generated ConfigMap/Secret volumes for configuration.

## Dependencies and Integration Points
It integrates the driver image, Kubernetes CSI provisioner and resizer sidecars, generated ConfigMap/Secret names, `chwrap` host execution through `/host`, RBAC service accounts, and operator code that expects stable container names and volume resource names.

## Risks
Privileged host-networked containers with host root mounted are high-trust. The `/host` mount is read-only but bidirectional mount propagation is still powerful. Sidecars are privileged for SELinux socket access. Config and secret names are intended for Kustomize hashing, so raw base application without generators may fail.

## Test Signals
Signals include `kubectl apply -k` deployment, sidecar connection to CSI socket, volume provisioning/resizing, controller pod scheduling on master-capable nodes, operator `deploy_test.go` container-name checks, and e2e example pod creation.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-driverinfo.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-driverinfo.yaml

## Purpose
This manifest defines the Kubernetes `CSIDriver` object for BeeGFS CSI.

## Important Objects and Fields
The `CSIDriver` name is `beegfs.csi.netapp.com`. `attachRequired: false` indicates the driver does not require controller publish/attach operations. `fsGroupPolicy: None` declares no Kubernetes fsGroup ownership management. `volumeLifecycleModes` lists `Persistent`.

## Control Flow
The object informs Kubernetes storage behavior rather than running containers. Kubelet and controller components use it to understand attach and lifecycle capabilities for the driver name.

## State and Persistence
The object is persisted in the Kubernetes API server. It has no local filesystem state.

## Dependencies and Integration Points
It is included in base Kustomize resources and embedded in Go via `deploy.go` for operator deployments. Comments mention version overlays may remove `fsGroupPolicy` for Kubernetes 1.18 validation compatibility.

## Risks
Changing the driver name breaks StorageClass/PV references and sidecar registration expectations. Keeping `fsGroupPolicy` in versions that reject the field requires correct version-specific Kustomize patches.

## Test Signals
Signals include strict unmarshal through `GetCSIDriver()`, `kubectl apply` against supported Kubernetes versions, CSI node registration, and successful persistent volume lifecycle tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-node.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-node.yaml

## Purpose
This base manifest defines the node-service `DaemonSet` that runs the BeeGFS CSI node plugin on every selected Kubernetes node.

## Important Objects and Fields
The `DaemonSet` is named `csi-beegfs-node`, uses service account `csi-beegfs-node-sa`, host networking, and containers `node-driver-registrar`, `beegfs`, and `liveness-probe`. The driver exposes health port 9898, connects to `unix://csi/csi.sock`, reads config/connauth/TLS files, and receives node ID from `spec.nodeName`.

## Control Flow
The driver container creates the CSI socket under the host plugin directory. `node-driver-registrar` registers that socket path with kubelet through `/var/lib/kubelet/plugins_registry`. `liveness-probe` checks the CSI socket over `/csi` and exposes health over port 9898.

## State and Persistence
Host-mounted state includes `/var/lib/kubelet/pods`, `/var/lib/kubelet/plugins/kubernetes.io/csi`, `/var/lib/kubelet/plugins_registry`, and `/var/lib/kubelet/plugins/beegfs.csi.netapp.com`. These mounts let the driver inspect mountpoints, publish volumes, and register with kubelet.

## Dependencies and Integration Points
It integrates with Kubelet CSI registration, CSI livenessprobe, generated config/secrets, `chwrap` host command execution via `/host`, and operator expectations for stable container and volume names.

## Risks
The DaemonSet requires privileged containers, host networking, host root visibility, and mount propagation. Host port 9898 must be free on every node. Registration directory type is `Directory`, not `DirectoryOrCreate`, assuming kubelet has created it. Config/secret generators must be applied for named volumes.

## Test Signals
Signals include daemon pod readiness on all nodes, socket registration in kubelet, liveness endpoint success, mount/unmount operations, e2e example pod startup, and `deploy_test.go` checks for stable containers and volume resource references.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-rbac.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-rbac.yaml

## Purpose
This base manifest defines service accounts and RBAC needed by the BeeGFS CSI controller and node services, including an OpenShift SCC role.

## Important Objects and Fields
It creates `csi-beegfs-controller-sa` and `csi-beegfs-node-sa`. The `csi-beegfs-provisioner-role` ClusterRole grants PV/PVC/storageclass/event/csinode/node/pod access and PVC status patching. `csi-beegfs-provisioner-binding` binds that role to the controller service account. The namespaced `csi-beegfs-privileged-scc-role` allows use of OpenShift `privileged` SCC, and its RoleBinding grants that use to both controller and node service accounts.

## Control Flow
Kubernetes authorizes sidecars and the driver based on these bindings. The provisioner sidecar needs cluster-level storage object access, and OpenShift deployments need SCC use before privileged host-network pods can start.

## State and Persistence
The resources persist in the Kubernetes API server. They do not create local filesystem state.

## Dependencies and Integration Points
`deploy.go` embeds and parses this multi-document YAML with `GetRBAC()`. Kustomize includes it in bases, and operator logic consumes the typed objects returned by the deploy package.

## Risks
RBAC permissions are broad enough for provisioning and eventing and should be reviewed when sidecar versions change. The OpenShift SCC role is harmless on non-OpenShift only if the API server tolerates unknown API groups in RBAC rules, which Kubernetes does. Document splitting in `GetRBAC()` depends on each document containing recognizable `kind` text.

## Test Signals
Signals include strict unmarshal of all RBAC documents, controller provisioning success, OpenShift pod admission, and CI/unit tests that assert only expected RBAC object types are returned.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/kustomization.yaml

## Purpose
This Kustomize base lists the core BeeGFS CSI deployment resources.

## Important Objects and Fields
The Kustomization uses `apiVersion: kustomize.config.k8s.io/v1beta1` and includes controller StatefulSet, RBAC, CSIDriver, and node DaemonSet resources.

## Control Flow
Kustomize consumers include this base directly or through version/overlay layers. It provides no transformations itself.

## State and Persistence
No runtime state is owned by this file. Applying the rendered Kustomize output creates the listed Kubernetes objects.

## Dependencies and Integration Points
It integrates the base manifests for user overlays and version-specific overlays referenced by default overlays. Any added base resource should be considered for `deploy.go` embedding if the operator also needs it.

## Risks
Missing resources here will be absent from Kustomize deployments even if embedded in operator code. Conversely, resources added here but not embedded may diverge operator and direct deployment behavior.

## Test Signals
Signals include `kubectl kustomize` or `kubectl apply -k` on overlays, direct base rendering, and comparison with operator embedded resources.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/deploy.go -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/deploy.go

## Purpose
`deploy.go` embeds base Kubernetes manifests and exposes typed accessors so Go code, especially the operator, can instantiate the same objects used by Kustomize deployments.

## Important APIs, Types, and Functions
`//go:embed` captures controller, CSIDriver, node, and RBAC YAML. Constants define expected container names, resource names, and keys: `beegfs`, `node-driver-registrar`, `csi-provisioner`, `csi-resizer`, `liveness-probe`, `csi-beegfs-config`, `csi-beegfs-connauth`, `csi-beegfs-tlscerts`, and their file keys. Accessors are `GetRBAC()`, `GetControllerServiceStatefulSet()`, `GetCSIDriver()`, and `GetNodeServiceDaemonSet()`.

## Control Flow
`GetRBAC()` splits the multi-document RBAC manifest on `---`, detects object kind by byte containment, strictly unmarshals each document into the corresponding Kubernetes API type, and returns a slice of interfaces. Other accessors strictly unmarshal single YAML documents into typed objects.

## State and Persistence
Embedded YAML bytes are compile-time state in the binary. The functions allocate typed Kubernetes objects but do not persist them; callers decide whether to create/update objects in a cluster.

## Dependencies and Integration Points
The package depends on Go embed, Kubernetes API packages, `sigs.k8s.io/yaml`, and `github.com/pkg/errors`. Operator logic relies on the exported constants and accessors to avoid separately maintaining deployment manifests.

## Risks
Kind detection by substring is simple and can be confused if comments or unexpected documents include matching text. Splitting on raw `---` assumes no document content uses that sequence. Strict unmarshal is good for drift detection but can break builds when Kubernetes API versions change fields. Constant names are intentionally coupled to operator logic.

## Test Signals
`deploy_test.go` verifies RBAC object typing, manifest unmarshalling, expected containers, expected key args, and expected volume resource names. Additional signals include operator reconciliation tests and CI generated-manifest diff checks.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/deploy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/deploy_test.go -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/deploy_test.go

## Purpose
`deploy_test.go` protects the embedded deployment-manifest contract used by the operator and direct deployments.

## Important APIs, Types, and Functions
Tests include `TestGetRBAC()`, `TestGetControllerServiceStatefulSet()`, `TestGetCSIDriver()`, and `TestGetNodeServiceDaemonSet()`. Helpers `testForKeysInContainerArgs()` and `testForResourceNamesInPodVolumes()` validate that config, connection auth, and TLS keys/resource names appear in container args and pod volumes.

## Control Flow
Each test calls the accessor from `deploy.go`, fails on unmarshal errors, and then scans returned Kubernetes objects for expected types or expected names. Container checks ensure operator-sensitive container names exist in controller and node pod specs.

## State and Persistence
The tests create in-memory Kubernetes API objects only. They persist no files or cluster state.

## Dependencies and Integration Points
The file depends on Go testing, Kubernetes API types, and a blank Ginkgo import so normal `go test` tolerates Ginkgo flags. It validates assumptions relied on by operator code that mutates embedded manifests.

## Risks
The tests check presence but not full semantic correctness of manifests. They do not verify resource quantities, security contexts, host paths, sidecar image versions, or all RBAC permissions. String containment in args could pass for stale or commented-like values if args are malformed.

## Test Signals
These are themselves unit-test signals. They should run in normal `make test` and fail if core names, keys, volumes, or object typing change without corresponding operator refactors.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/deploy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-config.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-config.yaml

## Purpose
This default-dev overlay file is the user-editable source for the `csi-beegfs-config` ConfigMap data in development deployments.

## Important Objects and Fields
The file contains comments only by default. Kustomize packages it as `csi-beegfs-config.yaml` within a generated ConfigMap named `csi-beegfs-config`.

## Control Flow
When `kubectl apply -k deploy/k8s/overlays/default-dev` is run, `configMapGenerator` in the overlay reads this file and updates pod volume references with a hashed ConfigMap name.

## State and Persistence
Edited contents persist in Git/worktree and become ConfigMap data in the cluster. Empty/default contents mean the driver runs with no custom configuration.

## Dependencies and Integration Points
The driver containers read `/csi/config/csi-beegfs-config.yaml`. The operator and tests expect this key name. Documentation and examples explain valid configuration content.

## Risks
Invalid YAML or semantically invalid driver config can cause driver startup or runtime failures. Because Kustomize hashes generated ConfigMaps, edits trigger rollout only if workloads reference generated names correctly.

## Test Signals
Signals include rendering the overlay, inspecting generated ConfigMap keys, driver startup logs, and end-to-end deployment with custom config.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-connauth.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-connauth.yaml

## Purpose
This default-dev overlay file is the user-editable source for BeeGFS connection authentication Secret data in development deployments.

## Important Objects and Fields
The file is comments-only by default. Kustomize packages it as `csi-beegfs-connauth.yaml` inside a generated Secret named `csi-beegfs-connauth`.

## Control Flow
The overlay's `secretGenerator` reads this file during Kustomize rendering, creates a hashed Secret, and rewrites pod volume references so the driver sees the file at `/csi/connauth/csi-beegfs-connauth.yaml`.

## State and Persistence
Edited secret content persists in the worktree and in generated Kubernetes Secret data after apply. Default empty content lets the driver deploy without custom connection authentication.

## Dependencies and Integration Points
It integrates with driver flags in controller and node manifests, Kustomize secret generation, BeeGFS authentication configuration, and examples referenced by comments.

## Risks
Secrets committed into this file would be stored in source control. Invalid auth content can prevent mounts or provisioning. Kustomize-generated Secret hashing requires workloads to consume the generated name.

## Test Signals
Signals include Kustomize rendering, Secret key inspection, driver logs for auth parsing, and BeeGFS 7/8 e2e tests that inject connection auth via this path.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-connauth.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-tlscerts.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-tlscerts.yaml

## Purpose
This default-dev overlay file is the user-editable source for BeeGFS TLS certificate Secret data in development deployments.

## Important Objects and Fields
The file is comments-only by default. Kustomize packages it as `csi-beegfs-tlscerts.yaml` inside a generated Secret named `csi-beegfs-tlscerts`.

## Control Flow
During overlay rendering, `secretGenerator` creates a hashed Secret and updates volume references. The driver reads the file through `--tlscerts-path=/csi/tlscerts/csi-beegfs-tlscerts.yaml`.

## State and Persistence
Certificate content persists in the worktree if edited and in Kubernetes Secret data after apply. Empty/default content supports deployments without TLS customization.

## Dependencies and Integration Points
It integrates with BeeGFS 8 TLS support, driver container args, Kustomize secret generation, and e2e workflows that inject TLS certificate test data for BeeGFS 8 direct deployments.

## Risks
Certificate material committed to the repository is sensitive. Invalid certificates can break BeeGFS 8 connectivity. BeeGFS 7 flows should tolerate TLS cert presence according to workflow comments.

## Test Signals
Signals include rendered Secret keys, BeeGFS 8 mount tests with TLS enabled, BeeGFS 7 tests with TLS data present but ignored, and driver config parsing logs.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-tlscerts.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/kustomization.yaml

## Purpose
This Kustomize overlay is a development-oriented deployment profile for BeeGFS CSI, targeting the `default` namespace and local/test image names.

## Important Objects and Fields
It bases on `../../versions/latest`, applies `patches/image-pull-policy.yaml` and `patches/node-affinity.yaml`, generates `csi-beegfs-config`, `csi-beegfs-connauth`, and `csi-beegfs-tlscerts`, and rewrites images. The driver image is rewritten to `beegfs-csi-driver:latest`; sidecar image rewrite entries point to an internal NetApp registry for older `k8s.gcr.io` names.

## Control Flow
Kustomize applies base resources, then strategic merge patches, generators, namespace transformation, and image transformations. Generated ConfigMap/Secret names are hashed and referenced by workloads.

## State and Persistence
Applying this overlay creates resources in the `default` namespace. Config and secret content comes from sibling YAML files. Image references are transformed for development pulls.

## Dependencies and Integration Points
It depends on version overlays under `deploy/k8s/versions/latest`, patch files, generator input files, and locally available images or registries. It is intended for developer workflows rather than release deployment.

## Risks
The sidecar image names use `k8s.gcr.io`, while current bases use `registry.k8s.io`; those transformations may no longer match sidecar images. `imagePullPolicy: Always` can slow local testing if images are not in a reachable registry. No Namespace resource is included, so `namespace: default` assumes it exists.

## Test Signals
Signals include `kubectl kustomize` output, image transform verification, generated config/secret name references, and local dev cluster deployment smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/container-resources.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/container-resources.yaml

## Purpose
This optional development patch is a template for adjusting resource requests and limits on controller and node deployment containers.

## Important Objects and Fields
It contains strategic merge fragments for `StatefulSet/csi-beegfs-controller` and `DaemonSet/csi-beegfs-node`, setting memory limits and CPU/memory requests for `beegfs`, `csi-provisioner`, `node-driver-registrar`, and `liveness-probe`.

## Control Flow
The file is not referenced by default. If uncommented in the overlay Kustomization, Kustomize strategic merge patches matching containers by name and replaces their `resources` fields.

## State and Persistence
No runtime state is created by the file alone. Applying it changes pod specs in the cluster, which can trigger rollouts.

## Dependencies and Integration Points
It depends on stable workload and container names from base manifests. It is a developer customization point and mirrors the production overlay template.

## Risks
The DaemonSet YAML indentation appears inconsistent around the container list, which may make the patch invalid if enabled. Resource values are examples/defaults and may be unsuitable for real workloads. Container name drift will cause patches not to apply.

## Test Signals
Signals include enabling the patch and running `kubectl kustomize`, validating YAML parse success, inspecting rendered resource fields, and observing pod scheduling/admission.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/container-resources.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/image-pull-policy.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/image-pull-policy.yaml

## Purpose
This development patch forces the BeeGFS driver container images to be pulled every time, supporting repeated use of mutable tags such as `latest`.

## Important Objects and Fields
It patches `StatefulSet/csi-beegfs-controller` and `DaemonSet/csi-beegfs-node`, setting `imagePullPolicy: Always` on the `beegfs` container in both workloads.

## Control Flow
The default-dev Kustomization references this patch, so it is applied automatically for development deployments. Kubernetes will pull the driver image for each pod start rather than relying on a cached image.

## State and Persistence
Applying the overlay persists changed pod templates in the cluster. Changing pull policy can trigger rollout when the rendered pod template changes.

## Dependencies and Integration Points
It depends on stable workload and container names. It supports local/CI development workflows that push repeated `latest` or SHA-like tags to a registry.

## Risks
Clusters without registry access or with locally loaded images may fail to start pods because `Always` bypasses convenient cache behavior. It only affects the driver container, not sidecars.

## Test Signals
Signals include rendered YAML inspection, pod event logs showing image pulls, and developer cluster rollout behavior after rebuilding images.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/image-pull-policy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/node-affinity.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/node-affinity.yaml

## Purpose
This development patch sets preferred scheduling for the controller service and provides a commented template for node-service affinity.

## Important Objects and Fields
It patches `StatefulSet/csi-beegfs-controller` with `preferredDuringSchedulingIgnoredDuringExecution` node affinity that prefers nodes with `node-role.kubernetes.io/master` at weight 50. A commented DaemonSet block shows how to add required node affinity.

## Control Flow
The default-dev Kustomization applies this patch. Kubernetes scheduling uses it as a preference, not a hard requirement, for controller pods.

## State and Persistence
Applying the overlay persists affinity in the StatefulSet pod template. It can influence future pod scheduling and rollouts.

## Dependencies and Integration Points
It depends on the controller StatefulSet name and Kubernetes node labels. It mirrors the production default overlay patch.

## Risks
Many clusters now use `node-role.kubernetes.io/control-plane` instead of `master`; the preference may be ineffective. Users may misunderstand the commented DaemonSet block as active policy. Hard affinity additions can prevent DaemonSet scheduling if labels are wrong.

## Test Signals
Signals include rendered pod spec inspection, scheduler placement on labeled nodes, and deployment behavior on clusters with `master`, `control-plane`, or neither label.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/node-affinity.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-config.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-config.yaml

## Purpose
This default overlay file is the user-editable source for production-style `csi-beegfs-config` ConfigMap data.

## Important Objects and Fields
It is comments-only by default and is packaged by Kustomize as the `csi-beegfs-config.yaml` key in a generated ConfigMap named `csi-beegfs-config`.

## Control Flow
Kustomize reads this file through `configMapGenerator`; the driver reads it from `/csi/config/csi-beegfs-config.yaml` in controller and node pods.

## State and Persistence
Edited content persists in the repository/worktree and in the generated Kubernetes ConfigMap after apply. Default empty content supports a no-custom-config deployment.

## Dependencies and Integration Points
It integrates with the default overlay, base pod volume references, driver config parser, documentation, and example config files.

## Risks
Invalid content can break driver startup or runtime behavior. Since this is a production-default overlay file, accidentally committing site-specific config may be undesirable.

## Test Signals
Signals include Kustomize rendering, generated ConfigMap key presence, driver startup logs, and deployment tests with representative custom configuration.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-connauth.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-connauth.yaml

## Purpose
This default overlay file is the user-editable source for BeeGFS connection authentication Secret data in production-style deployments.

## Important Objects and Fields
The file is comments-only by default. Kustomize packages it as the `csi-beegfs-connauth.yaml` key in a generated Secret named `csi-beegfs-connauth`.

## Control Flow
During default overlay rendering, `secretGenerator` creates the Secret and rewrites workload volume references to the hashed generated name. The driver reads the mounted file through the `--connauth-path` argument.

## State and Persistence
Edited auth data persists in the worktree and Kubernetes Secret. Empty default content supports deployments where auth is not configured.

## Dependencies and Integration Points
It integrates with BeeGFS connection authentication, Kustomize, driver flags, documentation, and CI e2e tests that overwrite this file before rendering.

## Risks
Sensitive secret material can be committed if users edit this file directly. Wrong formatting can prevent successful BeeGFS connections. Rollouts depend on generated Secret name propagation.

## Test Signals
Signals include rendered Secret inspection, driver logs, BeeGFS authenticated mount tests, and CI injection of test secrets.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-connauth.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-tlscerts.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-tlscerts.yaml

## Purpose
This default overlay file is the user-editable source for BeeGFS TLS certificate Secret data in production-style deployments.

## Important Objects and Fields
The file is comments-only by default. Kustomize packages it as `csi-beegfs-tlscerts.yaml` in a generated Secret named `csi-beegfs-tlscerts`.

## Control Flow
`secretGenerator` renders the Secret and updates workload volume references. Driver containers read it from `/csi/tlscerts/csi-beegfs-tlscerts.yaml`.

## State and Persistence
Edited certificate data persists in the worktree and Kubernetes Secret. Default content allows deployment without TLS configuration.

## Dependencies and Integration Points
It integrates with BeeGFS 8 TLS support, default overlay deployment, driver args, and CI direct e2e tests that inject TLS certificate data.

## Risks
TLS private or trust material can be accidentally committed. Invalid certificates or mismatched hostnames can break BeeGFS 8 connectivity. Users upgrading from BeeGFS 7 to 8 must coordinate cert content with server/client behavior.

## Test Signals
Signals include rendered Secret keys, BeeGFS 8 TLS e2e mounts, BeeGFS 7 compatibility when TLS data is present, and driver TLS parsing logs.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-tlscerts.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/kustomization.yaml

## Purpose
This is the production-default Kustomize overlay for deploying the BeeGFS CSI driver.

## Important Objects and Fields
It sets namespace `beegfs-csi`, bases on `../../versions/latest`, includes `namespace.yaml`, applies `patches/node-affinity.yaml`, and optionally supports `patches/container-resources.yaml`. It generates `csi-beegfs-config`, `csi-beegfs-connauth`, and `csi-beegfs-tlscerts`. It includes commented image-transform examples for driver and CSI sidecars.

## Control Flow
Rendering applies versioned bases, creates the namespace, applies strategic merge patches, generates hashed ConfigMap/Secret names, and can transform images if users uncomment the section.

## State and Persistence
Applying this overlay creates resources in the `beegfs-csi` namespace and generated config/secret resources with hash suffixes. The namespace object is created by the overlay.

## Dependencies and Integration Points
It depends on version overlays, default config/secret input files, and base manifests. CI direct e2e tests mutate this file by appending image transformations for SHA-tagged test images.

## Risks
The Kustomization uses older `bases` and `patchesStrategicMerge` fields rather than newer `resources`/`patches` style; future Kustomize versions may warn or deprecate them. Users must select compatible version overlays for older Kubernetes clusters. Commented sidecar image examples reference older registry names and may need updates.

## Test Signals
Signals include `kubectl kustomize deploy/k8s/overlays/default`, apply on supported Kubernetes versions, generated hash references, namespace creation, image override behavior, and CI direct e2e deployment.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/namespace.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/namespace.yaml

## Purpose
This manifest creates the default namespace for production-style BeeGFS CSI deployments.

## Important Objects and Fields
It defines a `v1` `Namespace` named `beegfs-csi`. The comment notes the name is subject to Kustomize namespace transformation.

## Control Flow
The default overlay includes this file as a resource. Applying the overlay creates the namespace before namespaced resources are applied.

## State and Persistence
The namespace persists in the Kubernetes API server and scopes namespaced CSI controller/node support resources such as service accounts, roles, role bindings, ConfigMaps, Secrets, StatefulSet, and DaemonSet.

## Dependencies and Integration Points
It integrates with the default overlay's `namespace: beegfs-csi` setting and all namespaced base resources. Cluster-scoped resources such as CSIDriver and ClusterRole are not scoped by it.

## Risks
Changing the namespace affects where service accounts, pods, and generated config/secrets live. Existing deployments may leave resources in the old namespace if not cleaned up.

## Test Signals
Signals include rendered overlay namespace fields, successful namespace creation, and pods/resources appearing under `beegfs-csi`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/namespace.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/patches/container-resources.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/patches/container-resources.yaml

## Purpose
This optional default overlay patch is a template for adjusting resource requests and limits for BeeGFS CSI workloads.

## Important Objects and Fields
It defines strategic merge patches for `StatefulSet/csi-beegfs-controller` and `DaemonSet/csi-beegfs-node`, setting resource defaults for `beegfs`, `csi-provisioner`, `node-driver-registrar`, and `liveness-probe`.

## Control Flow
The file is not applied unless a user adds it to `patchesStrategicMerge` in the overlay Kustomization. Once enabled, Kustomize merges matching container entries by name into the rendered workloads.

## State and Persistence
Applying the patch changes pod templates in the cluster and can trigger rollout. It owns no state when left unreferenced.

## Dependencies and Integration Points
It depends on stable workload/container names from base manifests. It is intended as a user customization starting point.

## Risks
The DaemonSet section has inconsistent indentation around `metadata`, `template`, and container entries; if enabled, YAML parsing or strategic merge may fail. The liveness-probe request in this patch uses CPU `100m`, while the base manifest uses `60m`, so comments that values are defaults are not fully aligned.

## Test Signals
Signals include enabling the patch, running `kubectl kustomize`, verifying rendered resource fields, and observing scheduling/admission with customized limits.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/patches/container-resources.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/patches/node-affinity.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/patches/node-affinity.yaml

## Purpose
This default overlay patch applies a preferred scheduling policy for the controller service and provides a commented template for node-service affinity.

## Important Objects and Fields
It patches `StatefulSet/csi-beegfs-controller` with preferred node affinity for nodes carrying `node-role.kubernetes.io/master`, weighted 50. It also includes commented examples for required node affinity on the controller and DaemonSet.

## Control Flow
The default overlay applies this patch by default. Kubernetes scheduling considers it as a soft preference for controller pod placement.

## State and Persistence
Applied affinity persists in the StatefulSet pod template and affects future scheduling decisions.

## Dependencies and Integration Points
It depends on the controller StatefulSet name and cluster node labels. It is part of the production-default overlay and mirrors the dev overlay.

## Risks
The `master` role label is not universal on modern clusters; many use `node-role.kubernetes.io/control-plane`. Because this is only a preference, it will not block scheduling if labels do not match. Users editing commented hard-affinity examples can accidentally prevent scheduling.

## Test Signals
Signals include rendered affinity inspection, scheduler placement behavior on clusters with relevant labels, and successful controller rollout.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/patches/node-affinity.yaml -->
