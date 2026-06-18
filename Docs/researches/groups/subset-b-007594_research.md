# subset-b-007594 Research

Grouped source research for Kubo command handlers under `core/commands`, including raw block operations, bootstrap/config mutation, CID formatting, DAG CAR import/export, MFS commands, diagnostics, and command-environment helpers. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/block.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/block.go

## Purpose

Defines the `ipfs block` plumbing command family for direct raw block access: stat, get, put, and rm. It is the command-layer bridge between CLI/RPC requests and the CoreAPI `Block()` service, with CID output honoring the shared `--cid-base` encoder.

## Important APIs, Types, and Functions

`BlockCmd` registers subcommands. `BlockStat` is the common stat/put response. `blockStatCmd` resolves a CID/path and returns CID plus size. `blockGetCmd` emits a raw block as `application/vnd.ipld.raw`. `blockPutCmd` imports streamed file arguments with `--cid-codec`, deprecated `--format`, `--mhtype`, `--mhlen`, `--pin`, and `--allow-big-block`. `blockRmCmd` resolves each argument and removes blocks with `--force` and quiet output.

## Control Flow

Handlers acquire CoreAPI with `cmdenv.GetApi`, parse paths through `cmdutils.PathOrCidPath`, and stream or emit typed results. `blockPutCmd` reads each multipart/stdin file, applies hash/codec options, stores through `api.Block().Put`, checks the 2 MiB soft size limit, and emits one result per input. `blockRmCmd` resolves immutable paths before removal and uses a CLI post-run loop to distinguish per-block failures from total aborts.

## State and Persistence Behavior

`put` writes blocks to the node blockstore and may pin recursively. `rm` deletes local blockstore entries; `force` affects nonexistent-block handling but not higher-level pin safety. `get` and `stat` are read-only except for possible network fetches when the request is not offline.

## Dependencies and Integration Points

Depends on `cmdenv`, `cmdutils`, CoreAPI block options, Kubo import config defaults, boxo files, `go-ipfs-cmds`, and multihash names. Integrates with global CID encoding flags and command response content-type metadata.

## Risks and Edge Cases

The deprecated `--format` path suppresses `--cid-codec` and can conflict with custom codec selection. Big blocks can be created only when explicitly allowed, and those may not transfer over standard Bitswap. `rm` emits per-block errors but returns a final error if any removal failed, which clients must handle as partial success.

## Test Signals

No file-local tests in this subset, but command tree coverage in `commands_test.go` includes all block subcommands. Good regression targets are CID codec/hash option combinations, stdin/multipart multiple puts, big-block rejection, raw content-type behavior, and partial `block rm` failure reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/bootstrap.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/bootstrap.go

## Purpose

Implements `ipfs bootstrap` commands for listing, adding, and removing trusted bootstrap peer addresses in the repo config. It also handles the newer `auto` placeholder used by AutoConf-backed bootstrap expansion.

## Important APIs, Types, and Functions

`BootstrapCmd` defaults to `bootstrapListCmd` and exposes `add`, `rm`, and `rm all`. `BootstrapOutput` carries peer strings. `bootstrapAdd`, `bootstrapRemove`, and `bootstrapRemoveAll` mutate `config.Config.Bootstrap` and persist with `repo.SetConfig`. `bootstrapWritePeers` sorts output and prefixes `added` or `removed`.

## Control Flow

Command handlers parse body arguments, open the fsrepo from `cmdenv.GetConfigRoot`, load config, apply validation or AutoConf rules, then persist changed config. `add` normalizes `default` to `auto`, rejects adding `auto` when AutoConf is disabled, validates non-auto multiaddrs as transport plus `/p2p`, deduplicates, and prepends new entries. `rm` either removes all or parses requested bootstrap peers and removes matching peer IDs or addresses.

## State and Persistence Behavior

This file directly persists repo config changes. `bootstrapRemoveAll` clears `cfg.Bootstrap`; selective `rm` rewrites it through `cfg.SetBootstrapPeers`. `list --expand-auto` is read-only and returns resolved bootstrap addresses without replacing the stored `auto` placeholder.

## Dependencies and Integration Points

Uses Kubo config, repo/fsrepo, `config.ParseBootstrapPeers`, `BootstrapPeers`, `BootstrapPeerStrings`, libp2p peer IDs, and multiaddr parsing. The `configExpandAutoName` option is shared with config commands.

## Risks and Edge Cases

Bootstrap peers are trust anchors, so accidental or malicious mutation changes network discovery. Selective removal is intentionally blocked when `auto` is active and AutoConf is enabled because expanded peers are managed externally. Address validation skips `auto`, so future placeholder strings need explicit handling.

## Test Signals

Command tree coverage verifies the bootstrap command paths. Useful targeted tests would cover `default` normalization, disabled AutoConf rejection, sorted output, selective address removal, `auto` plus `rm --all`, and config persistence failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/bootstrap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cat.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cat.go

## Purpose

Implements `ipfs cat`, which streams UnixFS file data for one or more IPFS/IPNS paths to stdout or RPC clients, with byte offset, length, and terminal progress support.

## Important APIs, Types, and Functions

`CatCmd` defines `ipfs-path` variadic arguments and `--offset`, `--length`, `--progress` options. The helper `cat(ctx, api, paths, offset, max)` resolves each path through `cmdutils.PathOrCidPath`, fetches UnixFS nodes, verifies they are files, seeks, applies aggregate length limits, and returns readers plus total length.

## Control Flow

The run handler validates non-negative offsets and lengths, parses stdin/body args, calls `cat`, sets response length, wraps all returned readers in `io.MultiReader`, and emits the stream. The CLI post-run skips progress for known short outputs, otherwise wraps emitted readers with `progressBarForReader` when `cmdenv.ShouldShowProgress` returns true.

## State and Persistence Behavior

The command is read-only. It can trigger path resolution and UnixFS block retrieval through CoreAPI unless the request is offline. No local config or repo state is mutated.

## Dependencies and Integration Points

Uses CoreAPI `Unixfs().Get`, boxo `files.File`, shared progress helpers from `get.go`, `cmdenv.ShouldShowProgress`, and command response length/streaming support. Directory inputs map to `iface.ErrIsDir`.

## Risks and Edge Cases

Offsets are consumed across multiple input paths, so a large offset can skip whole files. A file must implement `io.Seeker`; unsupported file implementations error. Stream read errors are returned through `res.Emit`, which is intentional so missing blocks surface to clients.

## Test Signals

No local tests in this subset. Regression coverage should include multi-path offset and length slicing, directory rejection, zero length, seek failures, short-output progress suppression, and missing-block propagation during `io.Copy`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cid.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cid.go

## Purpose

Defines repo-independent `ipfs cid` utilities for formatting, converting, inspecting, and listing multibase, multicodec, and multihash metadata.

## Important APIs, Types, and Functions

`CidCmd` registers `inspect`, `format`, `base32`, `bases`, `codecs`, and `hashes`. `cidFmtCmd` uses `cidFormatOpts`, `emitCids`, `toCidV0`, and `toCidV1`. `argumentIterator` merges positional and stdin arguments. `CidFormatRes`, `CodeAndName`, and `CidInspectRes` shape command output. Sorter types provide stable listings.

## Control Flow

`format` validates a printf-style CID format, optional version conversion, optional multicodec replacement, and optional output multibase. Requesting a non-base58btc base implicitly upgrades CIDv0 to CIDv1 unless `-v 0` is explicitly requested, where CIDv0 constraints are enforced. `emitCids` decodes each CID independently and emits non-fatal per-entry errors. `inspect` decodes one CID, derives base, codec, hash digest, CIDv0 feasibility, and CIDv1 canonical representation, with a PeerID fallback note.

## State and Persistence Behavior

All commands set `SetDoesNotUseRepo(true)` and are pure transformations over input strings and built-in multiformats tables. They do not read or write repo state.

## Dependencies and Integration Points

Uses `go-cid`, `go-cidutil`, multibase, multicodec, multihash, verifcid allowlist, IPLD multicodec registries, and libp2p peer ID conversion. `streamResult` from `commands.go` handles CLI non-fatal output errors.

## Risks and Edge Cases

CIDv0 conversion is valid only for dag-pb plus compatible sha2-256 hash. `emitCids` continues after per-CID decode/format errors, which can surprise clients expecting fail-fast behavior. `inspect` returns invalid-CID information as a typed result but its text encoder converts that into an error.

## Test Signals

`cid_test.go` covers CIDv0 with custom bases and implicit CIDv1 upgrade when a custom base is requested. Additional useful tests include unsupported multicodec conversion to CIDv0, stdin argument iteration errors, PeerID inspect hints, and sorted list stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cid_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cid_test.go

## Purpose

Tests selected `ipfs cid format` option interactions, especially CIDv0 base restrictions and automatic CIDv1 upgrades when a non-default multibase is requested.

## Important APIs, Types, and Functions

`TestCidFmtCmd` contains parallel subtests that directly invoke `cidFmtCmd.Run` with synthetic `cmds.Request` option maps. It iterates over `multibase.EncodingToStr` and checks expected errors for `-v 0` plus custom bases.

## Control Flow

The first subtest creates requests with `cidToVersionOptionName: "0"` and each multibase name, expecting no error only for `base58btc`. The second subtest builds requests with no explicit version and custom base options to assert the run path accepts implicit CIDv1 upgrade cases.

## State and Persistence Behavior

The test is pure and does not construct a repo, node, or filesystem. It exercises repo-independent command behavior.

## Dependencies and Integration Points

Depends on the `go-ipfs-cmds` request type and multibase table. It is tightly coupled to option names in `cid.go` and to `cidFmtCmd.Run` validation order.

## Risks and Edge Cases

The test uses a nil response emitter in cases where it expects validation to happen before emission. That is suitable for option validation but does not prove emitted formatted strings. The second subtest checks only absence of error, not exact output.

## Test Signals

Strong signal for custom-base validation and compatibility behavior. Missing signal remains actual response content, stdin argument handling, per-CID non-fatal errors, and inspect/list subcommands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cid_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/cidbase.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/cidbase.go

## Purpose

Provides shared command-environment helpers for CID output encoding, including the global `--cid-base` and deprecated `--upgrade-cidv0-in-output` options.

## Important APIs, Types, and Functions

`OptionCidBase` and `OptionUpgradeCidV0InOutput` are reusable command options. `GetCidEncoder` returns a `cidenc.Encoder`. `CidBaseDefined` checks whether `--cid-base` is set. `CidEncoderFromPath` infers output base from a CID embedded in a path.

## Control Flow

`GetCidEncoder` starts from `cidenc.Default`, applies a requested multibase encoder, and automatically enables CIDv0 upgrade for any base other than base58btc. If the deprecated upgrade flag is present, it overrides automatic behavior. `CidEncoderFromPath` extracts a likely CID from `CID`, `CID/...`, or `/namespace/CID/...`, decodes it, returns default encoding for CIDv0, and returns the CIDv1 multibase with upgrade enabled for CIDv1+.

## State and Persistence Behavior

No persistent state is changed. The functions only inspect request option maps or path strings.

## Dependencies and Integration Points

Uses `go-cid`, `go-cidutil/cidenc`, `go-ipfs-cmds`, and multibase. It is used by block, files, dag, filestore, and other commands that print CIDs.

## Risks and Edge Cases

Deprecated upgrade override can intentionally defeat automatic CIDv0 upgrade, producing output that may not match the requested base. `CidEncoderFromPath` is intentionally fuzzy and returns an error for non-CID paths, so callers must choose sensible fallback behavior.

## Test Signals

`cidbase_test.go` covers default encoding, base32 auto-upgrade, base58btc non-upgrade, deprecated overrides, CIDv0 path extraction, and CIDv1 base inference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/cidbase.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/cidbase_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/cidbase_test.go

## Purpose

Validates the shared CID encoder selection rules used across command output.

## Important APIs, Types, and Functions

`TestGetCidEncoder` uses synthetic `cmds.Request` instances to exercise `GetCidEncoder`. `TestEncoderFromPath` checks `CidEncoderFromPath` for CIDv0, CIDv1 base58btc, CIDv1 base32, namespaced paths, and malformed paths.

## Control Flow

Tests construct option maps and compare encoder fields directly. Path tests run a helper over multiple path shapes, then iterate bad inputs and assert extraction errors.

## State and Persistence Behavior

Pure unit tests. No repo, node, or filesystem state is used.

## Dependencies and Integration Points

Depends on `cidenc.Default`, multibase encoders, `cmds.Request`, and exact CID literals that encode representative version/base combinations.

## Risks and Edge Cases

Direct struct equality for encoders assumes stable comparable fields. The test intentionally treats IPNS and unknown namespaces as possible CID carriers, mirroring production fuzziness.

## Test Signals

Good coverage for automatic CIDv0 upgrade behavior and path-derived encoding. Remaining gaps include invalid multibase option errors and caller fallback behavior when no CID is found in a path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/cidbase_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/env.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/env.go

## Purpose

Centralizes command environment extraction, string escaping, and fast DHT providing helpers shared by command handlers.

## Important APIs, Types, and Functions

`GetNode`, `GetApi`, and `GetConfigRoot` extract Kubo node/API/config root from `commands.Context`. `EscNonPrint` and `needEscape` sanitize display strings. `ExecuteFastProvideRoot`, `ExecuteFastProvideDAG`, and `provideCIDSync` implement immediate DHT provide paths for import/add-like commands.

## Control Flow

`GetApi` honors `--offline` and deprecated `--local` by wrapping CoreAPI with `options.Api.Offline`. Fast root provide checks `Provide.Enabled`, active DHT availability, and `Provide.Strategy` match before either blocking on `router.Provide` or launching an async goroutine with node-lifetime context and timeout. Fast DAG provide builds a bloom tracker, walks entity roots or DAG links from the blockstore, and sends CIDs to a provider with backpressure.

## State and Persistence Behavior

Extraction functions are read-only. Fast provide mutates network/provider state by publishing provider records but does not alter blockstore data. Async goroutines are tied to `IpfsNode.Context()` to avoid outliving the daemon.

## Dependencies and Integration Points

Depends on Kubo `commands.Context`, CoreAPI options, config provide strategy logic, boxo blockstore/DAG walker, and libp2p routing. `ExecuteFastProvideDAG` integrates with node provider implementations and import/add workflows.

## Risks and Edge Cases

All extraction helpers type assert the environment and fail if used with an unexpected context. `provideCIDSync` assumes callers checked DHT availability. Async provide failures are logged rather than returned. Bloom tracker sizing and strategy flags affect how much of a DAG is announced.

## Test Signals

`env_test.go` covers string escaping only. Fast provide logic needs integration tests or fakes for strategy gating, DHT absence, wait vs async cancellation, and provider errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/env.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/env_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/env_test.go

## Purpose

Tests non-printable and backslash escaping used before displaying potentially unsafe strings.

## Important APIs, Types, and Functions

`TestEscNonPrint` exercises `needEscape`, `EscNonPrint`, and helper `hasNonPrintable`.

## Control Flow

The test injects byte `0x7f` into a string, asserts it needs escaping, checks the escaped result has no non-printable runes, verifies backslashes are escaped, and confirms plain strings and quotes are left alone except embedded escaped backslashes.

## State and Persistence Behavior

Pure string tests; no persistent state.

## Dependencies and Integration Points

Uses `strconv.IsPrint` in the test helper, matching production expectations for printable characters.

## Risks and Edge Cases

The test does not cover all Unicode categories, terminal escape sequences, or invalid UTF-8 replacement behavior. It focuses on the `strconv.Quote` based escaping path.

## Test Signals

Good signal for the common display sanitization path. Additional coverage could include control ranges, multi-byte Unicode, and strings with both quotes and backslashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/env_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/file.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/file.go

## Purpose

Provides a small helper to extract the next file argument from command multipart/stdin input.

## Important APIs, Types, and Functions

`GetFileArg(it files.DirIterator) (files.File, error)` advances the iterator, checks iterator errors, and converts the current entry to a `files.File`.

## Control Flow

If no entry is available, it returns the iterator error or an explicit "expected a file argument" error. If the entry is not a file, it returns "file argument was nil". Otherwise it returns the file handle for the caller to read or close.

## State and Persistence Behavior

No persistent state. It consumes one entry from the provided iterator, so callers control file lifetime.

## Dependencies and Integration Points

Depends on boxo `files`. Used by config replacement and MFS write paths to avoid duplicating multipart validation.

## Risks and Edge Cases

The helper only returns one file and does not enforce that no extra files remain. Callers must close returned files when appropriate.

## Test Signals

No direct tests in this subset. Coverage should include empty iterator, iterator error propagation, directory/non-file entries, and normal file extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/progress.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/progress.go

## Purpose

Defines shared progress-bar rendering policy and the full progress template used by transfer commands.

## Important APIs, Types, and Functions

`ProgressBarFullTemplate` is the `pb/v3` template for counters, bar, speed, percent, and ETA. `ShouldShowProgress(req, flag)` resolves a boolean progress option or defaults to terminal detection on stderr.

## Control Flow

If the option map contains a boolean for the named flag, that explicit value wins. If the option is absent or non-boolean, the function calls `IsTerminal(os.Stderr)`.

## State and Persistence Behavior

Read-only. It inspects request options and stderr terminal state.

## Dependencies and Integration Points

Uses `go-ipfs-cmds` and `tty.go`. Called by `cat`, `get`, `dag export`, and `dag stat` post-run paths.

## Risks and Edge Cases

Non-boolean option values silently fall back to TTY detection, which is robust but can hide caller option bugs. Terminal detection depends on the process stderr file descriptor.

## Test Signals

`progress_test.go` covers explicit true, explicit false, unset TTY default, and non-bool fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/progress_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/progress_test.go

## Purpose

Verifies progress display selection semantics for command post-run handlers.

## Important APIs, Types, and Functions

`TestShouldShowProgress` constructs request option maps with a local `makeReq` helper and compares `ShouldShowProgress` with expected values.

## Control Flow

Subtests assert explicit true and false override TTY state, unset options equal `IsTerminal(os.Stderr)`, and non-bool values are treated as unset.

## State and Persistence Behavior

Pure unit test; no persistence.

## Dependencies and Integration Points

Depends on `cmds.Request`, `os.Stderr`, and `IsTerminal`.

## Risks and Edge Cases

The unset and non-bool expectations are environment-dependent by design because they compare to the same terminal detection call. The test does not mock terminal state.

## Test Signals

Good signal for option precedence. Missing signal includes behavior when stderr is closed or replaced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/progress_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/tty.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/tty.go

## Purpose

Wraps terminal detection for standard and MSYS/Cygwin-style terminals.

## Important APIs, Types, and Functions

`IsTerminal(f *os.File) bool` checks both `isatty.IsTerminal` and `isatty.IsCygwinTerminal` for the file descriptor.

## Control Flow

The function extracts `f.Fd()` and returns true if either terminal detector recognizes it.

## State and Persistence Behavior

Read-only process/file-descriptor inspection.

## Dependencies and Integration Points

Depends on `github.com/mattn/go-isatty` and is used by `ShouldShowProgress`.

## Risks and Edge Cases

Callers must pass a non-nil file. Terminal detection can differ under containers, pipes, Windows compatibility layers, and test runners.

## Test Signals

Indirectly exercised by `progress_test.go`; no dedicated tests for Cygwin/MSYS behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/tty.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/sanitize.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/sanitize.go

## Purpose

Sanitizes untrusted remote strings before display in web UIs, terminals, or logs.

## Important APIs, Types, and Functions

`CleanAndTrim(str string) string` replaces Unicode control (`Cc`), format (`Cf`), and surrogate (`Cs`) runes with replacement characters, trims surrounding whitespace, and limits output to `maxRunes` 128 runes.

## Control Flow

The function builds a rune slice, replacing problematic categories and preserving other runes, including private-use characters. It trims whitespace after replacement, then truncates by rune count.

## State and Persistence Behavior

Pure string transformation. No persistence.

## Dependencies and Integration Points

Uses standard `strings` and `unicode`. `id.go` uses it for peer protocol IDs and agent versions returned from peerstore.

## Risks and Edge Cases

Length limiting is by runes, while pin-name validation elsewhere is by bytes. Replacement instead of deletion preserves evidence of unsafe input but may affect visual length. Whitespace introduced before invalid characters is trimmed after replacement.

## Test Signals

No direct test in this subset. Good tests would cover terminal escape controls, bidirectional format characters, long Unicode strings, private-use preservation, and whitespace trimming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/sanitize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/utils.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/utils.go

## Purpose

Holds reusable command utility functions for block-size safety, pin-name validation, CID/path parsing, and safe peer address copying.

## Important APIs, Types, and Functions

`AllowBigBlockOptionName`, `SoftBlockLimit`, and `AllowBigBlockOption` define the shared big-block override. `CheckCIDSize` loads a DAG node and delegates to `CheckBlockSize`. `ValidatePinName` enforces `MaxPinNameBytes`. `PathOrCidPath` accepts full paths or bare CID-like inputs. `CloneAddrInfo` clones peer address slices.

## Control Flow

`CheckBlockSize` allows any size only when `--allow-big-block` is true, otherwise rejects blocks over 2 MiB. `PathOrCidPath` first calls `path.NewPath(str)` and falls back to `/ipfs/` plus the string, returning the original error if both fail.

## State and Persistence Behavior

Utility functions are read-only except for DAG reads in `CheckCIDSize`. No persistent state is mutated.

## Dependencies and Integration Points

Uses boxo path, CoreAPI DAG service, go-cid, libp2p peer AddrInfo, and `go-ipfs-cmds`. Used by block put, DAG put/import, cat/get/files path parsing, and pin-related commands.

## Risks and Edge Cases

`PathOrCidPath` intentionally preserves original errors to avoid confusing fallback paths. Big-block override can create content that standard Bitswap peers cannot exchange. Pin-name length is by bytes, not runes.

## Test Signals

`utils_test.go` covers path fallback, original-error behavior, CID-with-path conversion, valid and invalid pin-name lengths, and Unicode byte counting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/utils_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/utils_test.go

## Purpose

Tests shared path/CID parsing and pin-name byte-length validation.

## Important APIs, Types, and Functions

`TestPathOrCidPath` exercises `PathOrCidPath` for full IPFS paths, bare CIDs, IPNS paths, invalid inputs, empty strings, and bare CID-with-path values. `TestValidatePinName` checks `ValidatePinName`.

## Control Flow

Subtests assert exact path strings on success and inspect error messages on failure. Pin-name tests check empty, valid, max-length, too-long, and multi-byte Unicode names.

## State and Persistence Behavior

Pure unit tests.

## Dependencies and Integration Points

Uses `testify/assert` and `require`, plus the utility constants from `utils.go`.

## Risks and Edge Cases

The invalid-character test allows either original input or generic "invalid" text, which is flexible but less exact. Unicode pin-name test assumes emoji byte length.

## Test Signals

Strong signal for user-facing parse errors and byte-length enforcement. Missing coverage includes `CheckBlockSize`, `CheckCIDSize`, and `CloneAddrInfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/commands.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/commands.go

## Purpose

Implements command-tree introspection through `ipfs commands`, shell completion subcommand wiring, and a CLI streaming helper for responses with per-entry non-fatal errors.

## Important APIs, Types, and Functions

`CommandsCmd(root)` returns the command tree lister. `Command`, `Option`, `commandEncoder`, `cmd2outputCmd`, and `cmdPathStrings` produce structured and text command listings. `CompletionCmd(root)` registers bash, zsh, and fish generation. `streamResult` prints streamed entries and aggregates non-fatal display errors.

## Control Flow

`CommandsCmd.Run` converts the root command tree into a `Command`, annotates whether options should be shown, and emits it. The text encoder recursively builds command paths, adds flag variants when requested, sorts output, and writes one line per path. Completion subcommands render scripts into a buffer and emit it as a stream. `streamResult` consumes response entries, invokes a callback, writes non-fatal errors to stderr, and returns a summary error if any occurred.

## State and Persistence Behavior

Read-only command metadata. It does not use repo state and marks itself with `SetDoesNotUseRepo(true)`.

## Dependencies and Integration Points

Uses `go-ipfs-cmds`, completion template functions from `completion.go`, and standard IO. `streamResult` is reused by CID and filestore command post-runs.

## Risks and Edge Cases

Command map iteration is normalized by sorting text output, but structured subcommand order is map-derived unless consumers sort. `streamResult` catches panics and converts them to internal errors, which protects CLI display but can hide callback bugs behind a generic message.

## Test Signals

`commands_test.go` checks the full root command tree and `Root.Get` lookup. Completion rendering has no dedicated tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/commands.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/commands_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/commands_test.go

## Purpose

Verifies that the exported root command tree contains the expected command and subcommand paths.

## Important APIs, Types, and Functions

`collectPaths` recursively walks `cmds.Command.Subcommands`. `TestCommands` compares the collected set to a long expected list and then verifies each listed path can be resolved with `Root.Get`.

## Control Flow

The test builds a set from `Root`, deletes every expected path, reports missing and unexpected paths, and then iterates expected paths again to assert command lookup succeeds and does not return nil.

## State and Persistence Behavior

Pure command metadata test. No repo state is used.

## Dependencies and Integration Points

Depends on the global `Root` command tree and exact command names from many files in `core/commands`.

## Risks and Edge Cases

This is intentionally brittle: adding, removing, renaming, deprecating, or relocating commands requires updating the list. It does not inspect options or handler behavior.

## Test Signals

Strong signal for command registration coverage, including all commands in this subset. Weak signal for runtime behavior, help text content, and completion generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/commands_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/completion.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/completion.go

## Purpose

Generates bash, zsh, and fish completion scripts from the Kubo command tree.

## Important APIs, Types, and Functions

`completionCommand` and `singleOption` are template models. `commandToCompletions` converts a `cmds.Command` tree into sorted subcommands and option buckets. `writeBashCompletions`, `writeFishCompletions`, and `writeZshCompletions` execute templates initialized in `init`.

## Control Flow

`commandToCompletions` recursively parses subcommands, separates boolean options as flags from value options, records short and long names, and sorts names for deterministic template output. Templates define shell-specific functions that skip flags, descend subcommands, and complete options or subcommands based on current position.

## State and Persistence Behavior

No persistent state. Package-level templates are parsed once at initialization and reused.

## Dependencies and Integration Points

Depends on `text/template` and `go-ipfs-cmds` option metadata. Called from `CompletionCmd` in `commands.go`.

## Risks and Edge Cases

Template quoting is sensitive to option descriptions and subcommand names. Zsh generation reuses bash completion through `bashcompinit`. Fish predicates model subcommand traversal and may drift from command parser behavior.

## Test Signals

No dedicated tests here. Command tree tests indirectly ensure the completion command is registered. Useful tests would snapshot generated scripts for representative command trees and descriptions with quotes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/completion.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/config.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/config.go

## Purpose

Implements `ipfs config` commands for reading, setting, showing, editing, replacing, and applying profile transforms to the repo config while protecting secrets.

## Important APIs, Types, and Functions

`ConfigCmd` handles key get/set with `--bool`, `--json`, and `--expand-auto`. `configShowCmd`, `configEditCmd`, `configReplaceCmd`, and `configProfileApplyCmd` are subcommands. Helpers include `matchesGlobPrefix`, `scrubValue`, `scrubOptionalValue`, `transformConfig`, `getConfigWithAutoExpand`, `setConfig`, `parseEditorCommand`, `replaceConfig`, and `getRemotePinningServices`.

## Control Flow

The main command blocks direct identity private-key and remote-pinning credential access, opens fsrepo, and either writes parsed JSON/bool/string values or reads config values with optional AutoConf expansion. `show` reads the config file, optionally expands auto placeholders through full config methods, scrubs identity, API auth, and pinning secrets, then emits JSON. `profile apply` clones config, applies a named transform, backs up and persists unless dry-run, and emits a scrubbed diff. `replace` decodes a whole config, preserves the existing private key, and refuses remote pinning service API changes or add/remove attempts.

## State and Persistence Behavior

Set operations call `SetConfigKey`; profile apply creates a backup and calls `SetConfig`; replace calls `SetConfig`. `edit` runs `$EDITOR` against the config file directly. Read/show/dry-run paths do not persist changes.

## Dependencies and Integration Points

Uses Kubo config model, profile registry, AutoConf expansion methods, repo/fsrepo, `jsondiff`, `go-shlex`, and command file helpers. Integrates with global `ConfigFileOption` and shared `configExpandAutoName`.

## Risks and Edge Cases

Secret scrubbing is security critical. `replace` must preserve existing secrets while refusing attempts to alter concealed remote-service API info. `$EDITOR` parsing must handle quoted paths and flags. `--expand-auto` is read-only and is rejected for writes.

## Test Signals

`config_test.go` covers scrub deletion behavior and editor parsing cases. Additional tests should cover secret access blocking, remote pinning replace constraints, AutoConf expansion, profile backup behavior, and JSON/bool type persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/config_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/config_test.go

## Purpose

Tests focused helper behavior for config scrubbing and `$EDITOR` command parsing.

## Important APIs, Types, and Functions

`TestScrubMapInternalDelete` exercises `scrubMapInternal`. `TestEditorParsing` table-tests `parseEditorCommand` with common editors, flags, quoted paths, and a malformed trailing backslash.

## Control Flow

The scrub test calls `scrubMapInternal(nil, nil, true)` and expects an empty non-nil map. Editor parsing subtests call the parser, branch on expected error, and compare argument slices element by element.

## State and Persistence Behavior

Pure unit tests. They do not open or mutate repo config.

## Dependencies and Integration Points

Coupled to `go-shlex` parsing semantics through `parseEditorCommand`.

## Risks and Edge Cases

The tests do not execute editors or validate config file edits. They cover POSIX-like parsing but not Windows shell quoting.

## Test Signals

Good signal for issue-prone `$EDITOR` values such as VS Code with `--wait`. Missing signal for the core config read/write/replace security paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/dag.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dag/dag.go

## Purpose

Defines the `ipfs dag` command family and shared output types for IPLD DAG put, get, resolve, import, export, and stat.

## Important APIs, Types, and Functions

`DagCmd` registers all DAG subcommands. Output types include `OutputObject`, `ResolveOutput`, `CarImportStats`, `CarImportOutput`, `RootMeta`, `DagStat`, and `DagStatSummary`. Command variables configure help, arguments, options, encoders, and post-run hooks for `DagPutCmd`, `DagGetCmd`, `DagResolveCmd`, `DagImportCmd`, `DagExportCmd`, and `DagStatCmd`.

## Control Flow

This file primarily wires handlers implemented in sibling files. Encoders handle CID base selection, import root/status formatting, and DAG stat tabular/JSON output. `DagResolveCmd` infers CID output base from the input path unless `--cid-base` is explicitly set. `DagImportCmd` exposes pin, local-only, stats, and fast-provide knobs, with text output validating event shape.

## State and Persistence Behavior

The state effects are in sibling handlers: DAG put/import write blocks and may pin/provide, export/get/stat/resolve read DAG state. This file defines command metadata and output formatting only.

## Dependencies and Integration Points

Uses `go-ipfs-cmds`, CID encoders, `cmdutils.AllowBigBlockOption`, human-size formatting, CSV/JSON encoders, and constants shared by DAG sibling files.

## Risks and Edge Cases

Event encoders assume import events contain exactly one of `Root` or `Stats`. `DagStatSummary.calculateSummary` divides by total size and assumes nonzero traversal. CID-base inference in resolve intentionally falls back if path extraction fails.

## Test Signals

Command tree tests cover DAG subcommand registration. Behavior coverage should target each sibling handler plus text/JSON encoders for import and stat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/dag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/export.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dag/export.go

## Purpose

Implements `ipfs dag export`, streaming a selected DAG as CARv1, with optional best-effort local-only export and CLI progress.

## Important APIs, Types, and Functions

`dagExport` is the command handler. `exportPartialCAR` writes a partial CAR from the raw local blockstore. `finishCLIExport` handles CLI stream/progress output. `dagStore` adapts CoreAPI DAG reads to go-car storage, and `cidFromBinString` decodes CAR storage keys.

## Control Flow

The handler parses a CID/path, validates `--local-only` versus explicit `--offline=false`, obtains API, forces offline API for local-only, stats the root block, and starts a goroutine that writes CAR data to an `io.Pipe`. Normal export uses `gocar.TraverseV1` over a link system backed by `dagStore`. Local-only export uses `exportPartialCAR`, which writes the root header and walks links from the raw blockstore, skipping missing/unreadable subtrees. The response emits the pipe as `application/vnd.ipld.car` and waits for the writer error.

## State and Persistence Behavior

Read-only. Normal export may fetch missing blocks through DAG API when online. Local-only export is structurally limited to local blockstore reads and does not fetch.

## Dependencies and Integration Points

Uses CoreAPI, boxo blockstore/walker, go-car v2, IPLD link systems, selector traversal, `cmdenv`, `cmdutils`, and progress helpers.

## Risks and Edge Cases

Pipe error handling must avoid losing writer-side failures after client emit. Local-only silently skips unavailable subtrees by design, producing incomplete CARs. Normal export decorates offline not-found errors for user clarity. CLI post-run rejects unexpected multipart responses.

## Test Signals

No local tests in this subset. Useful tests include local-only skip semantics, `--offline=false` conflict, missing root failure, writer error propagation, and CAR content-type behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/get.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dag/get.go

## Purpose

Implements `ipfs dag get`, resolving an IPLD path and serializing the target node in a requested output codec.

## Important APIs, Types, and Functions

`dagGet(req, res, env)` is the handler. It uses `output-codec`, CoreAPI `ResolvePath`, `Dag().Get`, IPLD legacy `UniversalNode`, `traversal.Get`, and multicodec encoder lookup.

## Control Flow

The handler obtains CoreAPI, parses the output multicodec, converts the input to a path, resolves root plus remainder, fetches the root DAG node, casts it to a universal IPLD node, traverses any remainder path, looks up the requested encoder, and streams encoded output through an `io.Pipe`.

## State and Persistence Behavior

Read-only. It may fetch DAG blocks through CoreAPI depending on online/offline request state.

## Dependencies and Integration Points

Depends on boxo path conversion, `go-ipld-legacy`, IPLD prime traversal and multicodec registries, `cmdenv`, and `cmdutils`.

## Risks and Edge Cases

The fetched object must implement `ipldlegacy.UniversalNode`; unsupported node implementations error. Encoder errors occur in the goroutine and are propagated through `CloseWithError`. Remainder traversal can fail on schema/path mismatches.

## Test Signals

No direct tests. Good coverage would include codec lookup failures, path remainder traversal, unsupported node type, and pipe error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/get.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/import.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dag/import.go

## Purpose

Implements `ipfs dag import`, importing CAR blocks into the local DAG/blockstore, optionally pinning roots, emitting stats, and triggering fast provider announcements.

## Important APIs, Types, and Functions

`dagImport` is the handler. It uses CARv2 `NewBlockReader`, legacy IPLD node decoding, `ipld.Batch`, `cmdutils.CheckBlockSize`, root pinning through `node.Pinning`, and `cmdenv.ExecuteFastProvideRoot`/`ExecuteFastProvideDAG`.

## Control Flow

The handler loads node config and forces an offline API for import-time pinning. It resolves defaults for `--pin-roots`, `--local-only`, and fast-provide flags from CLI or config. If pinning, it takes the blockstore pin/GC lock. It iterates input files, hides `io.Seeker` to force sequential CAR reading, records CAR header roots, validates block sizes, decodes blocks into IPLD nodes, batches them, and commits. After import, it optionally pins each root, emits stats, and either fast-provides the full DAG or root CIDs.

## State and Persistence Behavior

Writes imported blocks to the local DAG/blockstore. Optional root pinning updates pinner state and flushes it. Fast provide publishes provider records to the network. `--local-only` implies no root pinning because partial CARs may not contain complete DAGs.

## Dependencies and Integration Points

Depends on node blockstore, pinner, provider, import config batch limits, CARv2 reader, CoreAPI DAG, config defaults, and command file iterators.

## Risks and Edge Cases

Import is not transactional; partial blocks may persist if later blocks fail. Pinning happens after all files are processed so multi-file DAGs can work, but pin failures are reported per root. Truncated CAR errors include previous/current block context. Fast-provide async errors are logged, not returned.

## Test Signals

No direct tests in this subset. Regression targets include partial CAR import, pin-root conflicts with local-only, batch commit failures, malformed/truncated CAR messages, block-size rejection, stats emission, and fast-provide option resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/put.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dag/put.go

## Purpose

Implements `ipfs dag put`, decoding input IPLD data, re-encoding it with a storage codec, hashing it, adding it to the DAG service, and optionally pinning it.

## Important APIs, Types, and Functions

`dagPut` is the handler. Important options are `input-codec`, `store-codec`, `hash`, `pin`, and `allow-big-block`. It uses IPLD prime multicodec lookup, `cid.Prefix`, `blocks.NewBlockWithCid`, and `ipldlegacy.LegacyNode`.

## Control Flow

The handler gets CoreAPI and node config, chooses default hash from import config, parses multicodec codes, builds a CID prefix, looks up decoder and encoder, chooses a pinning or non-pinning DAG adder, and creates a batch. For each input file it decodes to an IPLD node, encodes storage bytes, computes the CID, constructs a legacy node, checks block size, adds it to the batch, and emits the CID. Finally it commits the batch.

## State and Persistence Behavior

Writes new DAG blocks and optionally pins them when `--pin` is set. Batch commit persists the additions.

## Dependencies and Integration Points

Uses CoreAPI DAG service, node repo import config, IPLD prime codecs, legacy node wrapper, command file iterators, and shared block-size safety.

## Risks and Edge Cases

Unsupported codecs or hashes fail before import. Batch add/commit errors can occur after some emitted CIDs, so clients should treat command failure as potentially partial. Oversized blocks are rejected unless explicitly allowed.

## Test Signals

No direct tests. Good tests include codec combinations, hash defaults, pinning path, multiple files, malformed input, and `--allow-big-block`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/put.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/resolve.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dag/resolve.go

## Purpose

Implements the core handler for `ipfs dag resolve`, resolving a path to the deepest resolved root CID plus unresolved remainder.

## Important APIs, Types, and Functions

`dagResolve(req, res, env)` gets CoreAPI, parses the path through `cmdutils.PathOrCidPath`, calls `api.ResolvePath`, and emits `ResolveOutput`.

## Control Flow

The handler resolves the path under the request context and converts the remainder segments into a path string with `path.SegmentsToString`.

## State and Persistence Behavior

Read-only. It may fetch path-resolution data depending on CoreAPI online/offline mode.

## Dependencies and Integration Points

Depends on boxo path utilities, `cmdenv`, `cmdutils`, and the `ResolveOutput` encoder defined in `dag.go`.

## Risks and Edge Cases

Invalid paths fail before API resolution. Remainders are returned rather than traversed further, so callers must distinguish fully resolved CIDs from partial paths.

## Test Signals

No direct tests. Useful coverage includes CID-only paths, paths with remainders, invalid path errors, and CID-base formatting through the encoder in `dag.go`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/resolve.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/stat.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dag/stat.go

## Purpose

Implements `ipfs dag stat`, traversing one or more DAG roots and reporting per-root and aggregate block/size statistics.

## Important APIs, Types, and Functions

`dagStat` traverses DAGs. `finishCLIStat` filters progressive updates and emits the final summary. It uses `DagStatSummary` and `DagStat` from `dag.go`, `merkledag.NewSession`, and boxo `traverse.Traverse`.

## Control Flow

The handler defaults progressive emission to true unless `--progress` is specified. It resolves each root, rejects path remainders, fetches the root node, appends a per-root stat entry, and traverses DFS with duplicate skipping. For a single root it avoids an extra command-level CID set to reduce memory; for multiple roots it uses a set to count cross-root unique blocks. It emits progress summaries during traversal, computes final unique/shared/ratio values, and emits the final summary.

## State and Persistence Behavior

Read-only. Traversal may fetch DAG blocks via CoreAPI depending on request mode.

## Dependencies and Integration Points

Uses `cmdenv.GetCidEncoder`, `cmdutils.PathOrCidPath`, boxo merkledag sessions/traversal, humanize output, and `e.TypeErr`.

## Risks and Edge Cases

Large DAG traversal can be expensive; the single-root memory optimization avoids duplicating boxo's seen set. Ratio calculation assumes total size is nonzero. CLI progress treats `Ratio == 0` as progress, so unusual final zero-size DAGs need care.

## Test Signals

No direct tests. Important tests include duplicate blocks within and across roots, progress on/off, path remainder rejection, missing blocks, and huge-DAG memory behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/stat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dht.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dht.go

## Purpose

Defines deprecated `ipfs dht` compatibility commands, keeping only direct DHT closest-peer query while routing users to `ipfs routing` for removed operations.

## Important APIs, Types, and Functions

`DhtCmd` registers deprecated subcommands. `ErrNotDHT` reports missing active DHT. `kademlia` is a local interface requiring `GetClosestPeers`. `queryDhtCmd` performs the query. `RemovedDHTCmd` returns a removed-command error for findprovs/findpeer/get/put/provide.

## Control Flow

`queryDhtCmd` gets the node, checks active DHT, decodes the input peer ID, registers routing query events, selects WAN or LAN DHT client when the dual DHT is present, runs `GetClosestPeers` in a goroutine, publishes final peer events, streams query events until the event channel closes, and returns the goroutine error.

## State and Persistence Behavior

Read-only relative to repo state. It performs DHT network queries and emits routing events.

## Dependencies and Integration Points

Depends on libp2p routing query events, peer IDs, Kubo node DHT fields, and event printers such as `printEvent`/`pfuncMap` defined elsewhere.

## Risks and Edge Cases

The command is deprecated, so behavior must remain compatible while steering users elsewhere. DHT client selection falls back to LAN if WAN is inactive. If the client does not implement `GetClosestPeers`, it fails explicitly.

## Test Signals

`dht_test.go` covers key-translation helper behavior from related DHT/routing code, not this query path. Command tree tests verify deprecated subcommand registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dht.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dht_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dht_test.go

## Purpose

Tests DHT key translation behavior for public key and IPNS routing keys.

## Important APIs, Types, and Functions

`TestKeyTranslation` generates a random peer ID, computes expected namesys public-key routing key and IPNS routing key, and compares them to `escapeDhtKey` outputs.

## Control Flow

The test builds `/pk/<peer>` and `/ipns/<peer>` paths, passes them to `escapeDhtKey`, fails on errors, and compares exact strings.

## State and Persistence Behavior

Pure test; no repo or network state.

## Dependencies and Integration Points

Uses boxo namesys, IPNS name routing keys, and libp2p test peer generation. `escapeDhtKey` is defined outside the listed source but is exercised by this test file.

## Risks and Edge Cases

The test is focused on two key namespaces and does not cover invalid keys or the deprecated query command in `dht.go`.

## Test Signals

Strong signal that DHT key escaping remains compatible with namesys/IPNS routing expectations. Limited signal for command runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dht_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/diag.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/diag.go

## Purpose

Defines diagnostic commands for daemon health and low-level datastore inspection/mutation.

## Important APIs, Types, and Functions

`DiagCmd` registers `sys`, `cmds`, `profile`, `datastore`, and `healthy`. `diagHealthyCmd` probes shutdown state and built-in DAG resolution. `openDiagDatastore` opens the repo datastore and mounts provider keystore datastores. `diagDatastoreGetCmd`, `diagDatastorePutCmd`, and `diagDatastoreCountCmd` expose raw datastore get/put/count. Result types include `diagDatastoreGetResult` and `diagDatastoreCountResult`.

## Control Flow

Health checks fail if shutdown has started, then resolve and fetch a built-in empty UnixFS directory CID. Datastore commands are `NoRemote` and guarded by `DaemonNotRunning`; they open fsrepo directly, mount extra provider stores if present, perform the requested datastore operation, and close all stores. `get --hex` formats a hex dump; otherwise it writes raw bytes.

## State and Persistence Behavior

`healthy` is read-only. `diag datastore get/count` are read-only. `diag datastore put` writes raw bytes to a datastore key and syncs it, which can directly mutate repo internals while the daemon is stopped.

## Dependencies and Integration Points

Uses shutdown state, CoreAPI DAG/path operations, fsrepo, datastore/mount/query packages, node provider keystore mounting, and command text encoders.

## Risks and Edge Cases

Datastore commands are explicitly debugging-only and can corrupt repo state if misused. Opening repo while daemon runs is blocked by `DaemonNotRunning`. Health probe isolates DAG/blockstore pipeline but does not prove network health.

## Test Signals

No direct tests in this subset. Useful tests include shutdown health failure, missing/corrupt probe behavior, datastore not-found messages, hex output, put sync errors, and provider keystore mount inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/diag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/e/error.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/e/error.go

## Purpose

Provides small error helpers for command handlers and post-run code.

## Important APIs, Types, and Functions

`TypeErr(expected, actual)` returns a type mismatch error. `HandlerError` wraps an error with a debug stack. `New(err)` constructs `HandlerError`.

## Control Flow

`TypeErr` formats expected and actual dynamic types. `HandlerError.Error` prints the wrapped error plus stack trace. A compile-time assignment verifies `HandlerError` implements `error`.

## State and Persistence Behavior

No persistent state. `New` captures the current goroutine stack at construction time.

## Dependencies and Integration Points

Uses standard `fmt` and `runtime/debug`. Used by post-run handlers such as `get.go` and `filestore.go` when response values have unexpected types.

## Risks and Edge Cases

`New(nil)` is valid by compile check but calling `Error` on a nil wrapped error would panic. Stack traces may be verbose for user-facing output if surfaced directly.

## Test Signals

No direct tests. Coverage should include expected formatting and nil handling expectations if callers can pass nil.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/e/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/external.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/external.go

## Purpose

Creates placeholder commands that delegate to external binaries named after the `ipfs` command path.

## Important APIs, Types, and Functions

`ExternalBinary(instructions string) *cmds.Command` returns a command with variadic `args`, `External: true`, `NoRemote: true`, and a run handler that locates and executes the external binary.

## Control Flow

The handler builds `ipfs-<path-components>` as the binary name. If missing and the user requested `--help` or `-h`, it emits explanatory help with installation instructions; otherwise it errors. If installed, it creates an `io.Pipe`, starts the process with arguments, discards stdin, combines stdout/stderr into the pipe writer, emits the pipe reader, waits for the process in a goroutine, and returns the process exit error.

## State and Persistence Behavior

Does not mutate repo state directly. It executes a local process that may have arbitrary side effects outside this code's control.

## Dependencies and Integration Points

Uses `os/exec`, process environment, pipes, and go-ipfs-cmds external command metadata.

## Risks and Edge Cases

Stdin is intentionally not passed through. Stdout and stderr are merged, losing stream distinction. External process behavior and side effects are outside command framework guarantees.

## Test Signals

No direct tests. Useful tests would mock PATH for missing/help behavior, successful streaming, nonzero exit status, and binary naming from nested paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/external.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/extra.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/extra.go

## Purpose

Defines typed metadata flags stored in `cmds.Extra` to influence command pre-hooks and repo/config usage.

## Important APIs, Types, and Functions

`CreateCmdExtras` builds an extra value from option functions. `SetDoesNotUseRepo`/`GetDoesNotUseRepo`, `SetDoesNotUseConfigAsInput`/`GetDoesNotUseConfigAsInput`, and `SetPreemptsAutoUpdate`/`GetPreemptsAutoUpdate` manage boolean flags. `getBoolFlag` is the shared extractor.

## Control Flow

Setter functions close over a typed zero-size key and call `Extra.SetValue`. Getter functions retrieve with the same key and type assert the stored value to bool.

## State and Persistence Behavior

Only in-memory command metadata is affected. No repo state is read or written.

## Dependencies and Integration Points

Depends on `go-ipfs-cmds`. Used across command definitions for repo-independent commands such as `cid`, `commands`, and recovery commands.

## Risks and Edge Cases

`getBoolFlag` type asserts without checking the value type; only the paired setters should store these keys. Misusing key types or direct `Extra.SetValue` can panic.

## Test Signals

No direct tests. Command behavior indirectly depends on these flags in pre-hook code outside this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/extra.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/files.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/files.go

## Purpose

Implements the `ipfs files` command family for MFS (Mutable File System) operations: read, write, move, copy, list, mkdir, stat, rm, flush, CID format changes, chmod, touch, and recovery chroot.

## Important APIs, Types, and Functions

`FilesCmd` registers all MFS subcommands and the shared `--flush` option. `updateNoFlushCounter` enforces `Internal.MFSNoFlushLimit`. Major handlers include `filesStatCmd`, `filesCpCmd`, `filesLsCmd`, `filesReadCmd`, `filesMvCmd`, `filesWriteCmd`, `filesMkdirCmd`, `filesFlushCmd`, `filesChcidCmd`, `filesRmCmd`, `filesChmodCmd`, `filesTouchCmd`, and `filesChrootCmd`. Helpers include `statNode`, `walkBlock`, `getNodeFromPath`, `getPrefix`, `checkPath`, `getFileHandle`, and `removePath`.

## Control Flow

Handlers validate absolute MFS paths with `checkPath`, get the node through `cmdenv`, and operate on `nd.FilesRoot`. Mutating commands call `updateNoFlushCounter` unless they always flush. `stat` resolves a node, computes UnixFS metadata, and optionally walks an offline DAGService to report local availability. `cp` supports lazy `/ipfs/` to MFS references, validates root codecs as UnixFS dag-pb or raw, optionally creates parents, force-unlinks files, puts the node, and flushes target plus parent. `write` opens or creates a file, applies CID/hash/raw-leaf options, seeks/truncates/limits input, copies bytes, closes, and flushes parent. `rm` rejects `--flush=false`, removes one or more paths, and emits per-path errors before returning aggregate failure.

## State and Persistence Behavior

Most commands mutate MFS DAG state and, when flush is true, persist updated roots and clear parent caches. `--flush=false` defers durability and increments a global unflushed operation counter. `files flush` persists a path and resets the counter. `files chroot` opens the repo while the daemon is stopped and directly rewrites `node.FilesRootDatastoreKey`, making it a recovery-grade persistent mutation.

## Dependencies and Integration Points

Uses boxo MFS, UnixFS, merkledag, blockstore, offline exchange, Kubo config/import defaults, fsrepo/datastore, CoreAPI resolution, CID/multihash builders, and command environment helpers. Integrates with GC safety through MFS root persistence and with import config for CID/hash/HAMT directory behavior.

## Risks and Edge Cases

`--flush=false` trades consistency for speed and can lose data on daemon crash before flush. The global no-flush counter is process-wide and caches the config limit on first use. Lazy `cp` can protect partial DAGs from GC without fetching full content. `files chroot` is destructive and requires confirmation but bypasses live MFS machinery. Race conditions are acknowledged around created file type checks.

## Test Signals

`files_test.go` covers rejection of non-UnixFS dag-cbor-like copy roots. Command tree tests cover subcommand registration. Important missing tests include no-flush limit behavior, parent flushing, write/truncate/count combinations, rm aggregate errors, chcid root rejection, stat locality, chmod/touch metadata, and chroot validation/persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/files.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/files_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/files_test.go

## Purpose

Tests that `ipfs files cp` rejects a copied DAG root that is not valid UnixFS.

## Important APIs, Types, and Functions

`TestFilesCp_DagCborNodeFails` constructs a mock command context and node, creates a protobuf DAG node with invalid UnixFS data, adds it to the DAG, and runs `filesCpCmd.Run`.

## Control Flow

The test builds a request copying `/ipfs/<cid>` to `/test-destination`, creates a writer response emitter, invokes the command with the mock context, and asserts the returned error contains the UnixFS validation message.

## State and Persistence Behavior

Uses an in-memory/mock node DAG. It writes a test node to the mock DAG but does not persist repo state.

## Dependencies and Integration Points

Depends on `core/mock`, boxo merkledag, command response emitters, and the `filesCpCmd` UnixFS validation path.

## Risks and Edge Cases

The test targets invalid dag-pb data, not every invalid codec path. It does not test valid raw or valid dag-pb copies, force behavior, or parent creation.

## Test Signals

Strong signal for the security/validity guard introduced around lazy MFS copy. Limited signal for broader MFS command behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/files_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/filestore.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/filestore.go

## Purpose

Implements `ipfs filestore` commands for listing, verifying, deleting bad filestore links, and finding duplicate blocks stored both in filestore and main blockstore.

## Important APIs, Types, and Functions

`FileStoreCmd` registers `ls`, `verify`, and `dups`. `lsFileStore`, `verifyFileStore`, and `dupsFileStore` are handlers. `getFilestore` obtains the enabled filestore from the node. `listByArgs` verifies requested CIDs and optionally removes bad blocks.

## Control Flow

List and verify handlers get the filestore, branch between explicit CID arguments and full scans, stream `filestore.ListRes` entries, and use CLI post-runs for formatted text with CID encoder support. `verify` optionally deletes bad blocks for statuses other than ok and other-error. `dups` iterates filestore keys and checks whether each also exists in the main blockstore, emitting refs.

## State and Persistence Behavior

`ls` and `dups` are read-only. `verify --remove-bad-blocks` mutates filestore metadata by deleting bad block links, with a warning that pinned data may be affected.

## Dependencies and Integration Points

Uses boxo filestore, Kubo node filestore/main blockstore, CID decoding, shared CID encoders, `refsEncoderMap`, and `streamResult`.

## Risks and Edge Cases

Filestore must be enabled or commands fail with `ErrFilestoreNotEnabled`. Removing bad blocks can affect pinned data and requires follow-up pin verification. Explicit invalid CIDs are emitted as per-entry errors rather than failing the whole command immediately.

## Test Signals

No direct tests. Useful tests include disabled filestore, explicit CID invalid/error statuses, full scan ordering, remove-bad-blocks action text, and duplicate detection errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/filestore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/get.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/get.go

## Purpose

Implements `ipfs get`, fetching UnixFS content and writing it to disk as extracted files, tar archives, or gzip-compressed streams.

## Important APIs, Types, and Functions

`GetCmd` defines output, archive, compress, compression-level, and progress options. Helpers include `getCompressOptions`, `getOutPath`, `getWriter.Write`, `writeArchive`, `writeExtracted`, `fileArchive`, `newMaybeGzWriter`, `progressBarForReader`, and `makeProgressBar`.

## Control Flow

`PreRun` validates compression options. The handler resolves the path, fetches UnixFS content, sets response length, wraps content into a tar or gzip stream with `fileArchive`, closes the reader on context cancellation, sets content type, and emits the stream. The CLI post-run receives the stream, computes output path, resolves compression/archive/progress options, and writes either an archive file or extracted files through a tar extractor.

## State and Persistence Behavior

The handler is read-only against IPFS data but the CLI post-run writes files to the local filesystem using `os.Create` or tar extraction. It may fetch blocks from the network unless offline.

## Dependencies and Integration Points

Uses CoreAPI UnixFS, boxo files/tar, gzip, archive/tar PAX format, shared progress helpers, command response streams, and `cmdutils.PathOrCidPath`.

## Risks and Edge Cases

Compression level is valid only 1 through 9 when compression is enabled. Without `--archive` and without compression, data is still transported internally as tar and then extracted. Output path defaults to the final path component and can be overridden. Context cancellation closes the generated reader to stop background goroutines.

## Test Signals

`get_test.go` covers default and explicit output path selection. Missing tests include compression validation, archive filename suffixing, extraction errors, progress behavior, and context cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/get.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/get_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/get_test.go

## Purpose

Tests default and explicit local output path selection for `ipfs get`.

## Important APIs, Types, and Functions

`TestGetOutputPath` constructs command requests for `GetCmd` and calls `getOutPath`.

## Control Flow

Table cases cover explicit `--output`, trailing slashes, nested path final components, and extra ignored arguments. Each case builds a request with `cmds.NewRequest` and compares the computed path.

## State and Persistence Behavior

Pure unit test. It does not fetch or write files.

## Dependencies and Integration Points

Depends on `GetCmd` option parsing and command request construction.

## Risks and Edge Cases

The test covers path naming only, not path traversal, filesystem errors, or archive/compression suffix behavior.

## Test Signals

Good signal for user-visible default output naming. Limited signal for the main data transfer path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/get_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/helptext_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/helptext_test.go

## Purpose

Recursively checks that commands have help taglines.

## Important APIs, Types, and Functions

`checkHelptextRecursive` calls `ProcessHelp`, skips external commands, and runs subtests for help fields. `TestHelptexts` starts from `Root`.

## Control Flow

For each command it verifies `Helptext.Tagline` is non-empty. Checks for long description, short description, and synopsis exist but are skipped. It then recurses into subcommands.

## State and Persistence Behavior

Pure metadata test.

## Dependencies and Integration Points

Uses the global `Root` command tree and go-ipfs-cmds help processing.

## Risks and Edge Cases

Skipped subtests mean only taglines are enforced. External commands are skipped to avoid requiring generated or plugin help.

## Test Signals

Good lightweight signal that command additions include a tagline. Weak signal for full help quality and option documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/helptext_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/id.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/id.go

## Purpose

Implements `ipfs id`, printing local or remote peer identity, public key, addresses, agent version, and protocol registrations with configurable peer ID base.

## Important APIs, Types, and Functions

`IDCmd` defines `peerid`, `--format`, and `--peerid-base`. `IdOutput` is the response. `printPeer` extracts peerstore information for a remote/local peer. `printSelf` gathers identity from the local node and host. `offlineIDErrorMessage` explains remote lookup limits without a daemon.

## Control Flow

The handler builds a `keyencode.KeyEncoder`, gets the node, chooses the requested peer or local identity, and either prints self directly or handles remote lookup. Remote lookup requires online mode unless `--offline` is set; online mode connects to the peer so identify data populates the peerstore. Text encoding either applies a token replacement format string or emits indented JSON.

## State and Persistence Behavior

Read-only for repo state. Online remote lookup may initiate libp2p connection and update peerstore metadata. Offline mode only formats existing peerstore data.

## Dependencies and Integration Points

Uses Kubo version, node host/peerstore, libp2p peer IDs, peerstore protocols, crypto public-key marshaling, kbucket lookup errors, key encoding, and display sanitization.

## Risks and Edge Cases

Remote `id` without daemon fails with a specific guidance message. AgentVersion and protocols are sanitized to avoid unsafe display. Format string replacement is simple token substitution and supports escaped newline/tab sequences, not a full template language.

## Test Signals

No direct tests in this subset. Useful coverage includes peerid-base variants, offline remote behavior, kb lookup failure mapping, sanitization of peerstore strings, and custom format output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/id.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/keyencode/keyencode.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/keyencode/keyencode.go

## Purpose

Provides peer/IPNS key encoding helpers for command output, supporting legacy base58 multihash and multibase CID forms.

## Important APIs, Types, and Functions

`OptionIPNSBase` defines the `--ipns-base` option defaulting to base36. `KeyEncoder` wraps an optional multibase encoder. `KeyEncoderFromString` parses labels, and `FormatID` formats a `peer.ID`.

## Control Flow

`KeyEncoderFromString` returns a zero encoder for `b58mh` and `v0`, preserving legacy `peer.ID.String()` output. For any other label it looks up a multibase encoder and stores it. `FormatID` either returns the legacy peer ID string or converts the peer ID to a CID and renders it in the requested base.

## State and Persistence Behavior

Pure formatting helper. No repo or network state.

## Dependencies and Integration Points

Uses `go-ipfs-cmds`, libp2p peer IDs, and multibase. `id.go` uses equivalent logic for `--peerid-base`; IPNS/name commands use `OptionIPNSBase`.

## Risks and Edge Cases

`FormatID` panics if `StringOfBase` fails, relying on prior encoder validation and valid peer IDs. Legacy labels are special-cased and do not use multibase.

## Test Signals

No direct tests in this subset. Useful tests include legacy labels, invalid base labels, base36/base32 output, and panic-free formatting for generated peer IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/keyencode/keyencode.go -->
