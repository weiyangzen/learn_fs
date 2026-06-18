# subset-b-007595 Research

Grouped source research for Kubo command handlers covering key management, logging, UnixFS listing, mount variants, multibase utilities, IPNS/name operations, legacy object commands, p2p tunnels, pinning, ping/profile/provide/pubsub/refs/repo maintenance. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/keystore.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/keystore.go

## Purpose

`keystore.go` defines the `ipfs key` command tree for creating, importing, exporting, listing, renaming, removing, rotating, signing with, and verifying named libp2p/IPNS keys. It bridges user-facing command syntax to the Kubo CoreAPI key service for daemon-safe operations, and to direct filesystem repo access for commands that must work offline or without a running daemon.

## Important APIs, Types, and Functions

The root `KeyCmd` registers `gen`, `export`, `import`, `ls`, deprecated `list`, `rename`, `rm`, `rotate`, `sign`, and `verify`. Output structs are `KeyOutput`, `KeyOutputList`, `KeyRenameOutput`, `KeySignOutput`, and `KeyVerifyOutput`. Key-format constants distinguish `libp2p-protobuf-cleartext` from `pem-pkcs8-cleartext`; key type/size options are shared with CoreAPI key generation. `doRotate` is the direct repo mutation helper that backs up the old identity and writes a new identity into config. `DaemonNotRunning` checks repo locking before rotation.

## Control Flow

Most live key operations call `cmdenv.GetApi` and then `api.Key()` methods. `key gen` validates the requested name and type/size, creates a key, and formats its peer ID with the requested IPNS base. `key export` is `NoRemote`; it checks repo version, opens the filesystem keystore read-only, formats the private key bytes, and its CLI post-run writes a `0600` output file. `key import` reads a file/stdin, decodes PEM or libp2p protobuf, optionally rejects non-RSA/non-Ed25519 keys, opens the repo, checks for duplicate names, persists into the keystore, and emits the derived peer ID. Rename/remove/list delegate to CoreAPI. Rotate opens the repo directly after confirming the daemon is not running, stores the old identity under a user-supplied keystore name, and rewrites config identity. Sign/verify read data from file/stdin, use CoreAPI signing/verification, and multibase-encode or decode signatures.

## State and Persistence Behavior

Generated/imported/renamed/removed keys persist in the repo keystore. `export` emits private key material to a user-selected file but does not mutate repo state. `rotate` mutates both keystore and config identity and is intentionally local-only. Sign/verify are read-only except for transient data in memory. CLI text encoders escape non-printable key names but signatures and private key bytes must still be treated as sensitive.

## Dependencies and Integration Points

This file depends on `go-ipfs-cmds`, Kubo `cmdenv`, `coreiface/options`, repo/fsrepo and migrations, boxo keystore, libp2p crypto/peer, multibase, Go `x509`/`pem`, and `keyencode` for IPNS base selection. It integrates with `ipfs name publish` through generated key names and peer IDs, and with repo migration/version compatibility through `fsrepo.RepoVersion`.

## Risks and Test Signals

High-risk behavior includes exporting cleartext private keys, importing arbitrary key types with `--allow-any-key-type`, direct repo locking during rotate/import/service operations, and PEM/std-key conversion edge cases for Ed25519 pointer/value handling. Tests should cover duplicate names, the protected `self` name, repo version mismatch on export, default output file permissions, PEM hints on wrong import format, disallowed key types, rotate with daemon lock present, signature round trips, multibase decode errors, and IPNS base formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/keystore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/log.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/log.go

## Purpose

`log.go` implements `ipfs log`, giving operators runtime control over go-log subsystem levels, subsystem discovery, and streaming daemon log output. It complements environment-variable logging configuration with RPC-visible commands.

## Important APIs, Types, and Functions

`LogCmd` exposes `level`, `ls`, and `tail`. `logLevelOutput` carries either a `Levels` map or a human message. Constants model the wildcard subsystem (`*`), convenient alias (`all`), current default keyword, default subsystem display key, and tail log-level option. The implementation uses `logging.SetLogLevel`, `logging.DefaultLevel`, `logging.SubsystemLevelNames`, `logging.SubsystemLevelName`, `logging.GetSubsystems`, and `logging.NewPipeReader`.

## Control Flow

`log level` parses optional subsystem and level arguments. The `all` alias is normalized to `*` for setting. When a level is supplied, `default` is resolved to the current default level and `SetLogLevel` mutates runtime state. Without a level, no subsystem returns only the default fallback, wildcard/all returns all configured subsystem levels with `(default)` substituted for the internal default key, and a named subsystem returns a single entry. The text encoder prints messages directly, then sorts map output. It shows subsystem names only for JSON/RPC-like calls or multi-entry output. `log ls` emits known subsystem names. `log tail` creates a pipe reader, optionally filtered by parsed level, closes it on request cancellation, and emits the reader as a streaming response.

## State and Persistence Behavior

Level changes are process-local runtime logging state and do not persist to config. `tail` holds a live pipe reader until cancellation. `ls` and level queries are read-only. There is no repo mutation.

## Dependencies and Integration Points

The command depends on `go-ipfs-cmds`, `go-log/v2`, and shared `stringList` formatting defined elsewhere in the commands package. It is `NoLocal` for `level`, reflecting daemon-side logging state, and integrates with RPC encodings where JSON consumers need structured subsystem names.

## Risks and Test Signals

Risks include ambiguity between default fallback and wildcard all-subsystem updates, shell escaping of `*`, and long-lived tail streams that must close when contexts cancel. Tests should cover `all`/`*` equivalence, `default` level reset semantics, querying no subsystem versus a single subsystem versus all subsystems, text encoder sorting and name suppression, invalid levels, tail log-level parse failures, and cancellation of pipe readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/ls.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/ls.go

## Purpose

`ls.go` implements `ipfs ls`, listing UnixFS directory entries for one or more IPFS/IPNS paths. It supports streamed or batch output, optional child type/size resolution, CID encoding selection, headers, and a long listing format that includes preserved UnixFS file mode and modification time metadata.

## Important APIs, Types, and Functions

`LsCmd` emits `LsOutput`, made of `LsObject` and `LsLink`. Important options are `headers`, `resolve-type`, `size`, `stream`, and `long`. Helper functions `formatMode`, `permBit`, `formatModTime`, and `tabularOutput` produce Unix-like text output. The command uses `api.Unixfs().Ls`, `cmdutils.PathOrCidPath`, `cmdenv.GetCidEncoder`, and maps CoreAPI entry types to UnixFS protobuf data types.

## Control Flow

The run path parses body args, builds a CID encoder, and chooses processing mode. In stream mode, each entry becomes a one-link `LsOutput` emitted immediately with the original path as object hash. In batch mode, each directory accumulates links, sorts them by name, stores them in a pre-sized output slice aligned with input paths, and emits once at the end. For every input path, a goroutine calls `api.Unixfs().Ls` into a channel while the command drains entries, maps type/size/target/mode/mtime into `LsLink`, and checks the goroutine error after the channel closes. CLI post-run consumes potentially multiple streamed outputs and calls `tabularOutput` while tracking the last object to place headers and inter-directory breaks.

## State and Persistence Behavior

The command is read-only. It can fetch or resolve blocks through CoreAPI depending on node mode and child-resolution flags. Batch mode holds entries in memory per directory; stream mode limits memory but cannot perfectly align table breaks in HTTP text encoding.

## Dependencies and Integration Points

It depends on Boxo UnixFS and UnixFS protobuf types, Kubo CoreAPI UnixFS, CID encoders, and command path utilities. Output integrates with global command encoders and with preserved metadata generated by `ipfs add --preserve-mode` and `--preserve-mtime`.

## Risks and Test Signals

Risks include goroutine cancellation when emit fails, large directory memory use in batch mode, ambiguous mode `0` displayed as metadata missing in long output, and time formatting based on current wall clock. Tests should cover stream/batch ordering, multiple directories with headers, long format with and without size, directory slash rendering, non-printable names, all file type and special permission bits, zero/old/recent/future mtimes, child resolution off/on, and path resolution errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/ls.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/ls_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/ls_test.go

## Purpose

`ls_test.go` validates the formatting helpers behind `ipfs ls --long`. It is focused on deterministic string rendering of file modes and modification times rather than full command execution.

## Important APIs, Types, and Functions

The file defines `TestFormatMode` and `TestFormatModTime`, using `testing` and `testify/assert`. The tests exercise unexported helpers `formatMode` and `formatModTime` from `ls.go`.

## Control Flow

`TestFormatMode` is table-driven and runs parent and child subtests in parallel. Cases cover regular files, directories, symlinks, named pipes, sockets, block and character devices, no/full permissions, setuid/setgid/sticky bits with and without execute bits, combined special bits, and directory sticky-bit output. Each case compares the exact 10-character Unix-style mode string. `TestFormatModTime` runs parallel subtests for zero time, old times, very old times, future times, and output length consistency. It uses fixed historical UTC values for stable year-format checks and relative `time.Now()` values only where the assertion is intentionally pattern/length based.

## State and Persistence Behavior

The tests do not mutate repository or filesystem state. They are pure formatting tests with wall-clock dependence in recent/future cases.

## Dependencies and Integration Points

These tests integrate directly with `ls.go` helpers and indirectly protect the `ipfs ls --long` text encoder. The dependency on `testify/assert` matches broader Kubo test style.

## Risks and Test Signals

The tests provide signal for file mode coverage, special-bit semantics, and the 12-character alignment contract for mtimes. Remaining gaps include full `tabularOutput` coverage, HTTP streaming output, sorting, escaped names, directory size placeholders, and deterministic tests around the six-month boundary. Because `formatModTime` uses `time.Now()`, boundary-sensitive tests should avoid exact expectations near the threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/ls_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/mount_nofuse.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/mount_nofuse.go

## Purpose

`mount_nofuse.go` provides the non-Windows, non-FUSE build stub for `ipfs mount`. It keeps the command visible while clearly explaining that the binary was compiled without usable FUSE support.

## Important APIs, Types, and Functions

The file defines only `MountCmd`, a `cmds.Command` with `Experimental` status and help text. Its build tag is `!windows && (nofuse || !(linux || darwin || freebsd))`, complementing the real Unix implementation and the Windows stub.

## Control Flow

There is no `Run` function. Invoking the command in this build mode surfaces help/status rather than attempting mount setup. The user-facing behavior is documentation-driven: use a Kubo binary compiled with FUSE support and see the project repository/FUSE docs.

## State and Persistence Behavior

No state is read or written. The command does not inspect repo config, online status, or mount points.

## Dependencies and Integration Points

The only runtime dependency is `go-ipfs-cmds`. Integration is compile-time: the build tags ensure exactly one `MountCmd` definition is selected among Unix FUSE, no-FUSE, and Windows variants.

## Risks and Test Signals

The key risk is build-tag drift causing duplicate or missing `MountCmd` definitions for a platform. Build matrix tests should cover Linux/Darwin/FreeBSD with and without `nofuse`, unsupported Unix-like platforms, and Windows. UX tests can assert the stub help text mentions missing FUSE support and does not imply a mount operation occurred.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/mount_nofuse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/mount_unix.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/mount_unix.go

## Purpose

`mount_unix.go` implements the real FUSE-backed `ipfs mount` command for Linux, Darwin, and FreeBSD builds without the `nofuse` tag. It mounts read-only `/ipfs`, `/ipns`, and `/mfs` views into the host filesystem.

## Important APIs, Types, and Functions

The file defines mount path option constants and `MountCmd`. It reads `config.Mounts`, retrieves the live `IpfsNode`, and delegates actual FUSE setup to `fuse/node.Mount`. The output type is `config.Mounts`, with a text encoder printing mounted paths.

## Control Flow

The command loads config from the old command context, obtains the node, rejects offline nodes with `ErrNotOnline`, resolves each mount point from explicit options or config defaults, and calls `nodeMount.Mount(nd, fsdir, nsdir, mfsdir)`. On success it emits the effective mount paths. The text encoder formats IPFS/IPNS/MFS lines and escapes non-printable path content.

## State and Persistence Behavior

The command does not persist config changes; option overrides affect only the invocation. It creates OS-level FUSE mounts that live outside the repo and must be unmounted by platform tooling or process lifecycle. It requires an online node because mounted paths resolve through the active node.

## Dependencies and Integration Points

Dependencies include `go-ipfs-cmds`, legacy command context config loading, `cmdenv.GetNode`, Kubo config types, and `github.com/ipfs/kubo/fuse/node`. Compile-time integration is governed by `(linux || darwin || freebsd) && !nofuse`.

## Risks and Test Signals

Risks include platform permissions, stale mount points, offline node rejection, missing config defaults, and FUSE implementation failures bubbling up. Tests should cover option fallback/override, offline error, encoder escaping, build-tag selection, and integration tests that validate mount readability for known IPFS/IPNS/MFS paths on supported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/mount_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/mount_windows.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/mount_windows.go

## Purpose

`mount_windows.go` is the Windows-specific `ipfs mount` stub. It preserves the command name while returning a clear runtime error because FUSE mounting is not implemented for Windows in this command path.

## Important APIs, Types, and Functions

The file defines `MountCmd` with help text and a `Run` function that returns `errors.New("Mount isn't compatible with Windows yet")`.

## Control Flow

Every invocation fails immediately without checking config, repo, node state, or arguments. Help text states the command is not implemented on Windows.

## State and Persistence Behavior

No state is read or written. No mount attempt is made.

## Dependencies and Integration Points

Dependencies are limited to Go `errors` and `go-ipfs-cmds`. The file is selected by filename/build convention for Windows and complements `mount_unix.go` and `mount_nofuse.go`.

## Risks and Test Signals

Risks are mainly UX and build selection: users should receive the Windows-specific incompatibility error, and the build should not accidentally include Unix or no-FUSE definitions. Build tests should compile Windows targets and command tests should assert the exact failure behavior remains non-mutating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/mount_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/multibase.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/multibase.go

## Purpose

`multibase.go` implements `ipfs multibase` utility commands for encoding, decoding, transcoding, and listing multibase encodings. It is a repo-independent data transformation command useful for IPFS/IPNS/PubSub workflows that expose multibase strings.

## Important APIs, Types, and Functions

`MbaseCmd` registers `encode`, `decode`, `transcode`, and shared `basesCmd` from elsewhere. `mbaseEncodeCmd`, `mbaseDecodeCmd`, and `mbaseTranscodeCmd` use `github.com/multiformats/go-multibase`. `CreateCmdExtras(SetDoesNotUseRepo(true))` marks the root as not needing a repo.

## Control Flow

Each command parses body/file args, obtains a single file/stdin reader through `cmdenv.GetFileArg`, and reads all input into memory. `encode` resolves an encoder by name, encodes raw bytes, and emits a string reader. `decode` decodes the input string and emits a bytes reader. `transcode` resolves the target encoder, decodes the input, re-encodes bytes in the target base, and emits a string reader.

## State and Persistence Behavior

The commands are stateless and do not use or mutate the IPFS repo. They operate entirely in memory and stream the final reader to the command response.

## Dependencies and Integration Points

Dependencies include `go-ipfs-cmds`, Kubo `cmdenv`, `go-multibase`, and standard `io`/`bytes`/`strings`. The utility integrates with pubsub topic/data encoding and key signature output where multibase strings are exchanged with users.

## Risks and Test Signals

Reading entire inputs into memory is acceptable for small utility use but risky for very large files. Tests should cover default base64url encoding, named bases, invalid base names, invalid multibase inputs, stdin/file handling, preserving binary bytes across encode/decode/transcode, and repo-less execution. Whitespace/newline handling should be explicit because `mbase.Decode(string(encodedData))` receives the raw file contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/multibase.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/name/ipns.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/name/ipns.go

## Purpose

`name/ipns.go` implements `ipfs name resolve`, resolving IPNS and DNSLink names to IPFS paths. It supports recursive or one-step resolution, DHT resolver tuning, cache control, and streaming intermediate search results.

## Important APIs, Types, and Functions

`IpnsCmd` emits `ResolvedPath`. Options are `recursive`, `nocache`, `dht-record-count`, `dht-timeout`, and `stream`. It uses `api.Name().Resolve` for final resolution and `api.Name().Search` for streaming. Resolver options are built with `namesys.ResolveWithDepth`, `ResolveWithDhtRecordCount`, and `ResolveWithDhtTimeout`.

## Control Flow

The command gets CoreAPI, chooses the requested name or defaults to `api.Key().Self().ID()`, builds name-resolution options from flags, validates non-negative DHT timeout, and prefixes bare names with `/ipns/`. Non-stream mode calls `Resolve`, tolerating `namesys.ErrResolveRecursion` only when the user requested non-recursive behavior, normalizes the result through `path.NewPath`, and emits once. Stream mode calls `Search`, iterates result events, applies the same recursion-error rule, and emits each resolved path.

## State and Persistence Behavior

The command is read-only. It may use or bypass resolver caches depending on `nocache`; online resolution can use DHT and DNSLink sources via the name system. Streaming mode holds a live resolver channel until completion or cancellation.

## Dependencies and Integration Points

Dependencies include Boxo `namesys` and `path`, Kubo CoreAPI name/key interfaces, command environment helpers, and Go duration parsing. It integrates with `name publish`, `name put/get`, IPNS pubsub, and key management through peer IDs and IPNS names.

## Risks and Test Signals

Risks include long DHT timeouts, recursion behavior confusion, accepting both bare and `/ipns/` inputs, and partial stream results when later resolution fails. Tests should cover default self-name lookup, cache flag inversion, recursive false depth-one behavior, DHT count/timeout validation including zero and negative values, stream and non-stream error handling, DNSLink inputs, and output path normalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/name/ipns.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/name/ipnsps.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/name/ipnsps.go

## Purpose

`name/ipnsps.go` implements experimental `ipfs name pubsub` management commands. It reports whether the IPNS pubsub resolver is enabled, lists current IPNS pubsub subscriptions, and cancels a subscription.

## Important APIs, Types, and Functions

`IpnsPubsubCmd` registers `state`, `subs`, and `cancel`. Output types are `ipnsPubsubState`, `ipnsPubsubCancel`, and `stringList`. `stringListEncoder` prints one string per line. The command uses `n.PSRouter`, `GetSubscriptions`, and `Cancel`.

## Control Flow

`state` obtains the node and emits whether `PSRouter` is non-nil. `subs` gets the requested IPNS key encoder, requires an enabled pubsub router, iterates subscription keys, splits each record key, filters to the `ipns` namespace, decodes the raw key bytes into a peer ID, formats it in the requested IPNS base, and emits `/ipns/<name>` paths. `cancel` requires an enabled router, trims an optional `/ipns/` prefix, decodes the user-supplied peer ID, calls `PSRouter.Cancel("/ipns/" + string(pid))`, and emits whether a subscription was canceled.

## State and Persistence Behavior

The command operates on live in-memory IPNS pubsub subscriptions. It does not mutate repo config. `cancel` affects active resolver subscriptions; `state` and `subs` are read-only.

## Dependencies and Integration Points

Dependencies include Kubo node access through `cmdenv`, key encoding helpers, libp2p record key parsing, and peer ID decoding. It integrates with the IPNS resolver's pubsub router and with user-facing key-base formatting.

## Risks and Test Signals

Risks include invalid subscription key data, disabled router errors, and the subtle internal path used for cancellation (`/ipns/` plus raw peer ID bytes). Tests should cover enabled/disabled state, non-IPNS subscription filtering, invalid peer IDs being logged/skipped in `subs`, cancel with bare and prefixed names, no-subscription output, key base formatting, and router errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/name/ipnsps.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/name/name.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/name/name.go

## Purpose

`name/name.go` defines the `ipfs name` command group and implements experimental IPNS record inspection, raw record retrieval, and raw pre-signed record storage. It is the command surface for both high-level IPNS operations and lower-level record debugging/import workflows.

## Important APIs, Types, and Functions

`NameCmd` registers `publish`, `resolve`, `pubsub`, `inspect`, `get`, and `put`. Shared output `IpnsEntry` is used by publish/put. Inspection types are `IpnsInspectValidation`, `IpnsInspectEntry`, and `IpnsInspectResult`. `IpnsInspectCmd` unmarshals and displays IPNS protobuf/DAG-CBOR fields. `IpnsGetCmd` reads raw records through `api.Routing().Get`. `IpnsPutCmd` validates and writes pre-signed raw records through `api.Routing().Put`.

## Control Flow

`inspect` reads a record file/stdin, unmarshals it as an IPNS record, best-effort extracts value, validity type/time, sequence, and TTL, then separately unmarshals protobuf to determine V1/V2 signature style and protobuf size. With `--verify`, it parses the supplied name and calls `ipns.ValidateWithName`; with `--dump`, it includes a hex dump. `get` normalizes a bare name to `/ipns/<name>`, retrieves raw routing bytes, and emits octet-stream content type `application/vnd.ipfs.ipns-record`. `put` validates mutually exclusive offline/delegated flags, optionally checks delegated publisher config, parses the target IPNS name, reads up to 1 MiB from input, and unless `--force` enforces the 10 KiB IPNS spec limit, protobuf validity, signature against name, and increasing sequence relative to any existing record. It then stores the original bytes with `Routing.AllowOffline(allowOffline || allowDelegated)` and emits the name plus extracted value.

## State and Persistence Behavior

`inspect` and `get` are read-only. `put` writes to the routing system and may store locally, broadcast over DHT, or use delegated publishers depending on routing configuration and flags. It does not sign records; it preserves the supplied bytes exactly.

## Dependencies and Integration Points

Dependencies include Boxo `ipns`, IPNS protobuf, CoreAPI routing, Kubo node/config access, protobuf utilities, datastore/routing behavior, and command file handling. It integrates with `name publish`, `routing get/put`, delegated publisher configuration, and IPNS specs.

## Risks and Test Signals

Risks include destructive or invalid records accepted with `--force`, sequence race conditions between validation and put, exact error-string matching for offline failures, memory limits that read only 1 MiB but only spec-check 10 KiB when not forced, and delegated mode relying on config presence. Tests should cover inspect malformed/partial records, verify valid/invalid names, content type for get, put size/signature/sequence checks, identical republish, force behavior, offline/delegated flag combinations, missing delegated publishers, and quiet text output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/name/name.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/name/publish.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/name/publish.go

## Purpose

`name/publish.go` implements `ipfs name publish`, the high-level path that signs and publishes an IPNS record for an IPFS path using a local key. It manages record lifetime, TTL, key selection, V1 compatibility, optional custom sequence number, and offline/delegated publishing modes.

## Important APIs, Types, and Functions

`PublishCmd` uses options for `key`, `resolve`, `lifetime`, `ttl`, `quieter`, `v1compat`, `allow-offline`, `allow-delegated`, `sequence`, and IPNS base formatting. It emits `IpnsEntry`. It relies on `api.Name().Publish`, `api.ResolveNode`, `cmdutils.PathOrCidPath`, `options.Name.*`, and `iface.ErrOffline`.

## Control Flow

The command obtains CoreAPI, validates that `--allow-offline` and `--allow-delegated` are not combined, parses and validates lifetime if explicitly set, then builds publish options for offline/delegated behavior, key name, valid time, and V1 compatibility. TTL is parsed separately: explicit negative TTL is rejected, explicit TTL greater than lifetime is rejected, and default TTL is capped to the chosen lifetime. If provided, a custom sequence option is appended. The target argument is parsed as a path/CID path; when `--resolve` is true, the command resolves the node before publishing. Finally it calls `api.Name().Publish`; `iface.ErrOffline` is replaced with a more actionable error message. Text output prints either only the IPNS name (`--quieter`) or "Published to <name>: <path>".

## State and Persistence Behavior

Publishing signs and stores a new IPNS record through the CoreAPI name system. Depending on flags and node configuration, the record can be stored locally, announced on the DHT, and/or sent to delegated publishers. The command itself does not directly mutate repo config.

## Dependencies and Integration Points

Dependencies include Boxo IPNS defaults, Kubo CoreAPI name/resolve APIs, key encoding options, path utilities, and command encoders. It integrates with keys created by `ipfs key`, IPNS resolution, delegated publisher config, and path availability in the local/network DAG.

## Risks and Test Signals

Risks include TTL/lifetime validation mistakes, sequence regressions, path verification causing network fetches, and user confusion between offline and delegated modes. Tests should cover defaults, explicit lifetime/TTL parsing, TTL cap behavior, invalid negative/too-large values, custom key names and peer IDs, `--resolve=false`, offline error mapping, delegated/offline mutual exclusion, V1 compatibility flag propagation, custom sequence propagation, and quiet output escaping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/name/publish.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/object/diff.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/object/diff.go

## Purpose

`object/diff.go` implements deprecated `ipfs object diff`, comparing two legacy dag-pb/IPFS objects and printing link-level changes. It remains for compatibility while directing users toward newer DAG/files APIs.

## Important APIs, Types, and Functions

`ObjectDiffCmd` emits `Changes`, a wrapper around `dagutils.Change` pointers. It accepts `obj_a`, `obj_b`, and `--verbose`. It uses `api.Object().Diff`, `cmdutils.PathOrCidPath`, Boxo `dagutils`, Boxo `path`, and request-specific CID encoding.

## Control Flow

The command obtains CoreAPI, parses both arguments as paths or CID paths, calls `api.Object().Diff`, and maps CoreAPI changes into `dagutils.Change` values. `Before` and `After` CIDs are populated only when the corresponding immutable path is non-zero. The text encoder chooses verbose prose or compact symbols: `+` for additions, `~` for modifications, and `-` for removals.

## State and Persistence Behavior

The command is read-only. It may resolve or fetch blocks through CoreAPI, but it does not mutate the DAG, blockstore, or repo.

## Dependencies and Integration Points

It integrates with the deprecated `ObjectCmd` tree and legacy dag-pb object APIs in CoreAPI. The command uses the global CID encoder so output honors request encoding options.

## Risks and Test Signals

Risks include deprecated API drift, path resolution errors, empty immutable-path detection, and output compatibility for scripts still consuming `object diff`. Tests should cover add/modify/remove changes, verbose and compact encoders, CID base selection, invalid paths, missing blocks, no-change output, and deprecation status visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/object/diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/object/object.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/object/object.go

## Purpose

`object/object.go` defines the deprecated `ipfs object` command tree for legacy dag-pb plumbing commands. Most subcommands are now removed and point users to `ipfs dag` or `ipfs files`.

## Important APIs, Types, and Functions

The file defines legacy output structs `Link` and `Object`, the unused/general `ErrDataEncoding`, `ObjectCmd`, and `RemovedObjectCmd`. `ObjectCmd` registers `diff` and `patch` as remaining deprecated subcommands while `data`, `get`, `links`, `new`, `put`, and `stat` route to `RemovedObjectCmd`.

## Control Flow

Invoking a removed subcommand returns `errors.New("removed, use 'ipfs dag' or 'ipfs files' instead")`. `ObjectCmd` itself has no run logic; behavior is delegated to subcommands.

## State and Persistence Behavior

Removed commands perform no repo or DAG mutation. `diff` is read-only; `patch` creates new DAG objects through its own file. This file itself only wires command state.

## Dependencies and Integration Points

Dependencies are minimal: Go `errors` and `go-ipfs-cmds`. It integrates with `object/diff.go` and `object/patch.go` and preserves command names for compatibility and deprecation messaging.

## Risks and Test Signals

Risks are compatibility and documentation-related: removed commands should fail consistently while deprecated commands remain accessible. Tests should assert command statuses, subcommand routing, removed command error text, and that object output struct JSON shapes remain compatible for `patch` results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/object/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/object/patch.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/object/patch.go

## Purpose

`object/patch.go` implements the remaining deprecated `ipfs object patch` subcommands for adding and removing links in dag-pb objects. It is retained for legacy workflows but warns users to prefer MFS `files` commands.

## Important APIs, Types, and Functions

`ObjectPatchCmd` exposes deprecated `add-link` and `rm-link`, while removed patch operations route to `RemovedObjectCmd`. `patchRmLinkCmd` uses `api.Object().RmLink`; `patchAddLinkCmd` uses `api.Object().AddLink`. Options include `--create`, `--allow-non-unixfs`, and the shared big-block allowance check. Both emit `Object{Hash: <cid>}`.

## Control Flow

`rm-link` parses the root path/CID, target link name, and UnixFS-validation bypass flag, then calls CoreAPI to create a new object without that link. `add-link` parses root, link name, and child ref, handles `--create` for intermediary nodes, and calls CoreAPI to create a new object with the link. Both commands get the request CID encoder, check resulting CID size via `cmdutils.CheckCIDSize`, and text-encode the new root hash.

## State and Persistence Behavior

The commands do not mutate existing immutable objects. They persist newly created DAG blocks through CoreAPI object patch operations. They may create invalid UnixFS structures if validation is bypassed or if used on sharded directories/files.

## Dependencies and Integration Points

Dependencies include Kubo CoreAPI object methods, command path utilities, CID-size enforcement, and command encoders. The file integrates with the deprecated `object` command tree and indirectly with MFS migration guidance in help text.

## Risks and Test Signals

Risks include producing malformed UnixFS, bypassing validation, big-block/CID-size policy violations, and confusion between immutable object creation and filesystem mutation. Tests should cover add/remove success, missing roots/children, invalid path inputs, `--create`, `--allow-non-unixfs`, CID-size rejection, deprecated status, and text/JSON output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/object/patch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/p2p.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/p2p.go

## Purpose

`p2p.go` implements experimental `ipfs p2p` stream mounting commands. It creates local-to-libp2p forwarders, libp2p-to-local listeners, lists and closes listeners, and lists/resets active p2p streams.

## Important APIs, Types, and Functions

`P2PCmd` registers `forward`, `listen`, `ls`, `close`, and `stream`. Output types are `P2PListenerInfoOutput`, `P2PStreamInfoOutput`, `P2PLsOutput`, `P2PStreamsOutput`, and `P2PForegroundOutput`. Helpers include `parseIpfsAddr`, `checkPort`, `forwardLocal`, and `p2pGetNode`. The protocol namespace default is `/x/`.

## Control Flow

All operational commands call `p2pGetNode`, which requires an online node and `Experimental.Libp2pStreamMounting` config. `forward` parses a protocol, local listen multiaddr, and remote peer multiaddr, resolves DNS multiaddrs if needed, enforces `/x/` unless custom protocols are allowed, adds target addresses to the peerstore, and starts a local listener. `listen` parses a protocol and local target multiaddr, rejects TCP/UDP port zero, enforces protocol namespace, and starts a remote protocol handler forwarding to the target. Foreground mode emits an active status and blocks until request cancellation or listener closure, cleaning up on cancellation. `ls` walks local and p2p listener registries under locks. `close` builds a predicate from all/protocol/listen/target filters and closes matching listeners. `stream ls` enumerates active stream handlers; `stream close` resets all or one by numeric ID.

## State and Persistence Behavior

State is live daemon memory: p2p listeners, streams, peerstore temporary addresses, and foreground command lifetimes. No repo config is changed. Listeners persist in the daemon until explicitly closed, daemon shutdown, or foreground cancellation.

## Dependencies and Integration Points

Dependencies include Kubo `p2p` manager, `core.IpfsNode`, cmdenv, libp2p peerstore/protocol/peer types, multiaddr, and multiaddr DNS resolution. The command integrates with daemon config and live network state.

## Risks and Test Signals

Risks include orphaned listeners, ambiguous DNS multiaddr resolution to multiple peers, unsafe custom protocol namespaces, port-zero listeners, foreground cleanup races, and output headers printed inside loops. Tests should cover config/offline gating, protocol prefix enforcement, parseIpfsAddr raw and DNS paths, ambiguous peer IDs, checkPort TCP/UDP/no-port/zero cases, close filter combinations, foreground cancellation/close behavior, stream reset by ID, and registry locking under concurrent changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/p2p.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/pin/pin.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/pin/pin.go

## Purpose

`pin/pin.go` implements local pin management: adding, removing, listing, updating, and verifying pins. It protects local DAGs from garbage collection and integrates with Kubo's fast-provide behavior so newly pinned content can be announced.

## Important APIs, Types, and Functions

`PinCmd` registers `add`, `rm`, `ls`, `verify`, `update`, and `remote`. Output types include `PinOutput`, `AddPinOutput`, `PinLsOutputWrapper`, `PinLsList`, `PinLsType`, `PinLsObject`, `PinVerifyRes`, `PinStatus`, and `BadNode`. Helpers include `pinAddMany`, `resolveFastProvideFlags`, `fastProvideAfterPin`, `pinLsKeys`, `pinLsAll`, `pinVerify`, and `PinVerifyRes.Format`.

## Control Flow

`pin add` validates optional pin name, resolves each path to an immutable root, and calls `api.Pin().Add` as recursive or direct. With `--progress`, it wraps the context in a DAG progress tracker, runs pinning in a goroutine, and emits periodic progress before final pins. After success it may fast-provide the root or whole DAG using config defaults and explicit flags. `pin rm` resolves inputs and removes pins. `pin ls` validates pin type/name filters, then either checks specific arguments through the pinner or streams all pins through CoreAPI; non-stream mode accumulates a legacy map. `pin update` resolves old and new paths, calls `api.Pin().Update`, optionally unpins the old root, and fast-provides the new root. `pin verify` walks recursive pin DAGs with a validating blockstore, detecting missing/corrupt blocks and optionally outputting OK pins.

## State and Persistence Behavior

Pin add/rm/update mutate the local pinning service and therefore GC reachability. Verify is normally read-only. Fast-provide affects provider queues/network advertisement but not pin state. Listing is read-only and may be expensive with names or indirect pins.

## Dependencies and Integration Points

Dependencies include CoreAPI pin/path/DAG APIs, Boxo pinner, blockstore, offline blockservice, merkledag, CID validation, config fast-provide settings, cmdenv provider helpers, and command utilities. `remotePinCmd` is wired in from `remotepin.go`.

## Risks and Test Signals

Risks include progress goroutine cancellation, name validation, pin list memory growth in non-stream mode, pin verify duplicate implementation drift from CoreAPI, and fast-provide errors being best-effort/log-only. Tests should cover recursive/direct add/rm/update, named pins, stream/non-stream listing, type and name filters, indirect pin reporting, progress output, invalid names/types, fast-provide flag resolution, verify broken/OK DAGs, and quiet/verbose formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/pin/pin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/pin/remotepin.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/pin/remotepin.go

## Purpose

`pin/remotepin.go` implements `ipfs pin remote` and `ipfs pin remote service` commands for interacting with remote pinning services and storing their credentials in repo config.

## Important APIs, Types, and Functions

`remotePinCmd` registers `add`, `ls`, `rm`, and `service`; `remotePinServiceCmd` registers service `add`, `ls`, and `rm`. Key types are `RemotePinOutput`, `ServiceDetails`, `Stat`, `PinCount`, and sortable `PinServicesList`. Helpers include `toRemotePinOutput`, `printRemotePinDetails`, `lsRemote`, `getRemotePinServiceFromRequest`, `getRemotePinService`, `getRemotePinServiceInfo`, and `normalizeEndpoint`.

## Control Flow

`remote add` gets a configured service client, resolves the path/CID locally, validates optional name, adds origin multiaddrs when the block is local and the host is online, warns when offline text output may leave no providers, submits `c.Add`, attempts to connect to returned delegates, and unless `--background` polls request status until pinned or failed. `remote ls` builds filter options for name, CIDs, and statuses, then streams statuses from the remote service. `remote rm` reuses the same listing filters to collect request IDs, rejects multi-delete unless `--force`, and deletes each request. Service `add` opens the repo directly, normalizes the endpoint, rejects duplicates, and stores endpoint/key under `Pinning.RemoteServices`. Service `rm` deletes config entries. Service `ls` reads config, optionally probes each service for queued/pinning/pinned/failed counts concurrently, sorts by service name, and emits text or JSON.

## State and Persistence Behavior

Remote pin requests persist in the external pinning service. Service credentials persist in the local repo config. Listing and stats are read-only apart from network calls. `remote add` can also create transient swarm connections to delegates.

## Dependencies and Integration Points

Dependencies include Boxo remote pinning client, Kubo fsrepo/config/cmdenv/cmdutils, CoreAPI path and swarm APIs, libp2p host/peer address helpers, errgroup, URL/path normalization, and CID encoders. It integrates with local blockstore/provider availability and with repo config lifecycle.

## Risks and Test Signals

Risks include storing service keys in config, direct repo opens while daemon may be active, polling without upper timeout except context, delegate connection failures being logged, bulk remove filter mistakes, and endpoint normalization/security validation. Tests should cover add/list/remove filters, status parsing, duplicate service names, config nil maps, endpoint normalization, `/pins` suffix rejection, query rejection, HTTP/HTTPS-only validation, stat invalid/valid services, offline warnings, background mode, and force behavior for multiple removals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/pin/remotepin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/pin/remotepin_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/pin/remotepin_test.go

## Purpose

`pin/remotepin_test.go` validates `normalizeEndpoint`, the helper that canonicalizes and rejects invalid remote pinning service API endpoints before they are stored in repo config.

## Important APIs, Types, and Functions

The file defines `TestNormalizeEndpoint`, a table-driven test calling unexported `normalizeEndpoint` from `remotepin.go`.

## Control Flow

Each case supplies an input endpoint, expected error text, and expected normalized output. Covered cases include bare HTTPS, trailing slash removal, rejecting `/pins` and `/pins/`, cleaning redundant path elements and slashes, rejecting query parameters, accepting HTTP with host/port, and rejecting unsupported schemes.

## State and Persistence Behavior

The test is pure. It does not create services, write config, or contact remote endpoints.

## Dependencies and Integration Points

It depends only on Go `testing` and the implementation helper. The test protects `pin remote service add` because that command persists normalized endpoints to `Pinning.RemoteServices`.

## Risks and Test Signals

The test gives direct signal on endpoint canonicalization and common user mistakes. Remaining gaps include uppercase schemes/hosts, credentials in URLs, fragments, empty hosts, IPv6 literals, percent-encoded paths, duplicate slashes immediately after host, and asserting that a nil error is required when `tc.err` is empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/pin/remotepin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/ping.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/ping.go

## Purpose

`ping.go` implements `ipfs ping`, a libp2p reachability and latency diagnostic command. It resolves a peer address or peer ID, optionally looks up missing addresses through routing, sends ping protocol messages, and reports round-trip times.

## Important APIs, Types, and Functions

`PingCmd` emits `PingResult`, with success, duration, and text fields. `ParsePeerParam` accepts either a multiaddr containing a peer ID or a raw peer ID. Constants include `kPingTimeout` and `pingCountOptionName`; `ErrPingSelf` protects self-ping.

## Control Flow

The command gets the node, rejects offline mode, parses the first argument into optional transport multiaddr and peer ID, rejects self, stores supplied addresses temporarily in the peerstore, validates positive ping count, and if no addresses are known emits a lookup message then calls `Routing.FindPeer` with a 10 second timeout. It emits a `PING` status, creates a context sized as `kPingTimeout * count`, receives libp2p ping results, emits per-ping success/error events, paces iterations with a one-second ticker, and finally emits average latency if at least one pong succeeded. CLI post-run recomputes an average if context cancellation/deadline occurs after partial success.

## State and Persistence Behavior

The command is mostly read-only but can add temporary peer addresses to the peerstore. It uses live network connections and routing. No repo data is changed.

## Dependencies and Integration Points

Dependencies include Kubo node access, libp2p peerstore and ping protocol, routing, peer IDs, multiaddr parsing, and command streaming. It integrates with the node's online network stack and routing subsystem.

## Risks and Test Signals

Risks include only the first peer argument being used despite variadic declaration, timeout behavior for large counts, partial success on cancellation, and address parsing differences between `/p2p/` multiaddrs and raw IDs. Tests should cover raw peer IDs, full multiaddrs, invalid addresses, self ping, offline mode, count <= 0, routing lookup path, no successful pongs, per-event text encoding, and average calculation on cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/ping.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/profile.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/profile.go

## Purpose

`profile.go` implements the system profiling command that collects Go runtime and Kubo diagnostic profiles from a running daemon into a zip archive. It is used for debugging performance and operational issues.

## Important APIs, Types, and Functions

`sysProfileCmd` emits a streaming zip and a CLI `profileResult`. Options include output path, collector list, profile duration, mutex profile fraction, and block profile rate. It uses `profile.WriteProfiles`, `profile.Options`, `archive/zip`, and a Windows-safe timestamp format.

## Control Flow

The run function parses collector names and durations, reads mutex profile fraction, creates an `io.Pipe`, starts a goroutine that wraps the pipe writer in a zip writer and calls `profile.WriteProfiles`, then emits the pipe reader as octet-stream content type `application/zip`. The CLI post-run consumes the reader, chooses either the explicit output path or `ipfs-profile-<timestamp>.zip`, creates the file, copies archive bytes, and emits a text result with the output filename.

## State and Persistence Behavior

The command reads live daemon/runtime profiling state and writes a zip file only in CLI post-run. It does not persist repo data. Profiles may contain diagnostic metadata such as goroutine stacks, binary/version data, and allocation/mutex/block information.

## Dependencies and Integration Points

Dependencies include Kubo `profile` collectors, go-ipfs-cmds streaming, zip archive writing, and command error typing. It is `NoLocal`, targeting a running daemon's state.

## Risks and Test Signals

Risks include privacy-sensitive profile contents, long-running CPU/trace collection, pipe goroutine error propagation, archive close ordering, and output file overwrite behavior through `os.Create`. Tests should cover duration parsing, zero profile time, block profile rate parsing, collector list propagation, content type/encoding, CLI default filename format, explicit output path, copy errors, and zip readability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/profile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/provide.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/provide.go

## Purpose

`provide.go` implements experimental commands for controlling and observing content providing. It can clear the provide queue, queue immediate provider-record announcements, and render detailed statistics for sweep or legacy provider systems.

## Important APIs, Types, and Functions

`ProvideCmd` registers `clear`, `once`, and `stat`. `ProvideOnceEvent` reports queued CIDs. `provideStats` carries either sweep stats or legacy reprovider stats. Helpers include `extractSweepingProvider`, human formatting functions, and `provideCIDSync`. Stats output supports sections for connectivity, queues, schedule, timings, network, operations, and workers.

## Control Flow

`provide clear` obtains the node and calls `n.Provider.Clear`, optionally suppressing output. `provide once` requires an online node, `Provide.Enabled`, and either peers or HTTP provider config. It deduplicates argument and stdin CIDs with an auto-growing bloom tracker, validates each CID exists locally, and either announces only roots or recursively walks reachable DAG blocks. Each announced CID calls `nd.Provider.ProvideOnce(c.Hash())` and emits a queued event. CLI post-run gives TTY-friendly running counters in text mode and forwards JSON/XML streams unchanged. `provide stat` requires online mode, handles legacy provider stats separately, unwraps sweep providers from dual/buffered wrappers, fetches stats, and text-encodes either a brief summary, selected sections, all sections, or compact two-column output.

## State and Persistence Behavior

`clear` mutates in-memory provider queues. `once` queues immediate provider announcements but explicitly does not add CIDs to the periodic reprovide schedule. Recursive walking reads local DAG blocks. Stats are read-only. Provider records are network-visible routing state after worker processing.

## Dependencies and Integration Points

Dependencies include Boxo DAG walker/merkledag/provider stats, Kubo config and cmdenv, libp2p DHT provider implementations, routing interfaces, terminal detection, humanize formatting, and DHT key formatting. It integrates with import fast-provide paths in pin/add and with node provider configuration.

## Risks and Test Signals

Risks include bloom false positives skipping rare CIDs, recursive walks over huge DAGs, no connected peers causing failures unless HTTP providers exist, distinction between queueing and actual network completion, and complex stats formatting. Tests should cover queue clear nil provider, provide-once local-missing blocks, stdin/argument dedup, recursive cancellation on announce error, text TTY/non-TTY post-run, JSON pass-through, disabled provide config, legacy versus sweep stats, LAN selection errors, compact requires all, closed provider output, and worker warning thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/provide.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/pubsub.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/pubsub.go

## Purpose

`pubsub.go` implements experimental `ipfs pubsub` commands for publishing, subscribing, listing topics, listing peers, and resetting persistent validator sequence-number state. The command is optimized for IPNS-over-PubSub and includes careful multibase URL encoding for binary topic/data values.

## Important APIs, Types, and Functions

`PubsubCmd` registers `pub`, `sub`, `ls`, `peers`, and `reset`. `pubsubMessage` carries multibase data, sender, sequence number, and topic IDs. Helpers include `multibaseDecodedStringListEncoder`, `safeTextListEncoder`, `urlArgsEncoder`, and `urlArgsDecoder`. `pubsubResetResult` reports deleted validator entries.

## Control Flow

`sub` pre-encodes URL args for RPC transport, decodes them server-side, subscribes through `api.PubSub().Subscribe`, flushes HTTP if possible, loops on `sub.Next`, and emits base64url multibase-encoded message fields. Text output decodes and writes message data bytes. Removed `ndpayload` and `lenpayload` encoders return explicit errors. `pub` decodes the topic, reads file/stdin bytes, and publishes them. `ls` gets subscribed topics, encodes them as base64url for structured output, while text output decodes and escapes unsafe characters. `peers` optionally decodes a topic arg, lists peers through CoreAPI, sorts peer IDs, and emits safe text. `reset` directly opens the repo datastore from the live node and deletes validator seqno keys for one decoded peer or all keys under `libp2p.SeqnoStorePrefix`, commits a batch, syncs the datastore prefix, and reports deletion count.

## State and Persistence Behavior

Pub/sub publish, subscribe, ls, and peers use live in-memory/network pubsub state. `reset` mutates persistent datastore validator sequence-number state and can weaken replay protection until state is rebuilt. It does not clear the in-memory seen-message cache.

## Dependencies and Integration Points

Dependencies include CoreAPI PubSub, go-datastore queries/batches, Kubo libp2p seqno prefix, cmdenv, peer IDs, multibase, HTTP flushing, and command encoders. It integrates with config-enabled pubsub and IPNS pubsub router behavior.

## Risks and Test Signals

Risks include binary topic corruption if URL args are not base64url, unbounded subscription lifetimes, reading whole publish payloads into memory, removed encoder compatibility, and destructive reset misuse. Tests should cover URL arg encode/decode, non-base64url rejection, pub/sub binary round trips, text escaping, sorted peers, subscription cancellation, reset one peer/all peers including datastore sync errors, removed encoder errors, and disabled pubsub errors from CoreAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/pubsub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/refs.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/refs.go

## Purpose

`refs.go` implements `ipfs refs` and `ipfs refs local`, listing linked CIDs from DAG objects or all local blockstore keys. It supports recursive traversal, unique output, max-depth pruning, edge formatting, and custom format tokens.

## Important APIs, Types, and Functions

`RefsCmd` emits `RefWrapper` and uses `RefWriter`. `RefsLocalCmd` emits all local blockstore keys. Helper `objectsForPaths` resolves input paths to root CIDs. `RefWriter` stores the response emitter, DAG getter/session, context, uniqueness flag, max depth, print format, and a seen-depth map. Methods are `WriteRefs`, `writeRefsRecursive`, `visit`, and `WriteEdge`.

## Control Flow

The command parses body args, obtains CoreAPI and CID encoder, resolves options, converts non-recursive mode to `maxDepth=1`, and maps `--edges` to format `<src> -> <dst>` while rejecting simultaneous custom format. It resolves all input paths to CIDs, creates a merkledag session, then writes refs for each root. Traversal iterates linked child nodes via `ipld.GetDAG`; `visit` decides whether to print and/or recurse based on depth limits and uniqueness. If a child must be printed or recursed into, the lazy getter is fetched, the edge is emitted, and recursion continues as allowed. `refs local` streams `n.Blockstore.AllKeysChan`.

## State and Persistence Behavior

The command is read-only. It may fetch DAG blocks during path resolution and traversal. Unique recursive traversals hold a map of seen CIDs and depths; local refs streams all blockstore keys.

## Dependencies and Integration Points

Dependencies include Kubo CoreAPI DAG/path resolution, Boxo merkledag sessions, go-ipld-format lazy traversal, CID encoding utilities, blockstore access through node, and command encoders. It integrates with repo listing as `ipfs repo ls`.

## Risks and Test Signals

Risks include memory growth for `--unique` on large DAGs, expensive recursive fetches, max-depth edge cases such as zero, custom format token replacement ambiguity, and emitting traversal errors as response objects that text encoding converts to errors. Tests should cover direct versus recursive refs, unique branch pruning at different depths, max-depth values, edges/custom format conflict, link names, traversal errors, context cancellation, local key streaming, CID base selection, and multiple roots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/refs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/repo.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/repo.go

## Purpose

`repo.go` implements `ipfs repo` maintenance commands: garbage collection, stats, version reporting, block verification/remediation, migrations, and local block listing. It is the main command surface for local repository health and lifecycle operations.

## Important APIs, Types, and Functions

`RepoCmd` registers `stat`, `gc`, `version`, `verify`, `migrate`, and `ls`. Output types include `RepoVersion`, `GcResult`, `VerifyProgress`, and internal `verifyResult`. Verification state is modeled by `verifyState` constants for valid, corrupt, removed, remove-failed, healed, and heal-failed blocks. Helpers include `verifyWorkerRun` and `verifyResultChan`.

## Control Flow

`repo gc` calls `corerepo.GarbageCollectAsync`; with `--stream-errors` it emits each removed CID or error and returns a final error if any occurred, otherwise it collects results while optionally suppressing output. `repo stat` either emits only size stats or full repo stats and text-formats sizes with optional human units. `repo verify` builds a validating blockstore over the repo datastore, parses `--drop`, `--heal`, and heal timeout, requires online CoreAPI for healing, streams all keys, and verifies blocks in `runtime.NumCPU()*2` workers. Corrupt blocks are reported, optionally deleted, and optionally re-fetched via `api.Block().Get`. The command aggregates outcomes and returns non-zero errors when corruption is only detected or remediation fails. `repo version` emits the supported fs-repo version. `repo migrate` is local-only/repo-direct: it reads current repo version, validates downgrade permission, runs hybrid migrations to a target version, and prints migration progress/errors directly.

## State and Persistence Behavior

`gc` deletes unpinned blocks from local storage. `verify` is read-only by default, but `--drop` deletes corrupt blocks and `--heal` deletes then attempts network refetch. `migrate` mutates repository layout/version and can downgrade only with explicit permission. `stat` and `version` are read-only.

## Dependencies and Integration Points

Dependencies include Kubo corerepo, fsrepo, migrations, old command context, CoreAPI block access, Boxo validating blockstore, path/CID types, humanize formatting, and concurrency primitives. It integrates with pinning/GC invariants, repo locks/migration tooling, and `refs local`.

## Risks and Test Signals

Risks are high because GC, verify drop/heal, and migrate are destructive. Tests should cover GC streaming and silent/quiet encoders, stats size-only/human output, verify corrupt detection, drop success/failure, heal online gating and timeout, worker cancellation, final exit-error rules, version quiet output, migration no-op, downgrade rejection/allowance, migration failure messaging, and not opening the repo through daemon paths before migrations acquire locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/repo.go -->
