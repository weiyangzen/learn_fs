# subset-b-009791 research

Grouped research for rclone library files under encoder, env, errcount, errors, exitcode, file, HTTP serving, race detection, JWT/OAuth, KV, mmap, multipart, and pacer packages. Each section preserves the source path in the title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/encoder_test.go -->
# sources/user-network-fs/rclone/lib/encoder/encoder_test.go

Source read signal: reviewed complete local file (433 lines, sha256 96a87f5e45a09e9b).

Purpose: Exercises the `encoder.MultiEncoder` public contract: flag string parsing, generated encode/decode fixtures, invalid UTF-8 quoting, edge-only rules for dot/space/tilde/control characters, and benchmarks against older map-based replacement helpers.

Important APIs/types/functions: Compile-time assertions verify `MultiEncoder` implements `pflag.Value` and `fmt.Scanner`. `TestEncodeString`, `TestEncodeSet`, `TestEncodeSingleMask`, `TestEncodeSingleMaskEdge`, `TestEncodeDoubleMaskEdge`, `TestEncodeInvalidUnicode`, `TestEncodeDot`, and `TestDecodeHalf` cover user-visible behavior. Local `testCase`, `benchReplace`, `benchRestore`, `replaceReservedChars`, and `restoreReservedChars` support tests and benchmarks.

Control flow: Table-driven tests iterate generated fixtures from `encoder_cases_test.go`, encode each input, compare the expected output, then decode back to the original input. Invalid UTF-8 tests verify quote-rune byte escaping only when the relevant flag is set. Benchmarks compare the current encoder against legacy regex/map behavior for a OneDrive-like mask.

State and persistence behavior: The test file has no persistent state; it builds an inverse character map in `init()` for the legacy benchmark helpers. It depends on generated fixture data and on package globals from the encoder implementation.

Dependencies and integration points: Uses `testing`, `strconv`, `regexp`, `strings`, `pflag`, and `testify/assert`. It integrates with generated encoder cases and protects backend path encodings that rely on `MultiEncoder` flag combinations.

Risks and test signals: The tests are broad but depend on generated cases remaining synchronized with encoder flags. Edge cases include ambiguous quote-rune decoding, invalid UTF-8 byte preservation, only-left/right transforms, and unknown high-bit mask string formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/encoder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/filename/decode.go -->
# sources/user-network-fs/rclone/lib/encoder/filename/decode.go

Source read signal: reviewed complete local file (95 lines, sha256 c75c5a9244ebd972).

Purpose: Decodes compact URL-safe filename encodings produced by the sibling encoder, including uncompressed, SCSU, run-length, predefined Huffman, and custom Huffman-table payloads.

Important APIs/types/functions: Exports `ErrCorrupted`, `ErrUnsupported`, `Decode`, and `DecodeBytes`. Package state includes `customDec` plus `customDecMu` because `huff0.Scratch` is stateful.

Control flow: `Decode` initializes coders, validates the leading table character through `decodeMap`, base64 URL-decodes the remaining payload, then delegates to `DecodeBytes`. `DecodeBytes` switches on the table id: raw bytes return directly, reserved ids report future-version unsupported, SCSU tables call `scsu.Decode`, RLE parses a uvarint count and repeated byte, custom tables read an embedded Huffman table under lock, and predefined tables use `decTables`.

State and persistence behavior: Decoder tables are initialized once by `initCoders`; custom Huffman decode reuses protected scratch memory. No durable state is written.

Dependencies and integration points: Uses `encoding/base64`, `encoding/binary`, `bytes`, `sync`, `scsu`, and `klauspost/compress/huff0`. It is the inverse of `filename.Encode` and is used anywhere rclone needs reversible URL-safe compressed filenames.

Risks and test signals: Corruption handling depends on strict table bounds, base64 validity, uvarint length, `maxLength`, and Huffman errors. Concurrency risk is isolated to the custom decoder lock; tests and fuzzing should continue to cover malformed inputs and all table classes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/filename/decode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/filename/decode_test.go -->
# sources/user-network-fs/rclone/lib/encoder/filename/decode_test.go

Source read signal: reviewed complete local file (147 lines, sha256 fda102fbdb3bd610).

Purpose: Regression-tests decoding of stored compressed filename samples across all supported table classes and checks encode-size regressions.

Important APIs/types/functions: `TestDecode` drives fixtures with `name`, `encoded`, `want`, and `wantErr` fields, calling both `Decode` and `Encode`.

Control flow: Each fixture decodes a known encoded string, compares errors and decoded text, then re-encodes the expected filename and flags any generated encoding longer than the checked-in reference.

State and persistence behavior: No persistent state is used beyond package decoder initialization. The test reads hard-coded payloads representing compatibility data.

Dependencies and integration points: Depends on the package encoder/decoder, predefined Huffman tables, SCSU support, and Go's testing package. It protects compatibility with previously generated filenames from older rclone versions.

Risks and test signals: The test covers raw, long raw, several fixed Huffman tables, custom Huffman, RLE, regular ASCII, and Unicode/SCSU examples. The duplicate `len(proposed) > len(tt.encoded)` branch logs the improvement path only after the same condition already failed, which limits the intended positive diagnostic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/filename/decode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/filename/encode.go -->
# sources/user-network-fs/rclone/lib/encoder/filename/encode.go

Source read signal: reviewed complete local file (85 lines, sha256 fc5f35a1605e4299).

Purpose: Encodes arbitrary byte strings into compact URL-safe filename strings by choosing the smallest available representation.

Important APIs/types/functions: Exports `Encode` and `EncodeBytes`. It uses package tables from `init.go`, SCSU transcoding, `huff0.Compress1X`, RLE fallback, and URL-safe base64.

Control flow: `EncodeBytes` initializes coders, starts with raw bytes as the current best, then walks each configured Huffman table for inputs of length 2 through `maxLength`. For `tableSCSU`, it first tries SCSU and records plain SCSU if smaller. It locks the stateful Huffman scratch for each table, records smaller compressed output, and handles `huff0.ErrUseRLE` by emitting a uvarint count plus repeated byte.

State and persistence behavior: Uses shared table scratch objects protected by `encTableLocks`; no persistent storage is modified. Returned payload slices are built from local copies of the original bytes.

Dependencies and integration points: Depends on `base64`, `binary`, `scsu`, and `huff0`. Its first-character table id is decoded by `Decode`, and the URL-safe output is suitable for remotes that need restricted path components.

Risks and test signals: The algorithm is size-driven, so table ordering and `WantLogLess` affect compatibility/performance. Inputs longer than 256 bytes or length 0/1 bypass compression; repeated-byte RLE must not be emitted for SCSU-transformed data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/filename/encode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/filename/fuzz.go -->
# sources/user-network-fs/rclone/lib/encoder/filename/fuzz.go

Source read signal: reviewed complete local file (35 lines, sha256 a5baec8b589a850b).

Purpose: Provides a go-fuzz harness for the filename encoder/decoder round trip and decoder robustness.

Important APIs/types/functions: The build-tagged `Fuzz(data []byte) int` function calls `Decode` on arbitrary data, then `Encode` and `Decode` on the original byte string.

Control flow: It first attempts to decode arbitrary bytes as a string and ignores result/errors to catch panics. It then encodes the input, decodes the encoded form, and panics if decoding fails or if bytes differ from the original input.

State and persistence behavior: No durable state is used. It exercises shared table initialization and table scratch under fuzz workload.

Dependencies and integration points: Uses `bytes` and `fmt` plus package functions. The `gofuzz` build tag keeps it out of normal builds and documents the `go-fuzz-build` invocation.

Risks and test signals: Strong signal for panic safety and reversibility over invalid UTF-8 byte strings. It does not assert minimal encoded size or distinguish expected corruption errors from unsupported/future table ids.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/filename/fuzz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/filename/gentable.go -->
# sources/user-network-fs/rclone/lib/encoder/filename/gentable.go

Source read signal: reviewed complete local file (129 lines, sha256 6dd62e7c87b4c97e).

Purpose: Build-tagged table generator for Huffman filename compression tables from byte histograms or indexed filename corpora.

Important APIs/types/functions: Command flags include `-index`, `-all`, and `-scsu`. `main` builds a byte histogram, optionally SCSU-encodes input lines, scales frequencies, asks `huff0` to build a table, and prints a base64 table plus sample compression statistics.

Control flow: With `-index`, it reads the file, optionally filters lines that SCSU compresses, counts bytes, and replaces the built-in example histogram. It then scales counts to about 100 KiB, fills a training slice, compresses once with `ReusePolicyNone` to obtain `OutTable`, then recompresses a sample with `ReusePolicyPrefer` for stats.

State and persistence behavior: It only reads optional input and writes generated data to stdout; maintainers manually paste table strings into `init.go`.

Dependencies and integration points: Uses `flag`, `os`, `bufio`, `unicode/utf8`, `scsu`, `huff0`, and `compress.ShannonEntropyBits`. It feeds the runtime filename table data.

Risks and test signals: Because generated tables become compatibility data, corpus choice and `-all` behavior affect future compression/decompression. Division by zero would occur if an indexed corpus produces zero total bytes; generated tables need decode tests before use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/filename/gentable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/filename/init.go -->
# sources/user-network-fs/rclone/lib/encoder/filename/init.go

Source read signal: reviewed complete local file (101 lines, sha256 fc495bf7a5a2cf34).

Purpose: Owns filename compression table ids, URL table character mapping, once-only initialization, and runtime encoder/decoder tables.

Important APIs/types/functions: Defines `encodeURL`, `decodeMap`, `maxLength`, `initOnce`, `encTables`, `encTableLocks`, `decTables`, special table constants, `tablesData`, and `initCoders`.

Control flow: `initCoders` populates `decodeMap`, decodes each non-empty base64 Huffman table, reads it with `huff0.ReadTable`, configures compression preferences, stores encoder scratch and decoder instances, then configures `tableCustom` with a reusable encoder and no fixed decoder.

State and persistence behavior: All state is process-local and initialized exactly once. Encoders are stateful and require per-table locks when used; decoders are treated as stateless except for custom decode scratch in `decode.go`.

Dependencies and integration points: Depends on `base64`, `sync`, and `huff0`. The data table is consumed by `EncodeBytes` and `DecodeBytes`, so table ids are an on-disk/on-remote compatibility surface.

Risks and test signals: Changing table ids or table bytes can break existing encoded filenames. Panics during init indicate invalid checked-in table data; tests should exercise every non-empty table and reserved/custom behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/filename/init.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/internal/gen/main.go -->
# sources/user-network-fs/rclone/lib/encoder/internal/gen/main.go

Source read signal: reviewed complete local file (628 lines, sha256 5e9a6832dfe49fcb).

Purpose: Generates `encoder_cases_test.go`, the large fixture table used to verify `MultiEncoder` encode/decode behavior across masks and edge rules.

Important APIs/types/functions: Uses `mapping`, `edge`, `stringPair`, `maskBits`, `allEdges`, `allMappings`, and helpers `invalidMask`, `runeRange`, `getMapping`, `buildTestString`, `buildEdgeTestString`, `fixEdges`, `runePos`, and `quotedToString`.

Control flow: `main` seeds a deterministic RNG, creates `encoder_cases_test.go`, writes test headers, emits single-mask cases from `allMappings`, emits single-edge cases for left/right edge-only encodings, then emits double-edge combinations excluding invalid control-mask overlaps.

State and persistence behavior: The generator writes one Go source file in the encoder package and otherwise keeps transient RNG and fixture slices in memory.

Dependencies and integration points: Imports `github.com/rclone/rclone/lib/encoder` and `fs.Fatal`, plus `slices`, `rand`, and file I/O. It is invoked by go generate comments in the generated file header and must track encoder flag definitions.

Risks and test signals: Generated cases are the main regression net for flag combinations, quote-rune handling, and edge substitutions. Any new encoder flag needs updates to `maskBits` and, if applicable, `allMappings`/`allEdges`; source duplication or syntax drift in this generator would break fixture regeneration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/internal/gen/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/os_darwin.go -->
# sources/user-network-fs/rclone/lib/encoder/os_darwin.go

Source read signal: reviewed complete local file (9 lines, sha256 fc31921f690fc33d).

Purpose: Selects the local backend filename encoding for macOS builds.

Important APIs/types/functions: Defines build-tagged constant `OS = Base | EncodeInvalidUtf8`.

Control flow: There is no runtime flow; the Go build selects this file on Darwin and consumers use `encoder.OS` as the platform policy.

State and persistence behavior: No state. The constant affects how local paths are encoded before reaching macOS filesystems.

Dependencies and integration points: Depends on constants from the encoder package. It integrates with local backend path normalization and `kv.makeName` through `encoder.OS.FromStandardPath`.

Risks and test signals: The macOS-specific concern is invalid UTF-8 preservation because macOS cannot store arbitrary invalid UTF-8 names. Cross-platform tests should assert `OS` includes `EncodeInvalidUtf8` only where needed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/os_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/os_other.go -->
# sources/user-network-fs/rclone/lib/encoder/os_other.go

Source read signal: reviewed complete local file (6 lines, sha256 b7ce6c47b479484e).

Purpose: Selects the local backend filename encoding for non-Windows, non-macOS platforms.

Important APIs/types/functions: Defines build-tagged constant `OS = Base`.

Control flow: No runtime flow; build constraints select this file for Unix-like platforms other than Darwin.

State and persistence behavior: No state. `Base` encodes zero, slash, and dot policy as defined by `standard.go`.

Dependencies and integration points: Integrates with local filesystem path handling and cache DB naming through the shared `encoder.OS` constant.

Risks and test signals: Platform build tags must exclude Windows and Darwin correctly. Behavior assumes other platforms can carry invalid UTF-8 without the Darwin/Windows escaping policy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/os_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/os_windows.go -->
# sources/user-network-fs/rclone/lib/encoder/os_windows.go

Source read signal: reviewed complete local file (33 lines, sha256 75f62dadc543d117).

Purpose: Selects the local backend filename encoding for Windows builds, reflecting Windows reserved character and trailing-name rules.

Important APIs/types/functions: Defines `OS = Base | EncodeWin | EncodeBackSlash | EncodeCtl | EncodeRightSpace | EncodeRightPeriod | EncodeInvalidUtf8`.

Control flow: No runtime flow; consumers use the constant for platform-specific path conversion.

State and persistence behavior: No state. The constant controls persistent local filenames and must remain compatible with existing encoded paths.

Dependencies and integration points: Depends on encoder flag constants and documents Windows character substitutions and invalid UTF-8 handling before UTF-16 conversion.

Risks and test signals: Omitting a reserved Windows rule can cause create/open failures or name collisions. Tests should verify trailing spaces/periods, control characters, backslash, and invalid UTF-8 behavior on Windows builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/os_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/standard.go -->
# sources/user-network-fs/rclone/lib/encoder/standard.go

Source read signal: reviewed complete local file (21 lines, sha256 c2ad677dd0847be3).

Purpose: Defines shared encoder presets for rclone's standard path representation, base local-safe representation, and display/logging representation.

Important APIs/types/functions: Constants are `Standard`, `Base`, and `Display`.

Control flow: No runtime flow; these bitmasks are consumed by encoder methods and backends.

State and persistence behavior: No mutable state. `Standard` is part of rclone's internal path contract and can affect stored config/cache names or remote paths when used by backends.

Dependencies and integration points: Depends on `MultiEncoder` flags in the same package. Used by OS-specific policies, backend encoders, and display formatting.

Risks and test signals: Changing presets has broad compatibility impact. Tests should continue to assert slash, zero, delete/control, and dot encoding choices for standard paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/standard.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/env/env.go -->
# sources/user-network-fs/rclone/lib/env/env.go

Source read signal: reviewed complete local file (46 lines, sha256 2e886bf3b2592875).

Purpose: Provides small environment helpers for shell-like path expansion and current user detection.

Important APIs/types/functions: Exports `ShellExpandHelp`, `ShellExpand`, and `CurrentUser`.

Control flow: `ShellExpand` expands a leading tilde with `go-homedir` when possible, then runs `os.ExpandEnv`. `CurrentUser` prefers `user.Current`, except when `$USER` is literally `$USER` for documentation generation, then falls back to `$USER` and `$LOGNAME`.

State and persistence behavior: Reads environment variables and OS user info only; no state is written.

Dependencies and integration points: Uses `os`, `os/user`, and `mitchellh/go-homedir`. Help text is embedded in command option descriptions that accept paths.

Risks and test signals: Tilde expansion is intentionally only leading-position. `user.Current` can fail in static/cross/container environments, so fallback ordering matters; env tests cover `~`, embedded `~`, and `${VAR}` expansion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/env/env.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/env/env_test.go -->
# sources/user-network-fs/rclone/lib/env/env_test.go

Source read signal: reviewed complete local file (32 lines, sha256 4ab874ec54b927de).

Purpose: Tests `ShellExpand` path and environment expansion semantics.

Important APIs/types/functions: `TestShellExpand` sets `EXPAND_TEST`, obtains the home directory with `homedir.Dir`, and checks table-driven expected values.

Control flow: The test sets and defers unsetting the environment variable, then compares empty input, bare `~`, leading `~/...`, non-leading `~`, and combined tilde/env expansion.

State and persistence behavior: Temporarily mutates the process environment and uses `t.Temp`-free local state only.

Dependencies and integration points: Uses `filepath.FromSlash` for platform-neutral expectations, `testify/assert`, and `require`.

Risks and test signals: Good coverage for `ShellExpand`; there is no direct test for `CurrentUser`, so fallback behavior remains less protected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/env/env_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/errcount/errcount.go -->
# sources/user-network-fs/rclone/lib/errcount/errcount.go

Source read signal: reviewed complete local file (58 lines, sha256 70ff2e49351470d7).

Purpose: Provides a thread-safe accumulator that reports the number of errors and the last error without flooding users with every failure.

Important APIs/types/functions: Type `ErrCount` holds a mutex, last error, and count. `New`, `Add`, and `Err` are the public API.

Control flow: `Add` ignores nil, then increments count and stores the latest error under lock. `Err` returns nil for no errors, wraps the only error for count one, or formats a summary with count plus last error for multiple failures.

State and persistence behavior: State is in-memory per `ErrCount` instance. Wrapped errors preserve `errors.Is` visibility for the last error.

Dependencies and integration points: Uses `sync` and `fmt`. It is suitable for batch operations that need a final summarized error.

Risks and test signals: Only the last non-nil error is retained, so earlier error identity is intentionally lost. Tests cover nil, single-error wrapping, multi-error count text, and `errors.Is` on the last error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/errcount/errcount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/errcount/errcount_test.go -->
# sources/user-network-fs/rclone/lib/errcount/errcount_test.go

Source read signal: reviewed complete local file (27 lines, sha256 b7c4d25df3c9a63e).

Purpose: Verifies the observable behavior of `ErrCount`.

Important APIs/types/functions: `TestErrCount` uses `New`, `Add`, and `Err` with two sentinel errors.

Control flow: It checks initial nil status, adds one error and validates message/wrapping, then adds a second error and validates count text plus wrapping of the latest error.

State and persistence behavior: No persistent state; all state is inside one `ErrCount`.

Dependencies and integration points: Uses Go `errors`, `testing`, and `testify/assert`.

Risks and test signals: Covers the main API but not concurrent `Add`/`Err` calls; thread-safety relies on the mutex implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/errcount/errcount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/errors/errors.go -->
# sources/user-network-fs/rclone/lib/errors/errors.go

Source read signal: reviewed complete local file (74 lines, sha256 9b93d102a6aebc67).

Purpose: Implements generic traversal of error chains across old `Cause`, modern `Unwrap`, multi-error `Unwrap() []error`, and common stdlib structs with an `Err` field.

Important APIs/types/functions: Public `WalkFunc` and `Walk`; private interfaces `causer`, `wrapper`, and `multiWrapper`.

Control flow: `Walk` invokes the callback for the current error and stops if it returns true. It recursively walks multi-wrapper children, otherwise follows `Cause`, `Unwrap`, or reflectively extracted `Err` fields, breaking if the next error is deeply equal to the previous one.

State and persistence behavior: Stateless traversal; no mutation of errors.

Dependencies and integration points: Uses `reflect`. `pacer.IsRetryAfter` depends on `Walk` to find nested retry metadata, and other packages can use it for mixed error-chain compatibility.

Risks and test signals: Reflection on unexported or unusual `Err` fields can panic if interface extraction is invalid, though the intended targets are exported stdlib fields. Recursive multi-error walking lacks cycle detection beyond the single-chain DeepEqual guard.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/errors/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/errors/errors_test.go -->
# sources/user-network-fs/rclone/lib/errors/errors_test.go

Source read signal: reviewed complete local file (249 lines, sha256 bdac5b1c2ac7f1e5).

Purpose: Exhaustively tests `Walk` over cause, unwrap, reflected `Err`, multi-error, and callback-stop scenarios.

Important APIs/types/functions: `TestWalk` defines local error wrappers `causerError`, `wrapperError`, `multiWrapperError`, `reflectError`, and `stopError`.

Control flow: Each table case records errors visited by `Walk`; the callback stops when it sees `stopError`. Cases cover nil children, nested mixed chains, multi-wrapper fan-out, and stop behavior inside nested chains.

State and persistence behavior: Test-local error values only; no persistence.

Dependencies and integration points: Uses `errors`, `fmt`, `testing`, and `testify/assert`.

Risks and test signals: Strong behavior signal for traversal ordering and stop semantics. It does not cover cyclic multi-wrapper graphs or structs with inaccessible `Err` fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/errors/errors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/exitcode/exitcode.go -->
# sources/user-network-fs/rclone/lib/exitcode/exitcode.go

Source read signal: reviewed complete local file (27 lines, sha256 d175aaf79b66c36d).

Purpose: Centralizes rclone process exit status numbers.

Important APIs/types/functions: Exports constants `Success`, `UncategorizedError`, `UsageError`, `DirNotFound`, `FileNotFound`, `RetryError`, `NoRetryError`, `FatalError`, `TransferExceeded`, `NoFilesTransferred`, and `DurationExceeded`.

Control flow: No runtime flow; constants are assigned by `iota`.

State and persistence behavior: No state. Numeric values are an external CLI contract consumed by scripts and users.

Dependencies and integration points: No imports. Command-line error handling should use these constants for consistent process termination.

Risks and test signals: Reordering or inserting constants before existing ones would change public exit codes. Tests elsewhere should assert key code values if this ABI must remain stable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/exitcode/exitcode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/driveletter_other.go -->
# sources/user-network-fs/rclone/lib/file/driveletter_other.go

Source read signal: reviewed complete local file (8 lines, sha256 38c2aba3f2ad97d0).

Purpose: Provides the non-Windows stub for unused drive-letter discovery.

Important APIs/types/functions: Exports `FindUnusedDriveLetter() uint8`, returning zero.

Control flow: No platform work is done on non-Windows builds.

State and persistence behavior: Stateless.

Dependencies and integration points: Selected by `!windows` build tag so callers can use one API cross-platform.

Risks and test signals: Callers must interpret zero as no drive letter available. Build tags are the main correctness surface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/driveletter_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/driveletter_windows.go -->
# sources/user-network-fs/rclone/lib/file/driveletter_windows.go

Source read signal: reviewed complete local file (22 lines, sha256 87e703cc3e18f250).

Purpose: Finds an available Windows drive letter for mount-like operations.

Important APIs/types/functions: Exports `FindUnusedDriveLetter() uint8`.

Control flow: Iterates from `Z:` down to `D:`, skipping `A:`, `B:`, and normally-system `C:`, and returns the first letter whose root path does not exist.

State and persistence behavior: Reads filesystem mount state via `os.Stat`; no state is written.

Dependencies and integration points: Uses `os` and Windows build tag. Consumers can use the returned byte to choose a mount drive.

Risks and test signals: Race exists between discovery and later mount. Access errors other than not-exist are treated as unavailable, and substituted network drives may influence results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/driveletter_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/file.go -->
# sources/user-network-fs/rclone/lib/file/file.go

Source read signal: reviewed complete local file (22 lines, sha256 9f50b4b9faabc2e2).

Purpose: Wraps platform-specific `OpenFile` with familiar `Open` and `Create` helpers.

Important APIs/types/functions: Exports `Open` and `Create`, both delegating to package variable/function `OpenFile`.

Control flow: `Open` calls `OpenFile` with `os.O_RDONLY`; `Create` opens read/write with create/truncate and mode 0666.

State and persistence behavior: Opens or creates real filesystem files; persistence is determined by caller writes and close behavior.

Dependencies and integration points: Uses `os` and integrates with Windows-specific `OpenFile` that enables delete/rename sharing.

Risks and test signals: Correctness depends on the platform `OpenFile` implementation. Tests verify open, append, read, rename-open, and delete-open semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/file_other.go -->
# sources/user-network-fs/rclone/lib/file/file_other.go

Source read signal: reviewed complete local file (20 lines, sha256 38a094c64d5890a0).

Purpose: Non-Windows implementation of file opening and reserved-name checking.

Important APIs/types/functions: Exposes `OpenFile = os.OpenFile` and `IsReserved(path string) error` returning nil.

Control flow: The standard library handles open semantics; reserved-name checking is a no-op outside Windows.

State and persistence behavior: Opening files may create/modify persistent files depending on flags; `IsReserved` is stateless.

Dependencies and integration points: Selected by `!windows` build tag. Shared `Open` and `Create` use this variable.

Risks and test signals: The variable form allows tests or callers in-package to replace `OpenFile`; no reserved-name validation is performed for non-Windows filesystems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/file_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/file_test.go -->
# sources/user-network-fs/rclone/lib/file/file_test.go

Source read signal: reviewed complete local file (170 lines, sha256 4e7f3eb1e7066ecf).

Purpose: Smoke-tests cross-platform file wrapper behavior and Windows reserved-name validation.

Important APIs/types/functions: Helpers `checkListingNoSize`, `checkListing`; tests `TestOpenFileRename`, `TestOpenFileDelete`, `TestOpenFileOperations`, and `TestIsReserved`.

Control flow: Tests create temp files with `Create`/`OpenFile`/`Open`, write and read data, remove or rename while the file handle remains open, and check directory listings. `TestIsReserved` skips non-Windows and validates reserved DOS names and trailing period/space.

State and persistence behavior: Uses `t.TempDir`, creates/removes files, and relies on cleanup after test completion.

Dependencies and integration points: Uses `os`, `path`, `runtime`, `io`, and `testify`. It validates the platform-specific `file_windows.go` sharing behavior through the common API.

Risks and test signals: Rename/delete semantics differ by OS; the tests express the intended Windows-compatible behavior. The reserved-name test only runs on Windows, leaving non-Windows no-op behavior implicit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/file_windows.go -->
# sources/user-network-fs/rclone/lib/file/file_windows.go

Source read signal: reviewed complete local file (102 lines, sha256 59892294574fc74a).

Purpose: Windows implementation of file opening that allows open files to be renamed/deleted, plus Windows reserved-name validation.

Important APIs/types/functions: Exports `OpenFile` and `IsReserved`. `OpenFile` maps Go open flags to `syscall.CreateFile` access/create modes and includes `FILE_SHARE_DELETE`.

Control flow: `OpenFile` validates path, converts to UTF-16, computes access and create modes from flags, calls `CreateFile`, and wraps the handle with `os.NewFile`. `IsReserved` checks empty/current/separator-only paths, trailing spaces/periods, and DOS device basenames with a regexp.

State and persistence behavior: Opens or creates real files using Windows APIs. `IsReserved` is stateless.

Dependencies and integration points: Uses `syscall`, `os`, `filepath`, `regexp`, and Windows build tag. It underpins all package `Open`/`Create` calls on Windows.

Risks and test signals: Flag mapping must stay compatible with Go's `os.OpenFile` behavior while adding delete sharing. Reserved-name validation is basename-based and intentionally rejects `CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, and `LPT1-9` with extensions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/file_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/mkdir.go -->
# sources/user-network-fs/rclone/lib/file/mkdir.go

Source read signal: reviewed complete local file (8 lines, sha256 db2ca063e2cf2bb9).

Purpose: Keeps a package-level `MkdirAll` wrapper around `os.MkdirAll`.

Important APIs/types/functions: Exports `MkdirAll(path string, perm os.FileMode) error`.

Control flow: Directly delegates to `os.MkdirAll`.

State and persistence behavior: Creates directories persistently according to the filesystem and permissions.

Dependencies and integration points: Uses `os`. The wrapper preserves a stable package API for callers that historically used `lib/file`.

Risks and test signals: Behavior is standard library behavior; tests should live at higher-level callers that depend on directory creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/mkdir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/preallocate.go -->
# sources/user-network-fs/rclone/lib/file/preallocate.go

Source read signal: reviewed complete local file (6 lines, sha256 60512e528574d12f).

Purpose: Defines the shared preallocation disk-full sentinel.

Important APIs/types/functions: Exports `ErrDiskFull`.

Control flow: No runtime flow.

State and persistence behavior: No state. Platform implementations wrap OS-specific ENOSPC/disk-full errors with this value.

Dependencies and integration points: Used by Linux and Windows `PreAllocate` implementations and by callers that want to distinguish no-space from other allocation failures.

Risks and test signals: Callers should use `errors.Is` only if platform wrappers preserve identity; current implementations return the sentinel directly for recognized disk-full cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/preallocate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/preallocate_other.go -->
# sources/user-network-fs/rclone/lib/file/preallocate_other.go

Source read signal: reviewed complete local file (23 lines, sha256 ddb844a934195412).

Purpose: Stub implementation of file preallocation and sparse-file marking for platforms other than Windows and Linux.

Important APIs/types/functions: Defines `PreallocateImplemented=false`, `PreAllocate`, `SetSparseImplemented=false`, and `SetSparse`.

Control flow: Both functions return nil without modifying the file.

State and persistence behavior: No state changes; preallocation is explicitly a no-op.

Dependencies and integration points: Uses `os` for file type. Build tag excludes Windows and Linux.

Risks and test signals: Callers must check implementation constants if behavior matters. Silent no-op is intentional for unsupported platforms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/preallocate_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/preallocate_unix.go -->
# sources/user-network-fs/rclone/lib/file/preallocate_unix.go

Source read signal: reviewed complete local file (72 lines, sha256 7328c813fd20ab2e).

Purpose: Linux implementation of file preallocation through `fallocate`.

Important APIs/types/functions: Exports `PreallocateImplemented=true`, `PreAllocate`, `SetSparseImplemented=false`, and `SetSparse`. Package state includes candidate `fallocFlags`, atomic `fallocFlagsIndex`, and `preAllocateMu`.

Control flow: `PreAllocate` ignores non-positive sizes, serializes calls, tries the current `fallocate` flag combination, advances to the next combination on `ENOTSUP`, maps `ENOSPC` to `ErrDiskFull`, retries on `EINTR`, and eventually returns nil if all fallocate modes are disabled.

State and persistence behavior: May allocate disk blocks for the file. The atomic flag index persists for the process after discovering unsupported fallocate modes.

Dependencies and integration points: Uses `golang.org/x/sys/unix`, `syscall`, `sync`, `atomic`, and `fs.Debugf`. Integrates with transfer writers that preallocate destination files.

Risks and test signals: Global fallback state means one filesystem's `ENOTSUP` can affect later files. Mutex limits concurrency. Disk-full mapping is important for retry/fatal policy; ZFS hole-punch fallback is noted in comments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/preallocate_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/preallocate_windows.go -->
# sources/user-network-fs/rclone/lib/file/preallocate_windows.go

Source read signal: reviewed complete local file (105 lines, sha256 d65b3007c15d1f8b).

Purpose: Windows implementation of preallocation and sparse-file marking using NT and DeviceIoControl APIs.

Important APIs/types/functions: Defines lazy `ntdll` procs, structs matching native info layouts, `PreallocateImplemented=true`, `PreAllocate`, `SetSparseImplemented=true`, and `SetSparse`.

Control flow: `PreAllocate` queries volume allocation-unit sizes, rounds requested size up to cluster size, calls `NtSetInformationFile` with `FileAllocationInformation`, and maps Windows disk-full handles to `ErrDiskFull`. `SetSparse` calls `DeviceIoControl` with `FSCTL_SET_SPARSE`.

State and persistence behavior: Alters allocation state of the supplied file and can mark it sparse. Package-level lazy procs and mutex are process state.

Dependencies and integration points: Uses `golang.org/x/sys/windows`, `syscall`, `unsafe`, `sync`, and `os`. Called by local write paths that want efficient allocation on NTFS-like filesystems.

Risks and test signals: Native struct layout and information-class constants must match Windows ABI. Cluster-size zero is guarded. Error mapping should be tested on full volumes and sparse-capable filesystems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/preallocate_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/unc.go -->
# sources/user-network-fs/rclone/lib/file/unc.go

Source read signal: reviewed complete local file (10 lines, sha256 ba84bc8ce489fc19).

Purpose: Non-Windows stub for converting Windows paths to long UNC paths.

Important APIs/types/functions: Exports `UNCPath(l string) string`.

Control flow: Returns the input unchanged.

State and persistence behavior: Stateless.

Dependencies and integration points: Selected by `!windows` build tag so callers can use `UNCPath` cross-platform.

Risks and test signals: No risk beyond build-tag correctness; Windows behavior is tested separately.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/unc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/unc_test.go -->
# sources/user-network-fs/rclone/lib/file/unc_test.go

Source read signal: reviewed complete local file (48 lines, sha256 d78736617d55d870).

Purpose: Windows-only tests for UNC long-path conversion.

Important APIs/types/functions: Defines `uncTestPaths`, `uncTestPathsResults`, and `TestUncPaths`.

Control flow: Each input is converted with `UNCPath`, compared to expected output, then passed through `UNCPath` again to assert idempotence.

State and persistence behavior: No filesystem mutation; all paths are strings.

Dependencies and integration points: Uses Windows build tag and `testing`. It validates paths used by Windows file APIs for long path support.

Risks and test signals: Covers drive paths, already-long paths, UNC server/share paths, long components, and malformed-looking UNC inputs. Only runs on Windows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/unc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/unc_windows.go -->
# sources/user-network-fs/rclone/lib/file/unc_windows.go

Source read signal: reviewed complete local file (31 lines, sha256 8b99fc56549604f7).

Purpose: Converts absolute Windows drive and server-share paths into extended-length UNC-style paths.

Important APIs/types/functions: Package regexp `isAbsWinDrive`; exported `UNCPath`.

Control flow: If a path starts with `\\?\`, it is already long and returned unchanged. If it starts with `\\`, it is converted to `\\?\UNC\...`; if it matches drive-root syntax such as `C:\`, it is prefixed with `\\?\`; otherwise it is unchanged.

State and persistence behavior: Stateless string conversion.

Dependencies and integration points: Uses `regexp` and `strings`. Called before Windows filesystem APIs where long paths or reserved characters may otherwise fail.

Risks and test signals: Regex only matches drive paths with a backslash after the colon, so relative drive paths are not converted. Tests assert idempotence and server/share behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/file/unc_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/auth.go -->
# sources/user-network-fs/rclone/lib/http/auth.go

Source read signal: reviewed complete local file (135 lines, sha256 11431c0ded0b3155).

Purpose: Defines HTTP authentication help text, configuration, flags, and the custom-auth callback type.

Important APIs/types/functions: Exports `AuthHelp`, `CustomAuthFn`, `AuthConfigInfo`, `AuthConfig`, `AddFlagsPrefix`, `AddAuthFlagsPrefix`, and `DefaultAuthCfg`.

Control flow: `AuthHelp` templates prefix-aware documentation. `AddFlagsPrefix` binds htpasswd, realm, user, pass, salt, and user-from-header options. `DefaultAuthCfg` returns the default MD5 crypt salt.

State and persistence behavior: Config structs are in-memory; no auth data is persisted here. Password and htpasswd values are supplied by flags/config elsewhere.

Dependencies and integration points: Uses `html/template`, `pflag`, rclone `fs.Options`, and config flag helpers. `server.go` consumes `AuthConfig` to install middleware.

Risks and test signals: User-from-header is powerful and documented as proxy-trust-sensitive. The default salt must stay synchronized with `AuthConfigInfo`; tests only verify help template prefix substitution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/auth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/auth_test.go -->
# sources/user-network-fs/rclone/lib/http/auth_test.go

Source read signal: reviewed complete local file (15 lines, sha256 3a398323fd657357).

Purpose: Verifies that authentication help text uses the requested flag prefix.

Important APIs/types/functions: `TestHelpPrefixAuth` calls `AuthHelp`.

Control flow: The test renders help with a sentinel prefix and fails if the prefix is absent.

State and persistence behavior: Stateless.

Dependencies and integration points: Uses `strings` and `testing`; protects template interpolation in CLI help.

Risks and test signals: This is a light smoke test and does not validate every documented option or wording.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/auth_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/context.go -->
# sources/user-network-fs/rclone/lib/http/context.go

Source read signal: reviewed complete local file (59 lines, sha256 1bff5d07cf16829a).

Purpose: Defines private request context keys and helpers for HTTP auth/user/public URL state.

Important APIs/types/functions: `NewBaseContext`, `IsAuthenticated`, `PublicURL`, `CtxGetAuth`, `CtxGetUser`, and `CtxSetUser`.

Control flow: `NewBaseContext` returns an `http.Server.BaseContext` function that marks Unix-socket listeners or stores the public URL. Auth middleware stores either auth values or usernames; helpers read them from request contexts.

State and persistence behavior: Request-scoped context values only; no persistence.

Dependencies and integration points: Uses `context`, `net`, and `net/http`. Integrated by `server.newInstance` and all auth middleware/handlers.

Risks and test signals: Context keys are private typed ints to avoid collisions. `IsAuthenticated` treats either custom auth value or user as authenticated, so middleware ordering determines semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/middleware.go -->
# sources/user-network-fs/rclone/lib/http/middleware.go

Source read signal: reviewed complete local file (227 lines, sha256 32a9bb94e699ac05).

Purpose: Implements HTTP middleware for basic/htpasswd/custom authentication, TLS-client-certificate usernames, trusted header usernames, CORS, response headers, and base-url stripping.

Important APIs/types/functions: Key functions are `parseAuthorization`, `NewLoggedBasicAuthenticator`, `MiddlewareAuthCertificateUser`, `MiddlewareAuthHtpasswd`, `MiddlewareAuthBasic`, `MiddlewareAuthCustom`, `MiddlewareAuthGetUserFromHeader`, `MiddlewareCORS`, `MiddlewareResponseHeaders`, and `MiddlewareStripPrefix`.

Control flow: Basic-style middleware skips `OPTIONS`, validates credentials, and stores the username in context. Custom auth can consume Basic auth or a user already set by certificate/header middleware. Header auth trims and validates a username regexp. CORS adds configured allow headers/methods, response-header middleware overwrites configured headers, and strip-prefix allows root `OPTIONS` while stripping the configured base path for other requests.

State and persistence behavior: Mostly stateless; `onlyOnceWarningAllowOrigin` logs the wildcard-origin warning once. Auth results are request-context state.

Dependencies and integration points: Uses `go-http-auth`, rclone logging and parsed HTTP options, and context helpers from `context.go`. Installed by `Server.initAuth` and `NewServer`.

Risks and test signals: Header-based auth is only safe behind a trusted proxy. `MiddlewareAuthCertificateUser` assumes `r.TLS` and peer certificates are present. CORS wildcard is explicitly warned; tests cover auth modes, CORS, and custom headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/middleware.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/middleware_test.go -->
# sources/user-network-fs/rclone/lib/http/middleware_test.go

Source read signal: reviewed complete local file (648 lines, sha256 c6b3982827b6cdda).

Purpose: Integration-tests HTTP authentication and middleware behavior through live `Server` instances.

Important APIs/types/functions: Tests include `TestMiddlewareAuth`, `TestMiddlewareAuthCertificateUser`, `TestMiddlewareCORS`, `TestMiddlewareCORSEmptyOrigin`, `TestMiddlewareCORSWithAuth`, and `TestMiddlewareResponseHeaders`.

Control flow: Tests create temporary servers with different `Config` and `AuthConfig`, mount echo or username handlers, issue real HTTP(S) requests, and assert status, body, auth challenge headers, CORS headers, and response headers.

State and persistence behavior: Starts local listeners and shuts them down after each case. Reads test TLS certs and htpasswd files.

Dependencies and integration points: Uses `net/http`, `crypto/tls`, `context`, server helpers from `server_test.go`, and `testify/require`. It validates interaction among `server.go`, `auth.go`, `context.go`, and middleware.

Risks and test signals: Strong signal for authentication precedence, invalid header usernames, cert common-name extraction, and `OPTIONS` preflight bypass. It does not test spoofed proxy chains beyond username validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/middleware_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/serve/dir.go -->
# sources/user-network-fs/rclone/lib/http/serve/dir.go

Source read signal: reviewed complete local file (254 lines, sha256 0049e810d80f6ab8).

Purpose: Represents and renders HTTP directory listings for rclone serve modes.

Important APIs/types/functions: Types `DirEntry`, `Directory`, and `Crumb`; functions/methods `NewDirectory`, `SetQuery`, `AddHTMLEntry`, `AddEntry`, `Error`, `ProcessQueryParams`, sorter types, and `Serve`.

Control flow: `NewDirectory` builds title/name/zip URL and breadcrumbs. Add methods append escaped entry URLs and optional zip links. `ProcessQueryParams` chooses and applies name, dir-first, size, or time sort with optional descending order. `Serve` accounts the directory transfer, executes the HTML template into a buffer, sets content headers, and writes it.

State and persistence behavior: `Directory` holds in-memory listing state only. `Error` records counted/logged errors and may write an HTTP 500 response.

Dependencies and integration points: Uses rclone `fs`, `accounting`, `rest.URLPathEscape`, `html/template`, and `net/http`. Called by HTTP/WebDAV serving code when presenting directories.

Risks and test signals: URL escaping for colon/quotes and query handling are important. Sorting directory sizes uses a sentinel offset to keep directories predictable. Template execution errors become counted transfer errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/serve/dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/serve/dir_test.go -->
# sources/user-network-fs/rclone/lib/http/serve/dir_test.go

Source read signal: reviewed complete local file (126 lines, sha256 724e692a573299e3).

Purpose: Unit-tests directory-listing construction, URL escaping, error responses, and template rendering.

Important APIs/types/functions: `GetTemplate`, `TestNewDirectory`, `TestSetQuery`, `TestAddHTMLEntry`, `TestAddEntry`, `TestError`, and `TestServe`.

Control flow: Tests construct directories with the golden template, add file/dir entries, assert exact `DirEntry` slices for escaped URLs/query strings, exercise `Error`, and render a listing through `httptest`.

State and persistence behavior: Reads a template from testdata; no persistent writes.

Dependencies and integration points: Uses `httptest`, `html/template`, `lib/http.GetTemplate`, `testify`, and the serve directory types.

Risks and test signals: Exact HTML output protects template data shape. Query propagation for `ZipURL` differs from entry query in the current behavior and is captured by tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/serve/dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/serve/serve.go -->
# sources/user-network-fs/rclone/lib/http/serve/serve.go

Source read signal: reviewed complete local file (115 lines, sha256 4f51d0736512c95b).

Purpose: Serves an `fs.Object` over HTTP for GET and HEAD, including range requests and selected metadata headers.

Important APIs/types/functions: Exported `Object(w, r, o)` is the main API.

Control flow: Rejects non-GET/HEAD, sets range/content-length/content-type/last-modified headers, forwards selected metadata headers, returns immediately for HEAD, parses Range into open options for GET, opens the object, wraps it in accounting, writes the status, and streams with `io.Copy`.

State and persistence behavior: Does not mutate the object; creates accounting transfer state for the request. Response headers/body are the only output.

Dependencies and integration points: Uses `fs.Object`, `fs.MimeType`, `fs.GetMetadata`, `fs.ParseRangeOption`, and `accounting.Stats`. Integrated by serve frontends that map URLs to objects.

Risks and test signals: Range math must avoid invalid content ranges and preserve correct content length. Errors after headers are written can only be logged. Metadata header pass-through affects browser/cache behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/serve/serve.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/serve/serve_test.go -->
# sources/user-network-fs/rclone/lib/http/serve/serve_test.go

Source read signal: reviewed complete local file (106 lines, sha256 ae5c730bbc4a90bc).

Purpose: Tests HTTP object serving semantics for methods, headers, range requests, metadata, and response body.

Important APIs/types/functions: Tests `TestObjectBadMethod`, `TestObjectHEAD`, `TestObjectGET`, `TestObjectRange`, `TestObjectBadRange`, and `TestObjectHEADMetadata`.

Control flow: Uses `httptest` requests/recorders and mock or memory objects, then asserts status, content length, accept-ranges, last-modified, content-range, body, and metadata headers.

State and persistence behavior: In-memory objects only; no persistent writes.

Dependencies and integration points: Uses `mockobject`, `object.NewMemoryObject`, `fs.Metadata`, and standard HTTP test tools.

Risks and test signals: Good coverage for basic and range behavior. It does not simulate streaming write errors or object-open failures after headers are prepared.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/serve/serve_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/server.go -->
# sources/user-network-fs/rclone/lib/http/server.go

Source read signal: reviewed complete local file (630 lines, sha256 eda428593afbf497).

Purpose: Provides rclone's reusable HTTP server wrapper with configuration, routing, TLS, socket activation, h2c, base URL stripping, auth, templates, and graceful shutdown.

Important APIs/types/functions: Public pieces include `Help`, `Middleware`, `ConfigInfo`, `Config`, flag methods, `DefaultCfg`, `Server`, options `WithAuth`/`WithConfig`/`WithTemplate`, `NewServer`, `Serve`, `Wait`, `Router`, `Shutdown`, `HTMLTemplate`, `URLs`, `Addr`, and `UsingAuth`. TLS errors include `ErrInvalidMinTLSVersion`, `ErrTLSBodyMismatch`, `ErrTLSFileMismatch`, and `ErrTLSParseCA`.

Control flow: `NewServer` builds a chi router, normalizes base URL, initializes template/TLS, parses response headers, installs CORS/response/auth middleware, then either uses systemd socket-activation listeners or creates Unix/TCP/TLS listeners from config. `newInstance` constructs `http.Server` with timeouts, base context, optional TLS wrapping, and h2c for cleartext. `Serve` starts one goroutine per instance and registers an atexit shutdown; `Shutdown` unregisters and gracefully closes each server.

State and persistence behavior: Holds listener/server instances, TLS config, parsed template, auth config, waitgroup, and atexit handle in memory. Unix sockets are created by listeners and removed by the runtime on close where supported.

Dependencies and integration points: Uses chi, rclone `fs` config flags, `atexit`, `sdactivation`, TLS/x509, and middleware/template/auth helpers. Serve commands mount handlers on `Router`.

Risks and test signals: Auth precedence is subtle when header/cert auth combines with custom/basic/htpasswd. TLS config must reject half-configured cert/key inputs. Socket activation overrides configured addresses. Tests cover Unix, HTTP, base URL, TLS, mutual TLS, h2c, and help prefix.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/server_test.go -->
# sources/user-network-fs/rclone/lib/http/server_test.go

Source read signal: reviewed complete local file (604 lines, sha256 30f6d4132d490005).

Purpose: End-to-end tests for the reusable HTTP server wrapper.

Important APIs/types/functions: Provides test helpers `testEmptyHandler`, `testEchoHandler`, `testAuthUserHandler`, `testExpectRespBody`, `testGetServerURL`, `testNewHTTPClientUnix`, and `testReadTestdataFile`; tests Unix sockets, HTTP auth, base URL normalization, TLS/mTLS config, h2c, and help text.

Control flow: Tests create `Server` instances with temp addresses or sockets, mount handlers, call `Serve`, make real client requests, assert responses, then call `Shutdown`.

State and persistence behavior: Creates Unix socket files and local TCP listeners; reads TLS testdata; cleanup is via deferred shutdown and temp dirs.

Dependencies and integration points: Uses `net/http`, `crypto/tls`, `x/net/http2`, and `testify/require`. Exercises integration across `server.go`, middleware, auth, TLS, and context helpers.

Risks and test signals: Strong coverage for TLS misconfiguration and listener URL generation. Some tests skip certificate hostname validation with `InsecureSkipVerify` because fixtures lack proper SANs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/server_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/template.go -->
# sources/user-network-fs/rclone/lib/http/template.go

Source read signal: reviewed complete local file (140 lines, sha256 afe0ae64f734ad4a).

Purpose: Provides help/configuration and parsing for custom HTML directory-listing templates.

Important APIs/types/functions: Exports `TemplateHelp`, `TemplateConfigInfo`, `TemplateConfig`, flag methods, `DefaultTemplateCfg`, `AfterEpoch`, embedded `Assets`, and `GetTemplate`.

Control flow: `TemplateHelp` renders prefix-aware docs. `GetTemplate` reads either an embedded default `templates/index.html` or a user-provided path, registers helper funcs (`afterEpoch`, `contains`, `hasPrefix`, `hasSuffix`), and parses the template.

State and persistence behavior: Embedded assets are read-only; parsed templates are returned to callers and held by `Server`.

Dependencies and integration points: Uses `embed`, `html/template`, `os`, `strings`, `time`, rclone flags/options, and serve directory data fields.

Risks and test signals: User templates can fail parse at server init. Helper names are part of the documented template contract; tests only check help prefix, while directory tests render a golden template.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/template.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/template_test.go -->
# sources/user-network-fs/rclone/lib/http/template_test.go

Source read signal: reviewed complete local file (15 lines, sha256 667802e96bc03f7a).

Purpose: Smoke-tests template help prefix interpolation.

Important APIs/types/functions: `TestHelpPrefixTemplate` calls `TemplateHelp`.

Control flow: Renders help with a sentinel prefix and asserts the prefix is present.

State and persistence behavior: Stateless.

Dependencies and integration points: Uses `strings` and `testing`.

Risks and test signals: Light coverage only; parsing and rendering behavior is covered indirectly by serve directory tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/http/template_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/israce/israce.go -->
# sources/user-network-fs/rclone/lib/israce/israce.go

Source read signal: reviewed complete local file (9 lines, sha256 981d6f5c52b8079d).

Purpose: Reports race-detector-enabled builds.

Important APIs/types/functions: Under the `race` build tag, exports `const Enabled = true`.

Control flow: No runtime flow; build tags select the file.

State and persistence behavior: No state.

Dependencies and integration points: Package can be used by tests or runtime code that adjust behavior under `go test -race`.

Risks and test signals: Correctness depends entirely on Go build tag selection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/israce/israce.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/israce/norace.go -->
# sources/user-network-fs/rclone/lib/israce/norace.go

Source read signal: reviewed complete local file (9 lines, sha256 0d017c64a7177287).

Purpose: Reports non-race-detector builds.

Important APIs/types/functions: Under the `!race` build tag, exports `const Enabled = false`.

Control flow: No runtime flow.

State and persistence behavior: No state.

Dependencies and integration points: Complements `israce.go` so callers have one import regardless of build mode.

Risks and test signals: Build constraints must remain complementary with the race-tagged file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/israce/norace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/jwtutil/jwtutil.go -->
# sources/user-network-fs/rclone/lib/jwtutil/jwtutil.go

Source read signal: reviewed complete local file (115 lines, sha256 8f3d3c369eb3111c).

Purpose: Implements JWT bearer-token authentication helpers for rclone backends that exchange signed JWTs for OAuth tokens.

Important APIs/types/functions: Exports `RandomHex` and `Config`; helper `bodyToString`; private JSON `response` struct.

Control flow: `RandomHex` returns hex-encoded crypto-random bytes. `Config` signs supplied JWT claims with RS256 and custom headers, posts an `application/x-www-form-urlencoded` JWT bearer grant to the token URL with query params, logs/reads the body, validates HTTP 200 and access token presence, builds an `oauth2.Token` with optional expiry, and stores it through `oauthutil.PutToken`.

State and persistence behavior: Persists the resulting OAuth token into the supplied config mapper. Reads randomness and performs an outbound HTTP request through the provided client.

Dependencies and integration points: Uses `golang-jwt/jwt/v4`, RSA keys, `oauth2`, rclone config maps, and `oauthutil`. Backends can call this during config to avoid browser OAuth flows.

Risks and test signals: Response body close is deferred after reading; the deferred error formatting currently wraps the outer `err` rather than the close error. Non-200 responses return only status, though body is logged at debug. Tests should mock token endpoints and malformed JSON.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/jwtutil/jwtutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/kv/bolt.go -->
# sources/user-network-fs/rclone/lib/kv/bolt.go

Source read signal: reviewed complete local file (320 lines, sha256 49ca1d74390c8dd3).

Purpose: Implements a process-shared, reference-counted bbolt key/value database for supported platforms.

Important APIs/types/functions: `DB` holds name/path/facility/ref count, bbolt handle, timers, queue, lock settings, and write mode. Public APIs are `Supported`, `Start`, `Get`, `Path`, `Do`, `Stop`, `IsStopped`, and `Exit`; helpers include `makeName`, `open`, `close`, `loop`, `request.handle`, and `execute`.

Control flow: `Start` reuses existing DBs by name, creates the cache directory, opens read-only if possible, registers the DB, and starts a serialized request loop. `Do` enqueues a request and waits. The loop handles requests, idle/lock timers that close the bbolt handle, and stop requests that decrement refs and optionally remove the DB file. `execute` opens for read/write and runs a bbolt view or update against the facility bucket.

State and persistence behavior: Persists data under `config.GetCacheDir()/kv/<encoded-name>.bolt` mode 0600, directory 0700. Maintains process-global `dbMap`, refs, timers, and at-exit shutdown state.

Dependencies and integration points: Uses bbolt, rclone config/cache settings, `encoder.OS` for safe DB filenames, and `fs.GetConfig` retry/lock durations. Callers implement `Op` over abstract `Bucket`/`Cursor`.

Risks and test signals: Queue size is small and `Do` can block if the loop stops after the nil check. `IsStopped` checks global map length, not this DB specifically. Cross-process bbolt locks and timer-close behavior need careful testing; unit tests cover concurrent `Start` refs and `Exit`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/kv/bolt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/kv/internal_test.go -->
# sources/user-network-fs/rclone/lib/kv/internal_test.go

Source read signal: reviewed complete local file (68 lines, sha256 ea42015a2c824eb5).

Purpose: Tests concurrency and global shutdown behavior of the supported KV implementation.

Important APIs/types/functions: `TestKvConcurrency` and `TestKvExit`.

Control flow: `TestKvConcurrency` starts the same facility from multiple goroutines, asserts one shared DB with multiple refs, then stops it repeatedly and checks the final inactive error. `TestKvExit` starts several facilities with increasing refs and verifies `Exit` clears the map.

State and persistence behavior: Mutates package global `dbMap` and may create cache DB files under the configured cache directory; test startup removes empty test leftovers in `Start`.

Dependencies and integration points: Uses `context`, `sync`, `fmt`, and `testify`.

Risks and test signals: Good coverage for reference counting and global map cleanup. It does not perform actual bucket read/write operations or timer expiry tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/kv/internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/kv/types.go -->
# sources/user-network-fs/rclone/lib/kv/types.go

Source read signal: reviewed complete local file (34 lines, sha256 0ce0aad1c03bca0a).

Purpose: Defines the platform-independent KV abstraction and shared errors.

Important APIs/types/functions: Errors `ErrEmpty`, `ErrInactive`, `ErrUnsupported`; interfaces `Op`, `Bucket`, and `Cursor`.

Control flow: No runtime flow. `Op.Do` receives a context and abstract bucket; bucket/cursor interfaces mirror bbolt operations needed by callers.

State and persistence behavior: No state. Implementations provide persistence or unsupported stubs.

Dependencies and integration points: Uses `context` and `errors`. Both `bolt.go` and `unsupported.go` depend on these definitions, as do callers implementing KV operations.

Risks and test signals: Interface shape is effectively an internal ABI. `Bucket.Get` returns byte slices whose ownership follows backend semantics, so callers must copy if they retain data after transactions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/kv/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/kv/unsupported.go -->
# sources/user-network-fs/rclone/lib/kv/unsupported.go

Source read signal: reviewed complete local file (45 lines, sha256 f839941648342a49).

Purpose: Provides plan9/js unsupported stubs for the KV package.

Important APIs/types/functions: Defines empty `DB`, `Supported=false`, `Start`, `Get`, `Path`, `Do`, `Stop`, `IsStopped`, and `Exit`.

Control flow: Operations return `ErrUnsupported`, nil, or true stopped status.

State and persistence behavior: No state and no persistence.

Dependencies and integration points: Uses build tag `plan9 || js`, `context`, and `fs.Fs`. Allows code to compile while callers can branch on `Supported`.

Risks and test signals: The `Get` signature order differs from the supported implementation (`Get(f fs.Fs, facility string)` vs `Get(facility string, f fs.Fs)`), which is a compile-time risk on unsupported targets if callers use it. Cross-target builds should catch this.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/kv/unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/mmap/mmap.go -->
# sources/user-network-fs/rclone/lib/mmap/mmap.go

Source read signal: reviewed complete local file (30 lines, sha256 b26994cae6e55e7a).

Purpose: Provides shared helpers around platform-specific large memory allocation.

Important APIs/types/functions: Exports `PageSize`, `MustAlloc`, and `MustFree`.

Control flow: `MustAlloc` calls `Alloc` and panics on error. `MustFree` calls `Free` and panics on error.

State and persistence behavior: Allocates process memory only. Callers must pass the exact returned slice to free on mmap-backed platforms.

Dependencies and integration points: Uses `os.Getpagesize`; platform files provide `Alloc`/`Free`. Used by high-throughput buffers that benefit from OS-backed allocation.

Risks and test signals: Panic helpers are only safe where allocation failure is unrecoverable. Derived slices passed to `Free` can fail or unmap the wrong range; tests cover basic write/free.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/mmap/mmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/mmap/mmap_test.go -->
# sources/user-network-fs/rclone/lib/mmap/mmap_test.go

Source read signal: reviewed complete local file (99 lines, sha256 9175f3dfe6112bfd).

Purpose: Tests and benchmarks memory-map allocation/free behavior.

Important APIs/types/functions: `TestAllocFree` and benchmarks for allocation/free across sizes and many allocations.

Control flow: The test allocates 4096 bytes, writes every byte, then frees. Benchmarks repeatedly allocate/free clean or dirtied pages and measure behavior with many pre-existing allocations.

State and persistence behavior: Allocates process memory only and frees it. Benchmarks can put pressure on virtual memory.

Dependencies and integration points: Uses `testing`, `fmt`, and `testify/assert`.

Risks and test signals: Basic correctness is covered, but double-free, derived-slice free, zero-size allocation, and allocation failure paths are not tested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/mmap/mmap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/mmap/mmap_unix.go -->
# sources/user-network-fs/rclone/lib/mmap/mmap_unix.go

Source read signal: reviewed complete local file (34 lines, sha256 670f0339d3b31899).

Purpose: Unix mmap-backed allocator for non-Plan9, non-Windows, non-JS builds.

Important APIs/types/functions: Exports `Alloc` and `Free`.

Control flow: `Alloc` calls anonymous private `unix.Mmap` with read/write permissions; `Free` calls `unix.Munmap` and wraps failures.

State and persistence behavior: Allocates anonymous virtual memory and releases it on `Free`; no file persistence.

Dependencies and integration points: Uses `golang.org/x/sys/unix` and `fmt`. Selected by build tags for Unix-like systems.

Risks and test signals: Callers must free the exact slice. Very large allocations may reserve address space or fail depending on OS overcommit policy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/mmap/mmap_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/mmap/mmap_unsupported.go -->
# sources/user-network-fs/rclone/lib/mmap/mmap_unsupported.go

Source read signal: reviewed complete local file (19 lines, sha256 0a2fdd6ba9700579).

Purpose: Fallback allocator for plan9/js where mmap APIs are unavailable.

Important APIs/types/functions: Exports `Alloc` and `Free`.

Control flow: `Alloc` returns `make([]byte, size)`; `Free` is a no-op.

State and persistence behavior: Uses Go heap memory and garbage collection; no explicit OS unmap.

Dependencies and integration points: Selected by `plan9 || js` build tag.

Risks and test signals: Memory is not returned synchronously to the OS. Behavior differs from mmap platforms but preserves API shape.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/mmap/mmap_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/mmap/mmap_windows.go -->
# sources/user-network-fs/rclone/lib/mmap/mmap_windows.go

Source read signal: reviewed complete local file (39 lines, sha256 1874f80cc8ef0092).

Purpose: Windows virtual-memory-backed allocator.

Important APIs/types/functions: Exports `Alloc` and `Free`.

Control flow: `Alloc` calls `windows.VirtualAlloc` with `MEM_COMMIT` and read/write protection, then constructs a byte slice from the returned pointer. `Free` passes the slice data pointer to `VirtualFree` with `MEM_RELEASE`.

State and persistence behavior: Allocates process virtual memory and releases it explicitly.

Dependencies and integration points: Uses `golang.org/x/sys/windows`, `unsafe`, and `fmt`. Selected by Windows build tag.

Risks and test signals: Unsafe pointer conversion and exact-slice free requirements are critical. Empty slices or derived slices would be unsafe inputs to `Free`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/mmap/mmap_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/multipart/multipart.go -->
# sources/user-network-fs/rclone/lib/multipart/multipart.go

Source read signal: reviewed complete local file (130 lines, sha256 582f42d1d8153b81).

Purpose: Implements generic concurrent multipart upload orchestration for backends that expose `fs.OpenChunkWriter`.

Important APIs/types/functions: Exports `BufferSize`, `NewRW`, `UploadMultipartOptions`, and `UploadMultipart`.

Control flow: `UploadMultipart` opens a chunk writer, bounds concurrency with `pacer.TokenDispenser`, creates a cancellable context and abort-on-error hook, unwraps accounting from the input, then loops reading `ChunkSize` buffers from the pool. Each chunk is uploaded in an errgroup goroutine via `WriteChunk`; tokens and buffers are released after upload. After all chunks succeed, it closes/finalizes the chunk writer and returns it.

State and persistence behavior: Uploads remote multipart state through the backend writer. On errors it cancels and, unless configured to leave parts, calls `Abort`.

Dependencies and integration points: Uses `fs.OpenChunkWriter`, `fs.ChunkWriter`, `pool.RW`, `pacer`, `accounting`, `atexit.OnError`, and `errgroup`. It is a backend utility for parallel chunked uploads.

Risks and test signals: Correctness depends on chunk writer concurrency safety and respecting cancellation. The first empty object still uploads one zero-length chunk only when `io.CopyN` returns EOF with part zero. Abort/finalize behavior needs backend integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/multipart/multipart.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/oauthutil/oauthutil.go -->
# sources/user-network-fs/rclone/lib/oauthutil/oauthutil.go

Source read signal: reviewed complete local file (1122 lines, sha256 d8e824981c71d8c6).

Purpose: Provides OAuth2 configuration, token persistence/refresh, interactive config state-machine flows, local callback server, client-credentials flow, and rc controls for active OAuth setup.

Important APIs/types/functions: Major APIs include `Config`, `MakeOauth2Config`, `MakeClientCredentialsConfig`, `SharedOptions`, `GetToken`, `PutToken`, `TokenSource`, `NewClientWithBaseClient`, `NewClientCredentialsClient`, `NewClient`, `AuthResult`, `Options`, `ConfigOut`, `ConfigOAuth`, rc handlers, `getAuthURL`, `configSetup`, `configExchange`, and `authServer`.

Control flow: Client creation overrides credentials from config, loads tokens, wraps oauth token sources, and saves refreshed tokens. `TokenSource.Token` returns cached valid tokens, rereads config for concurrent refreshes, builds the right oauth token source, retries refresh, wraps fatal OAuth errors, updates expiry timers, and persists changed tokens. `ConfigOAuth` is a state machine for existing-token confirmation, local/remote browser choice, authorize-token paste, client-credentials direct token retrieval, local webserver callback, and final return state. The auth server validates state, redirects `/auth` to the provider URL, receives callback data at `/`, renders a success/failure template, and sends an `AuthResult`.

State and persistence behavior: Persists OAuth tokens in the config mapper as JSON. Maintains process-global OAuth cancel function and active auth URL for rc status/stop. Token sources hold cached tokens, timers, and mutexes. Local auth server opens a TCP listener on 127.0.0.1:53682.

Dependencies and integration points: Uses `oauth2`, `clientcredentials`, rclone config/fserrors/fshttp/rc/random, `open-golang`, and HTTP/template packages. Backends register OAuth options and delegate config to `fs.ConfigOAuth`.

Risks and test signals: The flow has security-sensitive state validation and proxy/browser behavior. Global `templateString`, `oauthCancelFn`, and fixed port can conflict with concurrent auth attempts. Token refresh handles fatal OAuth errors specially. Some copied source lines show duplicated `if` text, so compile/test status should be watched. rc tests cover status/stop only.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/oauthutil/oauthutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/oauthutil/rc_test.go -->
# sources/user-network-fs/rclone/lib/oauthutil/rc_test.go

Source read signal: reviewed complete local file (68 lines, sha256 b9ed33edb63ebcb9).

Purpose: Tests remote-control endpoints that report or stop an active OAuth flow.

Important APIs/types/functions: `TestRcOAuthStatus` and `TestRcOAuthStop`.

Control flow: Tests fetch registered rc calls, assert stopped status/error with no active flow, manually install `oauthCancelFn` and `oauthURL` under lock, then verify running status, auth URL reporting, successful stop, and repeated-stop error.

State and persistence behavior: Mutates package globals `oauthCancelFn` and `oauthURL`, restoring them with deferred cleanup.

Dependencies and integration points: Uses `rc.Calls`, `context`, `testify/assert`, and `require`. Validates `init` rc registration in `oauthutil.go`.

Risks and test signals: Covers only rc state management, not the real auth server or cancellation during `configSetup`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/oauthutil/rc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/oauthutil/renew.go -->
# sources/user-network-fs/rclone/lib/oauthutil/renew.go

Source read signal: reviewed complete local file (94 lines, sha256 9b5ebc7fdc68f8fa).

Purpose: Keeps OAuth tokens refreshed while long-running uploads are active.

Important APIs/types/functions: Type `Renew` with constructor `NewRenew` and methods `Start`, `Stop`, `Invalidate`, `Expire`, and `Shutdown`.

Control flow: `NewRenew` starts `renewOnExpiry`, which waits on `TokenSource.OnExpiry` or shutdown. When expiry fires and upload count is nonzero, it runs the supplied transaction to refresh; otherwise it logs and does nothing. `Start`/`Stop` adjust an atomic upload counter.

State and persistence behavior: Holds upload count, done channel, shutdown once, and a pointer to `TokenSource`. Refresh side effects are delegated to `run` and token source persistence.

Dependencies and integration points: Uses `sync`, `atomic`, and rclone logging. Used by backends whose providers may cancel uploads if tokens are not refreshed during transfer.

Risks and test signals: `Shutdown` stops `ts.expiryTimer` only if it exists; nil handling for receiver is present. Upload counter can go negative if `Stop` is unbalanced. Tests should cover expiry with active/inactive uploads and idempotent shutdown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/oauthutil/renew.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/pacer.go -->
# sources/user-network-fs/rclone/lib/pacer/pacer.go

Source read signal: reviewed complete local file (302 lines, sha256 01ae0fa8fabf2e68).

Purpose: Provides a generic pacing, retry, and optional concurrency-limiting wrapper for API calls.

Important APIs/types/functions: Public types/functions include `State`, `Calculator`, `Pacer`, `InvokerFunc`, `Option`, `CalculatorOption`, `RetriesOption`, `MaxConnectionsOption`, `InvokerOption`, `Paced`, `New`, setters, `ModifyCalculator`, `Call`, `CallNoRetry`, `RetryAfterError`, and `IsRetryAfter`.

Control flow: `New` configures defaults, initializes a one-token pacing channel, optional connection tokens, calculator, and invoker. `beginCall` waits for the pace token based on current sleep and schedules token replacement after the delay, then optionally takes a connection token. `endCall` returns connection token, updates retry count/error, and asks the calculator for the next sleep. `call` invokes the paced function up to the retry limit and avoids recursive connection-token deadlock by checking the call stack. Retry-after errors wrap underlying errors and can be found through `lib/errors.Walk`.

State and persistence behavior: In-memory channels, mutex-protected options/state, and sleep goroutines only. No durable state.

Dependencies and integration points: Uses local `caller` and `errors` packages. Calculator implementations in sibling pacer files provide default, Google Drive, S3, and Azure IMDS behavior; multipart uploads use `TokenDispenser` from another sibling file.

Risks and test signals: Timer goroutines can accumulate under heavy pacing. Recursive-call detection by stack name is fragile but tested. Changing max connections after active calls is documented unsafe. Retry wrapping must preserve `errors.Is` through `Unwrap`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/pacer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/pacer_test.go -->
# sources/user-network-fs/rclone/lib/pacer/pacer_test.go

Source read signal: reviewed complete local file (480 lines, sha256 2f7f96b6510486e2).

Purpose: Tests pacer defaults, calculator behavior, call/retry flow, max-connection limiting, recursive deadlock avoidance, and retry-after error wrapping.

Important APIs/types/functions: Covers `New`, setters, `beginCall`, `endCall`, `Call`, `CallNoRetry`, default/Azure/GoogleDrive/S3 calculators, `RetryAfterError`, `Cause`, and `IsRetryAfter`.

Control flow: Tests drain tokens to control timing, use dummy paced functions and condition variables to observe concurrency, run retries with fixed counts, average randomized Google Drive sleeps, and verify nested retry-after errors through wrapping.

State and persistence behavior: Uses in-memory pacer channels and goroutines; no persistence.

Dependencies and integration points: Uses `sync`, `time`, `errors`, `strings`, `fmt`, and `testify/assert`. It reaches calculator types from sibling files, so it tests package-level integration beyond `pacer.go`.

Risks and test signals: Strong timing/concurrency signal, but timing tests can be sensitive under slow CI. Recursive deadlock tests protect the stack-inspection workaround.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pacer/pacer_test.go -->
