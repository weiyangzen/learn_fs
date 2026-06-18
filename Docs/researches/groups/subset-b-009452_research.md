# subset-b-009452 Research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/declextract/declextract.go -->
# sources/test-tools/syzkaller/pkg/declextract/declextract.go

Purpose: `declextract.go` is the main orchestration and type-lowering logic for converting clang extraction output into syzkaller description text plus interface metadata. `Run` builds a mutable `context`, processes functions, typing facts, constants, enums, structs, syscalls, io_uring operations, serializes generated descriptions, finalizes interfaces, and returns `Result`.

Important APIs/types/functions: `Result` exposes `Descriptions`, discovered `Interfaces`, constant-to-include usage, and `StructInfo`. `context` carries input `Output`, iface probe coverage, syscall rename rules, lookup maps, generated includes/defines/interfaces, and accumulated errors. `processConsts`, `processEnums`, `processSyscalls`, `emitSyscall`, `processIouring`, `processStructs`, `processFields`, and the `fieldType*` family are the major passes.

Control flow and state: most work mutates the shared context. Constants are split into kernel header includes versus explicit `define` records, then sorted and deduplicated. Structs and enums get the `$auto` suffix before references are serialized. Syscalls are duplicated into command-specific variants when dataflow discovers switched command arguments; ordinary variants are then refined by inferred argument and return types.

Dependencies and integration: this file depends on `clangtool.SortAndDedupSlice`, coverage data, ifaceprobe file coverage, and helper passes in `typing.go`, `interface.go`, `fileops.go`, `netlink.go`, and `serialization.go`. It emits syzkaller DSL constructs such as `ptr`, `array`, `flags`, `len`, `filename`, `sockaddr`, and generated resources.

Risks: heuristics are deliberately broad. Name-based fd/path/network recognition may misclassify fields; recursive pointer handling uses parent-name and `next` heuristics; unsupported bitfields, bounds, and missing structs become accumulated errors or panics. There are no direct tests in this subset, so confidence comes from integration with generated descriptions and downstream syzlang parsing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/declextract/declextract.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/declextract/entity.go -->
# sources/test-tools/syzkaller/pkg/declextract/entity.go

Purpose: `entity.go` defines the JSON-facing extraction model used by the clang tool and all subsequent declextract passes. It is the schema boundary between extracted kernel facts and generated syzkaller descriptions.

Important APIs/types/functions: `Output` aggregates functions, constants, enums, structs, syscalls, file operations, ioctls, io_uring operations, netlink families, and policies. `Function`, `FunctionScope`, `Field`, `Syscall`, `FileOps`, `Ioctl`, `IouringOp`, `NetlinkFamily`, `NetlinkPolicy`, `NetlinkAttr`, `Struct`, `Enum`, and `Type` model extracted declarations. `TypingFact` and `TypingEntity` model flow edges between returns, arguments, struct fields, locals, and global addresses. `Output.Merge`, `Output.Finalize`, and `Output.SetSourceFile` are the operational methods.

Control flow and state: `Merge` appends another extraction output into the receiver; `Finalize` sorts and deduplicates each top-level slice; `SetSourceFile` rewrites paths and attaches source-file provenance to syscall/fileop/netlink/io_uring entities. It also relaxes static-function status for included `.c` files that are compiled through another translation unit.

Dependencies and integration: consumers in `declextract.go`, `typing.go`, `interface.go`, `fileops.go`, and `netlink.go` mutate hidden fields such as `Field.syzType`, `Syscall.returnType`, `Function.callers`, and resolved `fileOps` callbacks. The public JSON tags are important for stable clang-tool interchange.

Risks: schema changes affect extraction compatibility and generated output determinism. Hidden state means copied values can lose derived metadata if not copied carefully. `EntityGlobalAddr.Name` lacks an explicit JSON tag unlike neighboring fields. There are no local tests for this file; coverage is indirect through end-to-end extraction and serialization paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/declextract/entity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/declextract/fileops.go -->
# sources/test-tools/syzkaller/pkg/declextract/fileops.go

Purpose: `fileops.go` synthesizes syzkaller descriptions and interface records for Linux `file_operations` tables, mapping callback coverage from ifaceprobe to concrete file paths and ioctl commands.

Important APIs/functions: `serializeFileOps` seeds known ioctl argument types, resolves callbacks, maps file operations to probed files, records `FILEOP` and `IOCTL` interfaces, and emits generated open/read/write/mmap/ioctl descriptions. `createFops` emits resources and operations for one file operation table. `createIoctls` emits command-specific or generic ioctl calls. Mapping helpers include `mapFopsToFiles`, `mapFileToFops`, `fileCandidates`, and `resolveFopsCallbacks`.

Control flow and state: callback names are resolved to `Function` pointers and counted for uniqueness. Probe coverage is converted into file-to-callback sets, then scored against candidate file operation tables. Unique callbacks dominate scoring; ioctl matches receive a high bonus; excessive duplicate read/write/mmap-only descriptions are filtered. A generic open-only entry is appended for files with no stronger mapping.

Dependencies and integration: this module uses `ifaceprobe.Info` from `context.probe`, `ast.IsValidStringLit` to reject non-ASCII/invalid filenames, `clangtool.SortAndDedupSlice` for deterministic candidates, type inference from `typing.go`, and field lowering from `declextract.go`.

Risks: mapping file paths to operation tables is acknowledged as heuristic-heavy because callbacks can be shared, chained, updated at runtime, or not covered by probe runs. `mustFindFunc` panics for missing callback functions. Generated descriptions can be generic when coverage cannot prove a precise file operation. No direct tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/declextract/fileops.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/declextract/interface.go -->
# sources/test-tools/syzkaller/pkg/declextract/interface.go

Purpose: `interface.go` tracks discovered kernel interfaces and computes reachability, coverage, and access metadata for reporting or prioritization.

Important APIs/types/functions: `Interface` records type, name, identifying constant, source files, implementation function, access class, description availability, reachable LOC, and block coverage. `TristateVal` models unknown/yes/no flags. Interface kinds include syscall, netlink, fileop, ioctl, and io_uring. Access classes include unknown, user, namespace admin, and admin. `noteInterface`, `finishInterfaces`, `processFunctions`, `calculateLOC`, `collectLOC`, `findFunc`, `mustFindFunc`, `fileNameSuffix`, and `Tristate` are the key routines.

Control flow and state: `processFunctions` indexes functions by file-qualified and global names, merges coverage blocks into function scopes, links call graph edges, and counts callers. `finishInterfaces` sorts and deduplicates interfaces, disambiguates duplicate names with file suffixes, computes LOC/coverage, normalizes file lists, and fills default access. `collectLOC` recursively follows relevant scope calls while skipping very common callees.

Dependencies and integration: coverage comes from `pkg/cover`; function/scope facts come from `entity.go`; command-scope relevance uses `inferArgFlow` from `typing.go`. Interface records are created by syscalls, fileops, netlink, and io_uring passes.

Risks: duplicate access defaulting appears twice but is benign. LOC calculation depends on scope accuracy and ignores functions above a caller threshold, so results are prioritization signals rather than exact complexity. Missing functions produce warnings except for `mustFindFunc` callers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/declextract/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/declextract/netlink.go -->
# sources/test-tools/syzkaller/pkg/declextract/netlink.go

Purpose: `netlink.go` serializes extracted generic-netlink families, operations, and attribute policies into syzkaller descriptions and interface metadata.

Important APIs/types/functions: `serializeNetlink` emits family resources, message header aliases, `syz_genetlink_get_family_id` calls, sendmsg calls for operations, and associated `NETLINK` interfaces. `policyQueue` ensures policies are emitted lazily on first use. `serializeNetlinkPolicy`, `nlattrType`, `netlinkType`, and `netlinkTypeInt` lower netlink attribute schemas into syzlang types.

Control flow and state: all extracted policies are loaded into `policyQueue`. Each family with operations gets a generated family id resource and message type. Operation policies are marked used; pending policies are drained after each family. Nested attributes recursively enqueue nested policies. Binary attributes are converted to scalar, buffer, struct, or array types based on explicit element type and maximum size.

Dependencies and integration: this file uses `stringIdentifier`, `fieldType`, `ctx.structs`, and `ctx.error` from the main declextract context. `Interface` records connect netlink operations back to source file, function, access level, and identifying command.

Risks: families without operations are skipped with a TODO, so broadcast-only APIs are not described. Unknown netlink integer kinds panic. Binary attributes with missing structs or odd element sizes accumulate errors. Policy naming assumes extracted names are unique after `$auto` suffixing. No direct tests are included.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/declextract/netlink.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/declextract/serialization.go -->
# sources/test-tools/syzkaller/pkg/declextract/serialization.go

Purpose: `serialization.go` owns final text emission for generated syzkaller descriptions.

Important APIs/functions: `serialize` initializes the output buffer, writes a standard generated header, then calls include, enum, syscall, fileop, netlink, struct, and define serializers. `fmt` is a thin buffer writer. `serializeIncludes`, `serializeDefines`, `serializeSyscalls`, `serializeEnums`, and `serializeStructs` emit concrete syzlang fragments.

Control flow and state: serialization is ordered intentionally: includes and reusable generated helper types first, then enums/syscalls/fileops/netlink/structs/defines. `serializeFileOps` and `serializeNetlink` have side effects beyond writing text: they also record interfaces and may consume dataflow and probe state. Struct serialization skips zero-size structs, chooses `{}` versus `[]` for struct versus union, emits field names and computed syzkaller types, and appends packed/alignment attributes.

Dependencies and integration: all emitted data comes from the shared `context` populated by earlier passes. The header defines `auto_todo`, `auto_union`, and `auto_aligner`, which are referenced by type-lowering code in `declextract.go`, `typing.go`, and `netlink.go`.

Risks: serializer assumes prior passes have already populated `syzType`, return types, suffixed names, sorted lists, and include/define lists. If any earlier pass omits normalization, this file will emit invalid syzlang rather than detecting all issues. There are no local tests; validation is likely downstream syzlang parsing or generated-description compilation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/declextract/serialization.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/declextract/typing.go -->
# sources/test-tools/syzkaller/pkg/declextract/typing.go

Purpose: `typing.go` performs resource/type inference over extracted data-flow facts. It refines syscall arguments, returns, struct fields, ioctl variants, and interface scope calculations.

Important APIs/types/functions: `typingNode` represents a graph node with bidirectional flows. `processTypingFacts` builds the graph. `canonicalNode` and `TypingEntity.ID` normalize local, field, argument, return, and global-address entities. Public inference entry points are `inferReturnType`, `inferArgType`, `inferFieldType`, `inferCommandVariants`, and `inferArgFlow`. `inferContext.walk`, `relevantScope`, and `refineFieldType` perform graph traversal and application.

Control flow and state: extracted scope facts become edges in per-function or global maps. Inference walks both from and to a node, looking for known resource producers or consumers from `flowResources`, respecting command-specific scopes where needed. Shorter paths win, with lexical tie-breaking for determinism. Command variants are collected from switch scopes reachable from an argument. Traversal depth is capped to limit false positives.

Dependencies and integration: the file relies on `FunctionScope` facts from `entity.go`, function lookup in `interface.go`, and generated field types from `declextract.go`. It feeds `processSyscalls`, `processStructs`, `createIoctls`, and LOC relevance.

Risks: the comments list many known limitations: incomplete resource dictionaries, missing SSA, possible false fd return inference, no const/unused-arg inference, and coarse ignore lists for noisy functions/files/structs. The graph is mutable and unguarded, but used during single-threaded generation. No direct tests are included.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/declextract/typing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/dungeon/dungeon.go -->
# sources/test-tools/syzkaller/pkg/dungeon/dungeon.go

Purpose: `dungeon.go` turns syzkaller bug-fix history into game-like contributor metadata: kingdoms by email domain, classes by subsystem, XP/level calculations, badges, hero names, tiers, and guild summaries.

Important APIs/types/functions: `BugInfo` carries normalized bug signals. `BadgeDefinition` contains display data and a predicate. `GetKingdom`, `GetBugXPAndDays`, `ResolveClass`, `GetHeroName`, `GetBadges`, `ScaleAttribute`, `CalculateLevel`, `GetClassNameByEmoji`, `GetKingdomTier`, and `GetKingdomGuilds` are the main exported helpers. Curated maps and class lookup tables encode domain and subsystem policy.

Control flow and state: package initialization builds `classLookup` from class definitions. XP starts at 100, adds crash, age, quick-fix, and no-reproducer bonuses with caps. Class resolution picks the most frequent subsystem, with lexicographic tie-breaking. Badges are returned as fresh predicate definitions and match bug titles plus commit titles using substring or token regex checks. Guild summaries sort by count descending and then name.

Dependencies and integration: standard `math`, `regexp`, `sort`, `slices`, `strings`, and `time` are used. External callers provide already-normalized lower-case titles and subsystem counts; this package does not persist state.

Risks: classification is static and curated, so domains/subsystems drift over time. Badge predicates are text heuristics and may false-positive or miss spelling variants. Some display strings include non-ASCII icon data. Tests in `dungeon_test.go` cover tie-breaking, XP thresholds, badge matching, kingdoms, tiers, and guild sorting.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/dungeon/dungeon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/dungeon/dungeon_test.go -->
# sources/test-tools/syzkaller/pkg/dungeon/dungeon_test.go

Purpose: `dungeon_test.go` validates the deterministic behavior of the dungeon scoring and classification helpers.

Important tests: `TestResolveClass` covers empty/unknown fallback, known subsystem selection, and lexicographic tie-breaking. `TestCalculateLevel` checks level progression around level 50 and a high-score case. `TestScaleAttribute` covers logarithmic scaling and lower bound clamping. `TestIntegrationBadges` verifies representative title matches for lock, leak, hung task, null pointer, and similar badge predicates. `TestGetKingdom`, `TestGetBugXPAndDays`, `TestGetKingdomTier`, and `TestGetKingdomGuilds` cover domain mapping, XP bonuses, tier boundaries, pluralization, and sorting.

Control flow and state: tests are table-driven and use `testify/require` for exact comparisons. `time.Now` is used inside `TestGetBugXPAndDays`, but expected durations are relative to the same captured `now`, so results are deterministic.

Dependencies and integration: these tests are in-package, so they exercise exported functions plus internal details indirectly through outputs. They establish public behavioral contracts for callers that render contributor profiles.

Risks/test gaps: tests do not exhaustively cover every curated domain, class, adjective, or badge. They also do not validate display descriptions. However, they cover the main scoring thresholds and sorting/tie-breaking paths most likely to regress.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/dungeon/dungeon_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/action.go -->
# sources/test-tools/syzkaller/pkg/email/action.go

Purpose: `action.go` decides how an incoming parsed email should affect dashboard discussion state: ignore, append to an existing thread, or start a new thread.

Important APIs/types/functions: `OldThreadInfo` records the existing dashboard discussion type. `MessageAction` has `ActionIgnore`, `ActionAppend`, and `ActionNewThread`. `NewMessageAction` is the decision function, consuming parsed `Email`, inferred `dashapi.DiscussionType`, and optional old-thread context.

Control flow and state: messages without `InReplyTo` always start new threads. Replies with known prior thread information append unless a patch reply arrives under a different old thread type, in which case it starts a new patch discussion. Replies from own email with no known old thread are ignored because they likely expose a bot response to an unseen private request. Other orphan replies start a visible sub-thread.

Dependencies and integration: this file depends on `dashboard/dashapi` types and the parsed `Email` model from `parser.go`. `lore/parse.go` uses it while walking message trees.

Risks: the logic intentionally encodes product assumptions about syzbot visibility and patch testing. A wrong `msgType` classification can split or merge discussions incorrectly. Tests in `action_test.go` cover all branches.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/action.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/action_test.go -->
# sources/test-tools/syzkaller/pkg/email/action_test.go

Purpose: `action_test.go` verifies `NewMessageAction` decision branches.

Important tests: `TestMessageActions` covers a plain new thread, replies to report and patch threads, own-email orphan reply ignored, human orphan reply becoming a new thread, and a patch reply to a report becoming a new patch thread.

Control flow and state: the test is table-driven and constructs minimal `Email` and `OldThreadInfo` values. It compares exact `MessageAction` constants for each named scenario.

Dependencies and integration: the test imports `dashapi` to use real discussion-type constants, ensuring compatibility with the lore parser and dashboard state model.

Risks/test gaps: it does not exercise malformed or ambiguous discussion types beyond the main branch cases. It also does not verify interaction with full parsed email headers; those paths are covered in parser and lore tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/action_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/lore/parse.go -->
# sources/test-tools/syzkaller/pkg/email/lore/parse.go

Purpose: `lore/parse.go` groups parsed lore.kernel.org emails into dashboard discussion threads and patch series.

Important APIs/types/functions: `Thread`, `Series`, and `Patch` are the core outputs. `Threads`, `PatchSeries`, `DiscussionType`, `parsePatchSubject`, `LinkToMessage`, and `LinkToThread` are public or package-significant helpers. `PatchSubject` and generic `Optional[T]` represent parsed subject metadata.

Control flow and state: `listThreads` records messages by `Message-ID`, builds parent-to-child edges from `In-Reply-To`, starts traversal from roots or orphan replies, then applies `email.NewMessageAction` to append, ignore, or create threads. Bug IDs are collected and sorted per thread. `PatchSeries` reuses shallow thread traversal, parses the root patch subject, collects cover/base-commit data, ignores cover seq 0 and non-patch replies, detects duplicates, sorts patches by sequence, and marks corrupted series when counts do not match.

Dependencies and integration: it layers on `pkg/email` parsing and action logic plus dashboard discussion-type constants. Link helpers encode lore.kernel.org URL shape.

Risks: patch subject parsing is regex-based and intentionally crude; unusual subject tags may be missed. Thread traversal depends on complete message IDs and can split orphan replies. Series corruption reasons are strings consumed by callers. Tests in `parse_test.go` cover thread grouping, subject parsing, discussion type, series parsing, and links.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/lore/parse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/lore/parse_test.go -->
# sources/test-tools/syzkaller/pkg/email/lore/parse_test.go

Purpose: `lore/parse_test.go` exercises thread extraction, patch subject parsing, discussion classification, patch-series construction, and lore URL formatting.

Important tests: `TestThreadsCollection` builds root/reply/orphan/own-email scenarios and validates resulting threads, bug IDs, and message ordering. `TestParsePatchSubject` checks plain, cover, numbered, RFC, versioned, resend, and net-next subjects. `TestDiscussionType` checks patch, reminder, report, and mention classification. `TestParseSeries` verifies single patches, cover-letter series, missing patches marked corrupted, and reply subjects without patches. `TestLink` validates message and thread URL helpers.

Control flow and state: tests parse raw email strings through `lore.Parse`, then normalize fields not relevant to grouping before comparing deep structures. Series tests use a dummy diff to set `HasPatch`.

Dependencies and integration: the test crosses `pkg/email` parsing, patch extraction, bug ID extraction, and dashboard discussion type constants.

Risks/test gaps: tests do not cover all malformed subject forms or duplicate patch sequence handling. They also do not verify base-commit propagation in series despite code support. Coverage is nevertheless strong for the primary lore grouping semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/lore/parse_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/lore/poller.go -->
# sources/test-tools/syzkaller/pkg/email/lore/poller.go

Purpose: `lore/poller.go` polls an LKML-style git archive, parses new messages, maintains ancestry metadata, and pushes root-resolved emails to consumers.

Important APIs/types/functions: `PollerConfig` configures repo directory, remote URL, tracer, own emails, lookback period, and test clock. `PolledEmail` carries parsed email, root message ID, and raw bytes. `Poller` stores repo handle, ancestor map, last processed commit, and initialization state. Main methods are `NewPoller`, `Poll`, `initialize`, `push`, `resolveRoot`, and `Loop`.

Control flow and state: first poll initializes by cloning/polling the archive and scanning all commit headers to populate `Message-ID -> In-Reply-To`. Subsequent polling fetches remote `master`, reads commits since `lastCommit` or within the lookback window, parses newest-to-oldest via `slices.Backward`, sanitizes future message dates to commit date, ignores missing message IDs, updates ancestor state, pushes to output unless an ancestry loop is detected, and advances `lastCommit`.

Dependencies and integration: it uses `vcs.NewLKMLRepo`, `ReadArchive`, `lore.Parse`, `email.ExtractInReplyTo`, `debugtracer`, contexts, and channels. `Loop` wraps `Poll` with a ticker and logs errors without exiting until context cancellation.

Risks: ancestor state is in-memory and can grow with archive size. `lastCommit` advances after each pushed/processed message, so crashes mid-batch may replay later messages. Poll errors are logged in `Loop` but suppressed. Tests cover initialization, lookback, root resolution, own-email parsing, loop detection, and date sanitization.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/lore/poller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/lore/poller_test.go -->
# sources/test-tools/syzkaller/pkg/email/lore/poller_test.go

Purpose: `poller_test.go` validates `Poller` behavior against a local test git archive.

Important tests: `TestPoller` builds an archive with old and recent messages, verifies first-poll initialization plus lookback filtering, checks root resolution across replies, then adds a later reply and an own-email message. `TestPollerLoop` creates a cyclic ancestry pair and verifies no message is emitted. `TestPollerDateSanitization` confirms future-dated email headers are clamped to commit date.

Control flow and state: tests use `NewTestLoreArchive` to create commits with controlled dates, a buffered output channel for polled messages, and injected `now` functions. They call `Poll` directly rather than relying on ticker timing.

Dependencies and integration: tests cross the vcs test repo helper, archive reader, poller initialization, raw email parsing, and root-resolution logic.

Risks/test gaps: tests do not exercise network failures, git poll failures, context cancellation during channel send, or `Loop` retry logging. They give good coverage of stateful polling and ancestry correctness.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/lore/poller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/lore/read.go -->
# sources/test-tools/syzkaller/pkg/email/lore/read.go

Purpose: `lore/read.go` adapts the syzkaller vcs abstraction to the email lore parser by exposing commit-backed email readers.

Important APIs/types/functions: `EmailReader` embeds `vcs.CommitShort` and supplies a `Read` closure. `ReadArchive` lists recent commits and returns one reader per commit. `Email` wraps `*email.Email` with `HasPatch`. `Parse` parses raw bytes through the base email parser and records whether a patch was present.

Control flow and state: `ReadArchive` calls `repo.LatestCommits(afterCommit, afterTime)`, captures each loop variable safely, and defines `Read` to fetch object `m` at the commit hash. `Parse` uses no mailing-list whitelist, accepts caller-provided own emails and domains, and computes `HasPatch` from `msg.Patch != ""`.

Dependencies and integration: this file bridges `pkg/vcs`, `pkg/email`, and the lore grouping/poller code. The convention that each archive commit stores message content as object `m` is central.

Risks: archive shape is assumed; if the LKML repo layout changes, `repo.Object("m", hash)` fails. `HasPatch` depends on the heuristic `email.ParsePatch`. Tests exercise this through lore parse and poller scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/lore/read.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/lore/test_util.go -->
# sources/test-tools/syzkaller/pkg/email/lore/test_util.go

Purpose: `test_util.go` provides helpers for lore poller tests to create a local git-backed email archive.

Important APIs/types/functions: `TestLoreArchive` wraps `*vcs.TestRepo`. `NewTestLoreArchive` initializes a test repo and checks out `master`. `SaveMessage` saves using current time; `SaveMessageAt` writes raw message content to file `m`, stages it, and commits with a controlled commit date.

Control flow and state: each saved message overwrites `m` and creates a new commit, matching the archive reader convention in `ReadArchive`. Assertions ensure file writes succeed before committing.

Dependencies and integration: this file depends on `vcs.MakeTestRepo`, git commands through the test repo helper, `os.WriteFile`, and `filepath.Join`. It is test-only and supports `poller_test.go`.

Risks: helper correctness depends on the `vcs.TestRepo` implementation and local git availability in tests. It intentionally sets broad file permissions for the temporary file. There are no standalone tests, but it is exercised by poller tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/lore/test_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/parser.go -->
# sources/test-tools/syzkaller/pkg/email/parser.go

Purpose: `parser.go` is the main email ingestion module: it reads RFC822 messages, normalizes headers and addresses, extracts body/patch/commands/bug IDs, detects mailing-list authorship, and exposes list utilities.

Important APIs/types/functions: `Email`, `SingleCommand`, and `Command` are core data types. `Parse` is the top-level parser. Address utilities include `AddAddrContext`, `RemoveAddrContext`, `CanonicalEmail`, `EmailsMatch`, and `Split`. Command parsing uses `extractCommands`, `extractCommand`, `strToCmd`, `extractArgsTokens`, and `extractArgsLine`. MIME and metadata helpers include `parseBody`, `ExtractInReplyTo`, `extractBodyBugIDs`, `MergeEmailLists`, `RemoveFromEmailList`, `SubtractEmailLists`, `decodeSubject`, `extractBaseCommitHint`, and `DirectlyAddressedTo`.

Control flow and state: `Parse` reads headers, identifies own addresses with optional plus-context bug IDs, builds deduplicated Cc lists, parses text and attachments recursively, extracts first patch from attachments or body, collects commands from subject plus body, unescapes Google Groups links, handles mailing-list sender/original-from rewrites, parses dates to UTC, and returns a populated immutable result.

Dependencies and integration: it depends on Go `net/mail`, MIME, quoted-printable/base64, regex, URL decoding, and `ParsePatch` from `patch.go`. Lore, dashboard, and sender code consume its normalized output.

Risks: MIME handling keeps only the first text/plain body and ignores non-text non-multipart content. Bug ID regex construction assumes non-empty own emails or domains. Email command restoration is heuristic. Tests in `parser_test.go` cover many real-world encodings and edge cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/parser_test.go -->
# sources/test-tools/syzkaller/pkg/email/parser_test.go

Purpose: `parser_test.go` is broad regression coverage for email parsing, command extraction, address context handling, bug ID extraction, MIME decoding, links, subjects, and base commit hints.

Important tests: `TestExtractCommand` verifies command syntax variations, CRLF parity, wrapped `test:` arguments, first-command iteration, and set/unset/reject commands. Address tests cover plus-context add/remove and canonicalization. `TestParse` runs many raw message fixtures covering Google Groups footers, own-email detection, multipart/base64 patch attachments, quoted-printable bodies, mailing-list sender/original-from behavior, bug IDs in headers/body/domain links, multi-command extraction, RFC 2047 subject decoding, and strict `base-commit` parsing. `TestDirectlyAddressedTo` checks raw-header context matching.

Control flow and state: tests compare full `Email` structs for exact output. Each parse fixture is also rerun with LF converted to CRLF, with expected body adjusted.

Dependencies and integration: fixtures exercise `ParsePatch`, MIME decoding, command parsing, email list merging, and direct-address logic.

Risks/test gaps: coverage is strong but not exhaustive for malformed MIME nesting, empty own email/domain inputs, or extremely large messages. Full-struct comparisons make intentional output changes noisy but effective at catching regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/patch.go -->
# sources/test-tools/syzkaller/pkg/email/patch.go

Purpose: `patch.go` extracts diff content from email text and formats outgoing kernel patch descriptions with tags, recipients, and base commit metadata.

Important APIs/types/functions: `ParsePatch` scans for diff starts and returns normalized diff text. `PatchTemplateData` carries base commit, fixes tag, tools, authors, recipients, links, closes, reported-by, reviewed-by, acked-by, and tested-by fields. `FormatPatchDescription` and `FormatPatch` render outgoing text. `formatAssistedBy`, `diffRegexps`, and `lineMatchesDiffStart` support formatting and parsing.

Control flow and state: `ParsePatch` begins collecting at git/index/new-file/Index diff markers, continues through blank/context/add/remove/hunk/separator lines, and stops at signature separators or quoted reply lines. Scanner `ErrTooLong` suppresses the patch as invalid input; other scanner errors panic because the source is memory. Formatting builds To/Cc `mail.Address` lists, shortens long Fixes hashes to 12 chars, sorts/reverses tool names, prefixes Gemini tool labels, always includes syzbot in `Assisted-by`, and appends `base-commit`.

Dependencies and integration: it depends on `pkg/aflow/ai` recipient/fixes types and Go templates. `parser.go` uses `ParsePatch` for incoming messages; patch-generation flows use formatting helpers.

Risks: scanner default token size rejects very long diff lines. Diff parsing is heuristic and may stop on non-standard lines. Recipient display names are not independently sanitized here. Tests in `patch_test.go` cover many diff styles and formatting outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/patch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/patch_test.go -->
# sources/test-tools/syzkaller/pkg/email/patch_test.go

Purpose: `patch_test.go` validates incoming patch extraction and outgoing patch formatting.

Important tests: `TestParsePatch` covers git diffs, index lines, file mode lines, new files, Index-style diffs, multi-file patches, signature and quoted-reply cutoffs, empty input, and realistic kernel patch mail content. `TestFormatPatch` checks rendered descriptions with Fixes, Assisted-by, review/ack/test/report/link tags, signed-off-by lines, To/Cc addresses, base-commit, and tool ordering.

Control flow and state: parse tests are table-driven with expected exact diff strings, including trailing newline normalization. Format tests build `PatchTemplateData` and compare exact output.

Dependencies and integration: tests exercise `ParsePatch`, template rendering, `mail.Address` formatting, AI recipient/fixes types, and assisted-tool normalization.

Risks/test gaps: tests do not explicitly cover scanner-too-long behavior, malformed recipients, or `Closes` output despite template support. They provide strong regression coverage for the common patch shapes seen in mailing-list traffic.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/patch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/reply.go -->
# sources/test-tools/syzkaller/pkg/email/reply.go

Purpose: `reply.go` creates a quoted email reply body, placing syzbot response text near the relevant `#syz` command when possible.

Important APIs/functions: `FormReply` is the public formatter. `writeReply` inserts blank lines around the response and ensures it ends with a newline.

Control flow and state: `FormReply` scans the original body line by line, prefixes each line with `>` and adds a space unless the original line already starts with `>`. If the message contains exactly one command, the reply is inserted immediately after the first line beginning with `#syz`. If there are multiple commands or no command match, the reply is appended after the quoted body.

Dependencies and integration: it depends on the `Email` struct and `commandPrefix` from `parser.go`. It is used for public bot responses to parsed commands.

Risks: scanner default token limits apply to very long lines. Command attribution is deliberately disabled for multi-command messages. It only checks raw line prefix, so leading whitespace before `#syz` will not trigger inline insertion. Tests in `reply_test.go` cover the major quoting paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/reply.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/reply_test.go -->
# sources/test-tools/syzkaller/pkg/email/reply_test.go

Purpose: `reply_test.go` verifies quote formatting and reply insertion for command responses.

Important tests: `TestFormReply` covers insertion after `#syz` commands, alternate command syntaxes, already-quoted input lines, replies with and without trailing newline, appending when no command exists, and appending when multiple commands prevent attribution.

Control flow and state: table fixtures compare exact string output, including blank lines and quote prefixes.

Dependencies and integration: tests use minimal `Email` values and, for the multi-command case, populate `Commands` to force append-only behavior.

Risks/test gaps: no tests cover scanner errors or leading-space command lines. Exact formatting coverage is otherwise strong for intended behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/reply_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/sender/dashapi.go -->
# sources/test-tools/syzkaller/pkg/email/sender/dashapi.go

Purpose: `sender/dashapi.go` implements the generic email sender interface by delegating delivery to the syzkaller dashboard API.

Important APIs/types/functions: `DashapiConfig` configures dashboard client/address, sender address, context prefix, and subject prefix. `dashapiSender` holds config plus a dashboard client. `NewDashapiSender` constructs the client. `Send` builds a `dashapi.SendEmailReq`.

Control flow and state: `Send` starts from configured `From`. If the item has a `BugID`, it embeds context into the sender local part using `email.AddAddrContext` and `ContextPrefix`. It prefixes the subject, forwards To/Cc/InReplyTo/body, and returns an empty message ID plus any dashboard error.

Dependencies and integration: it depends on `dashboard/dashapi`, `net/mail`, and address-context helpers from `pkg/email`. It implements `sender.Sender` from `sender.go`.

Risks: callers do not receive a real outgoing message ID. Invalid configured From or context insertion errors abort send. Dashboard API errors propagate directly. No local tests cover this file; SMTP sender tests cover only the alternate implementation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/sender/dashapi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/sender/sender.go -->
# sources/test-tools/syzkaller/pkg/email/sender/sender.go

Purpose: `sender.go` defines the small abstraction shared by concrete email delivery backends.

Important APIs/types/functions: `Email` contains To, Cc, Subject, InReplyTo, Body, and BugID fields. `Sender` defines `Send(context.Context, *Email) (string, error)`, where the string is the produced message ID when the backend can provide it.

Control flow and state: this file has no behavior and no persistence. It is a contract used by SMTP and dashboard senders.

Dependencies and integration: it depends only on `context`. `dashapi.go` and `smtp.go` implement the interface, allowing higher-level code to choose delivery backend without changing message construction.

Risks: the abstraction is intentionally minimal; it does not model attachments, HTML bodies, envelope-specific recipients, or delivery metadata beyond a message ID. There are no direct tests, but concrete sender tests exercise the interface shape.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/sender/sender.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/sender/smtp.go -->
# sources/test-tools/syzkaller/pkg/email/sender/smtp.go

Purpose: `smtp.go` sends plain-text email through SMTP and constructs raw RFC822-style message bytes.

Important APIs/types/functions: `SMTPConfig` holds host, port, credentials, and From address. `NewSMTPSender` returns a `Sender`. `smtpSender.Send` handles message ID generation, envelope validation, TLS or standard SMTP delivery, and returns the message ID. `rawEmail` formats headers and body.

Control flow and state: `Send` generates a UUID-based message ID at the SMTP host, builds the raw message, parses To/Cc addresses for the SMTP envelope, sorts and deduplicates recipients, then either uses implicit TLS for port 465 or `smtp.SendMail` otherwise. The TLS path authenticates, issues MAIL/RCPT/DATA, writes the body, closes the data writer, and quits. `rawEmail` emits From/To/Cc/Subject/In-Reply-To/Message-ID/MIME headers and an 8bit text/plain body.

Dependencies and integration: it uses Go `net/smtp`, `crypto/tls`, `net/mail`, MIME Q encoding, UUIDs, and `slices`. It implements the generic `Sender` contract.

Risks: non-465 ports do not use STARTTLS. Header injection is mitigated for Subject by Q-encoding, but To/Cc display names are written as supplied while envelope parsing rejects invalid recipients. Context is only used for implicit TLS dialing. Tests cover raw formatting and invalid recipient rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/sender/smtp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/sender/smtp_test.go -->
# sources/test-tools/syzkaller/pkg/email/sender/smtp_test.go

Purpose: `smtp_test.go` validates raw SMTP message construction and recipient validation.

Important tests: `TestRawEmail` checks full header/body output with To, Cc, In-Reply-To, Message-ID, plain subject, subject containing CRLF injection text encoded safely, and a display name containing encoded CRLF-like text. `TestSendInvalidRecipients` verifies `Send` rejects malformed Cc and To addresses before attempting delivery.

Control flow and state: tests instantiate `smtpSender` directly with a fixed From address. `TestSendInvalidRecipients` uses an empty config, relying on recipient validation to fail before network use.

Dependencies and integration: tests exercise `rawEmail`, `mail.ParseAddress` envelope validation inside `Send`, and MIME Q-encoding behavior.

Risks/test gaps: tests do not start an SMTP server, so TLS and `smtp.SendMail` delivery paths are not integration-tested. They also do not verify recipient deduplication. Header construction edge cases are covered well for known injection concerns.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/sender/smtp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/wordwrap.go -->
# sources/test-tools/syzkaller/pkg/email/wordwrap.go

Purpose: `wordwrap.go` wraps plain text to a visual width while preserving existing line breaks, indentation, spacing between words, tabs, and long words.

Important APIs/functions: `WordWrap(text string, width int) string` is the public formatter. `visualLength(p int, s string) int` computes visual column position after adding a string, expanding tabs to 8-column stops and counting runes rather than bytes.

Control flow and state: width is clamped to at least 1. The function splits input by newline, preserves each line's leading whitespace, and then repeatedly extracts original whitespace and word segments from the trimmed remainder. A word preceded by spaces is either appended if it fits or moved to a new indented line with the separating spaces dropped. Empty lines are preserved. Single words longer than width are not split.

Dependencies and integration: this file uses only `strings` and `unicode`. It is suitable for formatting generated email text before sending.

Risks: trailing spaces are dropped when only whitespace remains. It treats all non-tab runes as width 1, so East Asian wide characters and combining marks are approximate. Tests in `wordwrap_test.go` cover indentation, tabs, trailing spaces, newlines, quotes, stack traces, and non-ASCII rune counting.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/wordwrap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/wordwrap_test.go -->
# sources/test-tools/syzkaller/pkg/email/wordwrap_test.go

Purpose: `wordwrap_test.go` verifies `WordWrap` and `visualLength` formatting contracts.

Important tests: `TestWordWrap` covers empty input, zero width, no wrap, simple wrap, exact width, long words, preserving paragraphs/blocks/list markers/quotes, indentation on wrapped lines, trailing-space removal, tab-aware wrapping, preserving internal spaces and tabs, final newline preservation, stack-trace text, and non-ASCII rune counting. `TestVisualLength` validates tab-stop calculations from several offsets and mixed strings.

Control flow and state: tests are table-driven and compare exact strings with `testify/require`.

Dependencies and integration: these tests define the output expected by any email text formatting caller.

Risks/test gaps: tests do not cover East Asian wide runes or combining marks, matching the implementation's simple rune-width model. Otherwise they provide strong regression coverage for wrapping semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/email/wordwrap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/flatrpc/conn.go -->
# sources/test-tools/syzkaller/pkg/flatrpc/conn.go

Purpose: `conn.go` implements size-prefixed FlatBuffers RPC transport over `net.Conn`, plus a TCP server wrapper and defensive parsing for executor messages.

Important APIs/types/functions: `Serv`, `Listen`, `Serv.Serve`, and `Serv.Close` manage server sockets. `Conn`, `NewConn`, `Close`, and `RemoteAddr` wrap connections. Generic `Send`, `Recv`, and `Parse` serialize object-API messages and unpack raw FlatBuffers messages. Verification helpers include `verify`, `verifyExecutorMessage`, and `verifyExecResult`. `statSent` and `statRecv` track traffic.

Control flow and state: server `Serve` accepts connections until listener close, runs handlers in an errgroup, closes connections on context cancellation, and treats non-temporary accept errors as fatal. `Send` is mutex-protected for concurrent writers and reuses a FlatBuffers builder. `Recv` is single-reader only; it compacts leftover buffered bytes, reads a 4-byte size prefix, rejects messages over 64 MiB, reads the full message, and parses the body. `Parse` recovers panics from corrupted FlatBuffers before unpacking.

Dependencies and integration: it depends on generated flatrpc raw types, FlatBuffers Go runtime, syzkaller stat/log packages, and errgroup. Executor verification limits allocation risk from untrusted test-machine data.

Risks: received object pointers are valid only until the next receive because buffers are reused. The receive path is not goroutine-safe. Verification currently special-cases executor messages only. Tests and fuzzing in `conn_test.go` cover round-trips and corrupted input resilience.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/flatrpc/conn.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/flatrpc/conn_test.go -->
# sources/test-tools/syzkaller/pkg/flatrpc/conn_test.go

Purpose: `conn_test.go` validates FlatRPC transport round-trips, provides a benchmark, and fuzzes corrupted receive data.

Important tests/functions: `TestConn` starts a local TCP server, exchanges `ConnectHello`, `ConnectRequest`, `ConnectReply`, and repeated `ExecutorMessage` values, then closes the server and checks handler completion. `BenchmarkConn` measures repeated request/reply cycles. `FuzzRecv` seeds a valid executor result, mutates size-prefixed byte streams through a socketpair, constrains memory with `debug.SetMemoryLimit`, skips large fuzz inputs, and repeatedly calls `Recv` until error.

Control flow and state: the test server runs `Serv.Serve` in a goroutine and uses generic `Send`/`Recv` with generated raw types. The fuzz test uses OS socketpairs to exercise real connection reads instead of direct parser calls.

Dependencies and integration: tests cover `Listen`, `Serve`, `NewConn`, `Send`, `Recv`, FlatBuffers packing/unpacking, and executor message verification. They depend on generated flatrpc types and `testify/assert`.

Risks/test gaps: concurrency of multiple simultaneous client connections and concurrent sends is not directly tested. Fuzzing focuses on executor messages and short inputs, but it directly targets the highest-risk corrupted-input path.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/flatrpc/conn_test.go -->
