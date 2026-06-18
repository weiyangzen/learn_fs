# subset-b-009138 research

Grouped research report for Kopia CLI policy, repository, restore, and server-control files under `sources/sync-backup/kopia/cli`. Each section preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_export.go -->
# sources/sync-backup/kopia/cli/command_policy_export.go

Purpose: implements `kopia policy export`, emitting defined policies as a JSON map keyed by `snapshot.SourceInfo.String()`. It supports exporting all policies, the global policy, or explicit targets, and can write either to stdout or a file.

Important APIs/types/functions: `commandPolicyExport`, `setup`, `run`, `getOutput`, `policyTargetFlags`, `policy.GetDefinedPolicy`, `policy.ListPolicies`, `json.Marshal`, `json.MarshalIndent`, and `exportFilePerms`. The hidden `--json-indent` flag changes formatting only.

Control flow: setup registers `--to-file`, `--overwrite`, target flags, and a repository-reader action. `run` opens output, resolves target-limited policies when `--global` or target arguments are present, otherwise lists all policies, marshals the map, writes a trailing newline, and closes file output through a joined defer path.

State/persistence behavior: repository state is read-only. File output is created with mode `0600` when exclusive creation is used; `--overwrite` uses `os.Create`, truncating an existing path. Passing `--overwrite` without `--to-file` is rejected.

Dependencies/integration: integrates policy target parsing, repository reader services, stdout abstraction, OS file creation, and policy JSON schemas. Risks/test signals: failures are mostly IO and target-resolution errors; JSON marshal is treated as impossible after typed map construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_export_test.go -->
# sources/sync-backup/kopia/cli/command_policy_export_test.go

Purpose: integration coverage for `policy export`, including default global policy output, target-specific export, path-to-source resolution, file output, overwrite behavior, pretty JSON, and error paths.

Important APIs/types/functions: `TestExportPolicy`, `testenv.NewCLITest`, `RunAndExpectSuccess`, `RunAndExpectFailure`, `testutil.MustParseJSONLines`, `snapshot.SourceInfo`, and `policy.Policy`.

Control flow: the test creates a filesystem repository with fixed user/host, exports the default global policy, sets a splitter policy on a temp directory, checks explicit full-source and local-path target export, exports all policies, writes to `--to-file`, verifies no overwrite by default, then verifies `--overwrite` and `--json-indent`.

State/persistence behavior: it mutates repository policy state through `policy set` and validates exported JSON against the expected in-memory policy map. It also creates and rereads a policy export file.

Dependencies/integration: depends on repository create/disconnect, policy set, policy export, filesystem temp paths, and JSON parsing. Risks/test signals: one assertion compares `expectedPolicy` against `policies5[id]` after overwrite instead of `policies7[id]`, but the surrounding length and parse checks still exercise overwrite output.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_export_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_import.go -->
# sources/sync-backup/kopia/cli/command_policy_import.go

Purpose: implements `kopia policy import`, reading a JSON map of target strings to `policy.Policy` values from a file or stdin and applying them to repository policy definitions.

Important APIs/types/functions: `commandPolicyImport`, `setup`, `run`, `deleteOthers`, `json.Decoder`, `DisallowUnknownFields`, `snapshot.ParseSourceInfo`, `policy.SetPolicy`, `policy.ListPolicies`, and `policy.RemovePolicy`.

Control flow: setup registers `--from-file`, `--allow-unknown-fields`, `--delete-other-policies`, and target flags. `run` opens the chosen input, decodes policies with unknown-field rejection by default, optionally computes a target allowlist, parses each imported source string relative to the repository client host/user, imports matching policies, and optionally deletes repository policies not imported.

State/persistence behavior: writes policy blobs through `repo.RepositoryWriter`. `--delete-other-policies` can remove any listed repository policy whose target string is not in the imported set after target filtering.

Dependencies/integration: integrates JSON schema compatibility, source-info parsing, policy storage, stdin/file services, and target filters. Risks/test signals: delete filtering compares target strings from the input, so noncanonical or locally parsed target forms must align with persisted `Target().String()` to avoid unexpected removals.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_import_test.go -->
# sources/sync-backup/kopia/cli/command_policy_import_test.go

Purpose: end-to-end coverage for importing policy JSON, target-limited imports, unknown-field handling, deletions, global-target equivalence, and invalid input failures.

Important APIs/types/functions: `TestImportPolicy`, `assertPoliciesEqual`, `json.Marshal`, `os.WriteFile`, `testutil.MustParseJSONLines`, `policy.DefaultPolicy`, and `snapshot.SourceInfo`.

Control flow: the test creates a repository, deep-copies the default global policy, writes JSON policy files, imports changes, adds local policies, restricts imports to `(global)` or a specific source, validates that deleted fields clear policy values, adds a second target, tests unknown fields with and without `--allow-unknown-fields`, and exercises `--delete-other-policies`.

State/persistence behavior: repository policies are repeatedly replaced and removed, and expected state is always validated through `policy export`, not direct internals. File state is a generated `policy.json`.

Dependencies/integration: depends on `policy export` for verification and on stable JSON names for `policy.Policy`. Risks/test signals: because it is integration-style, failures can originate in export, source parsing, or policy set serialization as well as import itself.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_import_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_ls.go -->
# sources/sync-backup/kopia/cli/command_policy_ls.go

Purpose: implements `kopia policy list`/`ls`, showing all defined policies in text or JSON form.

Important APIs/types/functions: `commandPolicyList`, `jsonOutput`, `textOutput`, `jsonList`, `policy.ListPolicies`, and `policy.TargetWithPolicy`.

Control flow: setup wires the command alias, JSON options, text output, and repository-reader action. `run` begins a JSON list wrapper, loads policies, sorts them by target string for deterministic output, and emits either JSON records including ID, target, and policy, or text lines containing policy ID and target.

State/persistence behavior: read-only over repository policy metadata. No policy inheritance is evaluated; the command lists defined policies only.

Dependencies/integration: integrates CLI output abstractions and the policy package's list API. Risks/test signals: text output is intentionally minimal and depends on deterministic `Target().String()` ordering; JSON consumers get one object per policy through the shared JSON list machinery.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_ls.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_remove.go -->
# sources/sync-backup/kopia/cli/command_policy_remove.go

Purpose: implements `kopia policy delete` with aliases `remove` and `rm`, removing defined policies for resolved policy targets.

Important APIs/types/functions: `commandPolicyDelete`, `policyTargetFlags`, `policyTargets`, `policy.RemovePolicy`, and the `--dry-run`/`-n` flag.

Control flow: setup registers target flags and dry-run, then uses a repository-writer action. `run` resolves all target arguments, logs each removal, skips mutation in dry-run mode, and otherwise calls `policy.RemovePolicy` per target.

State/persistence behavior: deletes policy definitions from the repository. Effective policy inheritance is not recomputed here; downstream policy lookups will fall back to parent/global definitions after removal.

Dependencies/integration: integrates target parsing and repository write transactions. Risks/test signals: removing multiple targets stops at the first remove error; dry-run still validates targets and logs intended changes, making it useful for target-resolution checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set.go -->
# sources/sync-backup/kopia/cli/command_policy_set.go

Purpose: central implementation of `kopia policy set`, coordinating many flag groups that mutate a `policy.Policy` definition for one or more targets.

Important APIs/types/functions: `commandPolicySet`, `setPolicyFromFlags`, helper functions `applyPolicyStringList`, `applyOptionalInt`, `applyOptionalInt64MiB`, `applyPolicyNumber64`, `applyPolicyBoolPtr`, `supportedCompressionAlgorithms`, `policy.GetDefinedPolicy`, and `policy.SetPolicy`.

Control flow: setup registers target flags, `--inherit`, and all sub-policy flag groups. `run` resolves targets, loads the existing defined policy or starts a new one for missing targets, applies all flag groups in a fixed order, rejects invocations with zero changes, and persists the result.

State/persistence behavior: writes complete defined policy objects. Optional pointer fields use nil to mean inherited/default, while scalar numeric fields use zero for inherited/default. String-list helpers build sorted unique lists from add/remove/clear operations.

Dependencies/integration: depends on compression registry, policy inheritance conventions, repository writer sessions, and all sibling flag structs. Risks/test signals: some helpers mutate earlier fields before returning an error from a later field, so callers must rely on the outer command not persisting when an error is returned.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_actions.go -->
# sources/sync-backup/kopia/cli/command_policy_set_actions.go

Purpose: implements `policy set` flags for snapshot action commands that run before/after folder traversal or snapshot root processing.

Important APIs/types/functions: `policyActionFlags`, `setActionsFromFlags`, `setActionCommandFromFlags`, `quoteArguments`, `policy.ActionCommand`, and `maxScriptLength`.

Control flow: setup registers four action flags, timeout, mode, and script persistence. For each action, `"-"` means unchanged, empty string removes the action, and any other value creates a `policy.ActionCommand`. With `--persist-action-script`, the value is read as a file and embedded as repository-stored script text; otherwise it is parsed as a space-separated CSV command line with quote handling.

State/persistence behavior: stores action commands inside policy definitions, either as command/argument arrays or embedded script text. Embedded scripts are capped at 32,000 bytes.

Dependencies/integration: uses `encoding/csv` for shell-like argument splitting, `os.ReadFile` for script capture, and policy action execution semantics elsewhere. Risks/test signals: command parsing is not a full shell parser; storing script contents in repository state can preserve sensitive local script content.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_actions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_compression.go -->
# sources/sync-backup/kopia/cli/command_policy_set_compression.go

Purpose: implements content and metadata compression policy flags for `policy set`.

Important APIs/types/functions: `policyCompressionFlags`, `policyMetadataCompressionFlags`, `setCompressionPolicyFromFlags`, `setMetadataCompressionPolicyFromFlags`, `compression.Name`, `compression.ByName`, `applyPolicyNumber64`, and `applyPolicyStringList`.

Control flow: setup registers `--compression`, `--metadata-compression`, min/max compression size strings, and add/remove/clear lists for only-compress and never-compress patterns. Setters apply size changes, map `inherit` to an empty compressor name, set explicit compressor names including `none`, and update sorted pattern lists.

State/persistence behavior: stores compression algorithm names and size thresholds directly in policy. Size thresholds are parsed as raw integer bytes, not human suffixes. Empty algorithm names mean inherited/default, while `"none"` is a concrete disabled value in display logic.

Dependencies/integration: depends on registered compression algorithms from `repo/compression` and on policy evaluation during snapshot upload. Risks/test signals: users may expect size suffix parsing; the CLI currently accepts only integer strings.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_compression.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_error_handling.go -->
# sources/sync-backup/kopia/cli/command_policy_set_error_handling.go

Purpose: implements `policy set` flags that control whether snapshot traversal ignores file read errors, directory read errors, and unknown filesystem entry types.

Important APIs/types/functions: `policyErrorFlags`, `setup`, `setErrorHandlingPolicyFromFlags`, `applyPolicyBoolPtr`, and `policy.ErrorHandlingPolicy`.

Control flow: setup registers three enum flags accepting `true`, `false`, or `inherit`. The setter applies each value to a `*policy.OptionalBool` field, wrapping parse errors with field-specific context.

State/persistence behavior: writes optional bool pointers into the policy. Nil means inherit/default; nonnil true/false overrides traversal behavior for the target.

Dependencies/integration: consumed by snapshot traversal and policy inheritance. Risks/test signals: the flag descriptions for directory and unknown-type errors have minor missing closing quotes, but enum validation prevents invalid values at CLI parse time; direct unit tests also exercise malformed values in the setter.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_error_handling.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_files.go -->
# sources/sync-backup/kopia/cli/command_policy_set_files.go

Purpose: implements file selection policy flags for ignores, dot-ignore files, maximum file size, filesystem-boundary traversal, and cache-directory ignores.

Important APIs/types/functions: `policyFilesFlags`, `setFilesPolicyFromFlags`, `applyPolicyNumber64`, `applyPolicyStringList`, `applyPolicyBoolPtr`, and `policy.FilesPolicy`.

Control flow: setup registers add/remove/clear variants for ignore rules and dot-ignore files, a `--max-file-size` string, `--one-file-system`, and `--ignore-cache-dirs`. The setter parses the scalar max size, updates list fields with sorted unique values, then applies optional booleans.

State/persistence behavior: stores ignore lists and traversal limits in policy definitions. `clear-*` sets lists to nil; scalar max size of zero means inherited/default.

Dependencies/integration: consumed by snapshot source traversal and ignore-rule evaluation. Risks/test signals: max file size uses a raw integer parser, unlike some user-facing size displays; list operations increment change count even when adding an existing value or removing a missing one.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_files.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_logging.go -->
# sources/sync-backup/kopia/cli/command_policy_set_logging.go

Purpose: implements policy flags controlling snapshot logging detail for directory and entry events.

Important APIs/types/functions: `policyLoggingFlags`, `setLoggingPolicyFromFlags`, `applyPolicyLogDetailPtr`, `policy.LoggingPolicy`, and `policy.LogDetail`.

Control flow: setup registers six string flags for directory snapshotted/ignored and entry snapshotted/ignored/cache-hit/cache-miss detail levels. The setter applies each through `applyPolicyLogDetailPtr`; empty means unchanged, `inherit` clears the pointer, and numeric values must be within `LogDetailNone` through `LogDetailMax`.

State/persistence behavior: stores optional log-detail pointers in nested logging policy fields. Nil inherits the parent/default value.

Dependencies/integration: affects snapshot logging verbosity, policy show output, and inheritance definitions. Risks/test signals: accepted values are numeric rather than named levels; validation prevents out-of-range values and is covered by integration tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_logging.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_logging_test.go -->
# sources/sync-backup/kopia/cli/command_policy_set_logging_test.go

Purpose: integration test for logging policy display, inheritance, overrides, inherit reset, and invalid numeric values.

Important APIs/types/functions: `TestSetLoggingPolicy`, `compressSpaces`, `testenv.NewCLITest`, `policy show`, and `policy set`.

Control flow: the test creates a repository, checks default global logging detail rows, checks inherited values for a temp directory, sets all six logging detail flags on the directory, verifies target-defined rows, resets one entry field to inherit, and asserts failures for negative, too-large, and nonnumeric inputs.

State/persistence behavior: mutates one local policy while observing effective inherited values from the global policy. Display assertions normalize repeated spaces to reduce formatting brittleness.

Dependencies/integration: spans `policy set`, `policy show`, policy inheritance, and display formatting. Risks/test signals: assertions depend on current default policy numeric detail levels and exact row labels.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_logging_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_os_snapshot.go -->
# sources/sync-backup/kopia/cli/command_policy_set_os_snapshot.go

Purpose: implements OS-level snapshot policy flags, currently the Windows Volume Shadow Copy mode.

Important APIs/types/functions: `policyOSSnapshotFlags`, `setOSSnapshotPolicyFromFlags`, `applyPolicyOSSnapshotMode`, `policy.OSSnapshotMode`, and string constants `never`, `always`, `when-available`, and `inherit`.

Control flow: setup registers `--enable-volume-shadow-copy` as an enum. The setter delegates to `applyPolicyOSSnapshotMode`, where empty means unchanged, `inherit`/`default` clears the pointer, and explicit modes allocate a `policy.OSSnapshotMode` pointer.

State/persistence behavior: stores optional OS snapshot mode under `policy.OSSnapshotPolicy.VolumeShadowCopy.Enable`. Nil inherits parent/default; concrete modes override behavior.

Dependencies/integration: consumed by OS-specific snapshot support during snapshot creation and shown by policy display. Risks/test signals: mode is available in policy regardless of runtime OS; actual behavior depends on platform-specific snapshot providers elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_os_snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_os_snapshot_test.go -->
# sources/sync-backup/kopia/cli/command_policy_set_os_snapshot_test.go

Purpose: integration test for Volume Shadow Copy policy defaults, global overrides, inherited display, and local override.

Important APIs/types/functions: `TestSetOSSnapshotPolicy`, `testenv.NewCLITest`, `policy show`, `policy set`, and shared `compressSpaces`.

Control flow: the test creates a repository, verifies the global default `never`, sets global mode to `when-available`, verifies a temp directory inherits it, changes global mode to `always`, verifies inherited update, then sets local mode to `never` and checks it is target-defined.

State/persistence behavior: mutates global and local policy definitions and validates effective inherited policy output.

Dependencies/integration: covers setter, policy inheritance, and show formatting. Risks/test signals: it does not exercise platform-specific VSS execution; it only validates policy storage and display.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_os_snapshot_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_retention.go -->
# sources/sync-backup/kopia/cli/command_policy_set_retention.go

Purpose: implements retention-related `policy set` flags for snapshot keep counts and identical-snapshot suppression.

Important APIs/types/functions: `policyRetentionFlags`, `setRetentionPolicyFromFlags`, `applyOptionalInt`, `applyPolicyBoolPtr`, and `policy.RetentionPolicy`.

Control flow: setup registers keep counts for latest/hourly/daily/weekly/monthly/annual snapshots and `--ignore-identical-snapshots`. The setter iterates a table of retention count fields, applying optional integer parsing and inheritance clearing, then applies the optional bool.

State/persistence behavior: stores keep counts as `*policy.OptionalInt` pointers. Nil means inherit/default; explicit integer zero can be represented if provided and means a concrete keep count rather than inheritance.

Dependencies/integration: consumed by snapshot retention/maintenance logic and displayed by policy show. Risks/test signals: integer parsing has no domain-specific min/max in this layer; invalid retention semantics must be enforced by policy consumers or lower validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_retention.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_scheduling.go -->
# sources/sync-backup/kopia/cli/command_policy_set_scheduling.go

Purpose: implements scheduling policy flags for interval snapshots, times of day, crontab expressions, missed-run behavior, and manual-only snapshots.

Important APIs/types/functions: `policySchedulingFlags`, `setSchedulingPolicyFromFlags`, `setScheduleFromFlags`, `setRunMissedFromFlags`, `splitCronExpressions`, `setManualFromFlags`, `policy.TimeOfDay`, and `policy.ValidateSchedulingPolicy`.

Control flow: setup registers duration-list interval, comma-separated times, semicolon-separated cron, `run-missed`, and `manual`. Manual mode rejects simultaneous schedule flags, clears existing interval/times/cron, then sets `Manual`. Schedule mode applies first interval value, parses and deduplicates times, splits cron entries, validates cron policy, applies `run-missed`, and clears prior manual mode.

State/persistence behavior: stores interval seconds, sorted time-of-day slices, cron slices, optional `RunMissed`, and manual bool in the policy. `inherit`/`default` clears time or cron slices.

Dependencies/integration: consumed by server/KopiaUI scheduled snapshots. Risks/test signals: only the first interval list value is used; comment-only cron expressions are preserved and validated by policy logic.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_scheduling.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_splitter.go -->
# sources/sync-backup/kopia/cli/command_policy_set_splitter.go

Purpose: implements `policy set --splitter`, overriding the object splitter algorithm for a policy target.

Important APIs/types/functions: `policySplitterFlags`, `setSplitterPolicyFromFlags`, `supportedSplitterAlgorithms`, `splitter.SupportedAlgorithms`, and `policy.SplitterPolicy`.

Control flow: setup registers an enum containing `inherit` and all supported splitter algorithms. The setter leaves empty values unchanged, clears `p.Algorithm` for `inherit`, or stores the explicit algorithm string and increments the change count.

State/persistence behavior: splitter override is a string in the policy. Empty string means inherited/repository default; explicit values override object chunking for affected snapshots.

Dependencies/integration: depends on the splitter registry and policy evaluation during content upload. Risks/test signals: changing splitters affects deduplication boundaries for future snapshots, so policy changes can have storage-efficiency implications even though this layer only stores a string.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_splitter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_splitter_test.go -->
# sources/sync-backup/kopia/cli/command_policy_set_splitter_test.go

Purpose: integration test for splitter policy default display, local override, inherit reset, and invalid algorithm rejection.

Important APIs/types/functions: `TestSetSplitterPolicy`, `testenv.NewCLITest`, `policy show`, `policy set`, and `compressSpaces`.

Control flow: the test creates a repository, verifies the global repository-default splitter row, verifies local inherited display for a temp directory, sets `FIXED-4M`, verifies it is target-defined, resets with `inherit`, and expects failure for a nonexistent splitter.

State/persistence behavior: creates and clears a local splitter override while preserving global default behavior.

Dependencies/integration: spans CLI enum validation, policy persistence, inheritance, and display formatting. Risks/test signals: test assumes `FIXED-4M` is present in the supported splitter registry.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_splitter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_test.go -->
# sources/sync-backup/kopia/cli/command_policy_set_test.go

Purpose: focused unit tests for setter helpers in `policy set`, especially error-handling optional bools and scheduling policy transitions.

Important APIs/types/functions: `TestSetErrorHandlingPolicyFromFlags`, `TestSetSchedulingPolicyFromFlags`, `policyErrorFlags`, `policySchedulingFlags`, `policy.ErrorHandlingPolicy`, `policy.SchedulingPolicy`, and `testlogging.Context`.

Control flow: the error-handling table covers no-op, malformed input, partial mutation before error, inherit clearing, true/false overrides, and mixed values. The scheduling table covers no-op, manual mode, interval, times of day, invalid manual/schedule combinations, clearing existing schedules when manual is set, resetting manual when schedules are set, cron parsing, invalid cron validation, inherited cron, and `RunMissed`.

State/persistence behavior: tests mutate in-memory policy structs and count changes; no repository is opened. The tests explicitly document that setters may partially mutate before returning errors.

Dependencies/integration: validates local helper semantics independent of kingpin enum parsing and repository writes. Risks/test signals: one error-handling test ignores returned errors/change-count assertions, so its main signal is final struct shape rather than exact error propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_upload.go -->
# sources/sync-backup/kopia/cli/command_policy_set_upload.go

Purpose: implements upload concurrency policy flags for file reads, server/UI snapshot parallelism, and threshold for parallel upload.

Important APIs/types/functions: `policyUploadFlags`, `setUploadPolicyFromFlags`, `applyOptionalInt`, `applyOptionalInt64MiB`, and `policy.UploadPolicy`.

Control flow: setup registers `--max-parallel-file-reads`, `--max-parallel-snapshots`, and `--parallel-upload-above-size-mib`. The setter applies optional integer parsing to the first two and parses the threshold as MiB, converting to bytes.

State/persistence behavior: stores optional integer pointers in upload policy. Nil means inherited/default. The threshold conversion persists bytes even though the CLI accepts MiB.

Dependencies/integration: consumed by snapshot upload workers and server/UI scheduling paths. Risks/test signals: parser accepts raw integers only; negative values are not rejected in this layer unless lower policy validation rejects them elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_upload_test.go -->
# sources/sync-backup/kopia/cli/command_policy_set_upload_test.go

Purpose: integration test for upload policy default display, inherited display, global overrides, and reset to default.

Important APIs/types/functions: `TestSetUploadPolicy`, `testenv.NewCLITest`, `policy show`, `policy set`, and `compressSpaces`.

Control flow: the test creates a repository, checks global upload defaults, checks inherited values on a temp directory, sets global max parallel snapshots, max file reads, and parallel threshold, verifies inherited display reflects the global changes, then resets all three with `default`.

State/persistence behavior: mutates only global upload policy and observes inherited effective policy for a local source.

Dependencies/integration: covers setter conversion from MiB to bytes and display via `units.BytesString`. Risks/test signals: display strings like `2.1 GB` and `4.3 GB` depend on unit formatting conventions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_upload_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_show.go -->
# sources/sync-backup/kopia/cli/command_policy_show.go

Purpose: implements `kopia policy show`/`get`, displaying effective policy for one or more targets as JSON or a human-aligned text table with definition/inheritance annotations.

Important APIs/types/functions: `commandPolicyShow`, `policy.GetEffectivePolicy`, `printPolicy`, `policyTableRow`, `alignedPolicyTableRows`, `definitionPointToString`, and append helpers for retention, files, error handling, scheduling, upload, compression, metadata compression, splitter, actions, OS snapshots, and logging.

Control flow: setup registers target and JSON flags. `run` resolves targets, loads effective policy plus definition provenance, and emits JSON or formatted text. Text formatting builds rows by policy category, computes alignment widths, and appends provenance such as `(defined for this target)` or `inherited from ...`.

State/persistence behavior: read-only. It displays effective values after inheritance resolution, not merely defined local policy fields.

Dependencies/integration: depends on policy definition tracking, source-info rendering, unit formatting, and action command formatting. Risks/test signals: output is user-facing and heavily asserted by policy tests; changes to row labels, defaults, or alignment may break tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_show.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repo_status_test.go -->
# sources/sync-backup/kopia/cli/command_repo_status_test.go

Purpose: smoke test for repository status text and JSON output.

Important APIs/types/functions: `TestRepoStatusJSON`, `cli.RepositoryStatus`, `testenv.NewCLITest`, and `testutil.MustParseJSONLines`.

Control flow: the test creates a filesystem repository, runs `repo status` in text mode, then runs `repo status --json` and parses the output into `cli.RepositoryStatus`.

State/persistence behavior: creates and connects a repository, then reads connection/config metadata. No repository parameters are changed.

Dependencies/integration: covers repository create, status, JSON output, and config file handling. Risks/test signals: it validates JSON parseability but does not assert specific status fields, so it catches gross serialization failures rather than semantic regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repo_status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repo_throttle_test.go -->
# sources/sync-backup/kopia/cli/command_repo_throttle_test.go

Purpose: integration test for repository throttling get/set behavior, unlimited values, invalid negatives, and JSON output.

Important APIs/types/functions: `TestRepoThrottle`, `throttling.Limits`, `testenv.NewCLITest`, `repo throttle get`, `repo throttle set`, and `testutil.MustParseJSONLines`.

Control flow: the test creates a filesystem repository, verifies all throttle limits start unlimited, sets download/upload speeds, request rates, and concurrent read/write limits, checks negative values fail, verifies formatted text output, resets two values to `unlimited`, and parses JSON output into `throttling.Limits`.

State/persistence behavior: mutates the repository throttler limits in the active direct repository and reads them back through the same CLI layer.

Dependencies/integration: depends on common throttle flag helpers, repository throttler persistence, unit formatting, and JSON output. Risks/test signals: text expectations are exact, including spacing and `GB/s` formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repo_throttle_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository.go -->
# sources/sync-backup/kopia/cli/command_repository.go

Purpose: top-level repository command registrar for `kopia repository` and alias `repo`.

Important APIs/types/functions: `commandRepository`, `setup`, and subcommand fields for connect, create, disconnect, repair, set-client, set-parameters, status, sync-to, throttle, change-password, validate-provider, and upgrade.

Control flow: setup creates the parent command and delegates setup to each subcommand in a fixed order. There is no run method or state mutation in this file.

State/persistence behavior: none directly; it wires command handlers that manage repository config files, format blobs, storage, and runtime state elsewhere.

Dependencies/integration: central integration point for advanced app services and kingpin command tree construction. Risks/test signals: missing a subcommand registration here makes otherwise implemented functionality unreachable from CLI.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_change_password.go -->
# sources/sync-backup/kopia/cli/command_repository_change_password.go

Purpose: implements `repository change-password`, changing the repository format password and updating local password persistence.

Important APIs/types/functions: `commandRepositoryChangePassword`, `askForChangedRepositoryPassword`, `repo.DirectRepositoryWriter`, `rep.FormatManager().ChangePassword`, and `passwordPersistenceStrategy().PersistPassword`.

Control flow: setup registers `--new-password` with an environment variable override and direct repository write action. `run` obtains the new password from flag or interactive prompt, calls the format manager password-change API, logs success, and persists the new password for the repository config.

State/persistence behavior: mutates the repository format password and local password store. Existing clients with cached old credentials may fail after the change, especially with format blob cache disabled.

Dependencies/integration: depends on format version support for password changes, direct repository access, password prompting, and password persistence backend. Risks/test signals: failure after repository password change but before local persistence could leave repository updated while local convenience credentials remain stale.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_change_password.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_change_password_test.go -->
# sources/sync-backup/kopia/cli/command_repository_change_password_test.go

Purpose: format-specific integration test for repository password changes and old/new password behavior across clients.

Important APIs/types/functions: `TestRepositoryChangePassword`, `formatSpecificTestSuite`, `testenv.NewCLITest`, and `format.FormatVersion1`.

Control flow: the test creates two CLI environments/runners, creates a filesystem repository with format cache disabled, rejects change-password for format v1, otherwise connects a second client, changes the password from the first client, verifies the second client and new connections with the old password fail, then verifies a new connection succeeds with `KOPIA_PASSWORD=newPass`.

State/persistence behavior: changes the repository password and local password state for `env1`; `env2` uses stale credentials and fails after the format update.

Dependencies/integration: covers format manager password changes, connection cache behavior, environment-supplied password, and snapshot listing as an operational probe. Risks/test signals: relies on disabled format cache to make password change immediately visible.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_change_password_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_connect.go -->
# sources/sync-backup/kopia/cli/command_repository_connect.go

Purpose: implements `repository connect` for storage providers and shared connection options used by both connect and create.

Important APIs/types/functions: `commandRepositoryConnect`, `connectOptions`, `toRepoConnectOptions`, `getFormatBlobCacheDuration`, `App.runConnectCommandWithStorage`, `App.runConnectCommandWithStorageAndPassword`, `repo.Connect`, and `passwordpersist.OnSuccess`.

Control flow: setup registers shared cache/client flags, API-server connect subcommand, and one storage-provider subcommand per registered provider. Provider actions connect to blob storage, prompt/read password, then call repo connect. Connection options include cache directory/sizes, host/user override, read-only, permissive cache loading, description, action enablement, update checks, and format-blob cache control.

State/persistence behavior: writes or updates the local repository config file and persists the password only after successful `repo.Connect`. It does not initialize repository storage.

Dependencies/integration: depends on storage provider flags, password services, content cache settings, repo config, and update-check initialization. Risks/test signals: permissive cache loading is only meaningful for read-only repositories but this layer records the option without enforcing that relationship.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_connect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_connect_from_config.go -->
# sources/sync-backup/kopia/cli/command_repository_connect_from_config.go

Purpose: storage provider implementation named `from-config`, allowing connect/create operations from a repository config file or encoded storage token.

Important APIs/types/functions: `storageFromConfigFlags`, `Setup`, `Connect`, `connectToStorageFromConfigFile`, `connectToStorageFromConfigToken`, `connectToStorageFromStorageConfigFile`, `connectToStorageFromStorageConfigStdin`, `repo.LoadConfigFromFile`, `repo.DecodeToken`, `repo.EncodeToken` counterpart, and `blob.NewStorage`.

Control flow: setup registers `--file`, `--token`, `--token-file`, and `--token-stdin`. For connect, `--file` loads an existing config with blob storage connection info. Token inputs decode connection info and an optional password, set the password service from the token when present, and open storage.

State/persistence behavior: this provider opens blob storage only; actual repo config creation is handled by connect/create callers. Tokens can carry the repository password into password flags.

Dependencies/integration: registered through `mustRegisterStorageProvider` in `init`. Risks/test signals: server-only connection files are rejected because this provider requires blob storage parameters.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_connect_from_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_connect_server.go -->
# sources/sync-backup/kopia/cli/command_repository_connect_server.go

Purpose: implements `repository connect server`, connecting the local CLI to a Kopia API server instead of direct blob storage.

Important APIs/types/functions: `commandRepositoryConnectServer`, `repo.APIServerInfo`, `repo.ConnectAPIServer`, `connectOptions.toRepoConnectOptions`, `passwordpersist.OnSuccess`, and `repo.SupportedLocalCacheKeyDerivationAlgorithms`.

Control flow: setup registers required `--url`, optional server certificate fingerprint, and hidden local-cache key derivation algorithm. `run` trims trailing slashes from the base URL, lowercases the fingerprint, resolves default username/hostname for logging, obtains the password, connects to the API server, persists password on success, logs completion, and initializes update checks.

State/persistence behavior: writes local repository config for an API-server connection, not direct storage. Password persistence is tied to the server connection config file.

Dependencies/integration: integrates API client trust configuration, local cache key derivation, password prompting, and shared connect options. Risks/test signals: a missing or wrong certificate fingerprint affects TLS trust at connect/open time rather than during this file's option construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_connect_server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_create.go -->
# sources/sync-backup/kopia/cli/command_repository_create.go

Purpose: implements `repository create`, initializing a new repository in a storage provider, optionally connecting to it, setting default policy, and default maintenance parameters.

Important APIs/types/functions: `commandRepositoryCreate`, `newRepositoryOptionsFromFlags`, `ensureEmpty`, `runCreateCommandWithStorage`, `populateRepository`, `repo.Initialize`, `repo.Open`, `repo.WriteSession`, `policy.SetPolicy`, and `setDefaultMaintenanceParameters`.

Control flow: setup registers content format, encryption, ECC, splitter, format version, retention, create-only, key-derivation, shared connect flags, and provider subcommands. Creation verifies storage is empty, obtains a password, builds `repo.NewRepositoryOptions`, initializes storage, optionally connects with the same password, opens the repository, writes default global policy and maintenance parameters, and prints validation guidance.

State/persistence behavior: writes the repository format blob and initial repository contents to blob storage; when not create-only it also writes local config and password persistence.

Dependencies/integration: depends on registered hash/encryption/ECC/splitter algorithms, blob storage listing, repository initialization, policy defaults, and maintenance setup. Risks/test signals: `ensureEmpty` treats any listed blob as existing data and stops before initialization, protecting against accidental overwrite.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_create_test.go -->
# sources/sync-backup/kopia/cli/command_repository_create_test.go

Purpose: tests repository create/connect behavior using the `from-config` provider with token files and stdin.

Important APIs/types/functions: `TestRepositoryCreateWithConfigFile`, `TestRepositoryCreateWithConfigFromStdin`, `repo.EncodeToken`, `blob.ConnectionInfo`, `filesystem.Options`, and `testenv.NewCLITest`.

Control flow: the first test checks failure messages for invalid create/connect arguments and bad tokens, writes an encoded filesystem storage token to a file, and creates the repository from `--token-file`. The second test pushes the token through runner stdin and creates with `--token-stdin`.

State/persistence behavior: creates a filesystem repository via decoded storage connection info; temp token files are written with `0600`.

Dependencies/integration: covers token decoding, storage provider registration, stdin handling, and create initialization. Risks/test signals: exact error substring assertions couple the test to provider validation wording.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_disconnect.go -->
# sources/sync-backup/kopia/cli/command_repository_disconnect.go

Purpose: implements `repository disconnect`, removing the local repository configuration.

Important APIs/types/functions: `commandRepositoryDisconnect`, `setup`, `run`, `svc.noRepositoryAction`, and `repo.Disconnect`.

Control flow: setup creates the command under advanced services and uses a no-repository action, meaning it does not require successfully opening the configured repository. `run` calls `repo.Disconnect` on the configured repository config file path and logs completion.

State/persistence behavior: removes or invalidates the local connection config; it does not delete repository data from blob storage.

Dependencies/integration: depends on repository config file naming and disconnect semantics in the repo package. Risks/test signals: because no repository open is required, disconnect can clean up broken or inaccessible local configs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_disconnect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_repair.go -->
# sources/sync-backup/kopia/cli/command_repository_repair.go

Purpose: hidden deprecated repair command for recovering the `kopia.repository` format blob from older-format pack replicas.

Important APIs/types/functions: `commandRepositoryRepair`, `packBlockPrefixes`, `runRepairCommandWithStorage`, `recoverFormatBlob`, `format.RecoverFormatBlob`, `format.KopiaRepositoryBlobID`, `content.PackBlobIDPrefixes`, and `blob.Storage`.

Control flow: setup registers hidden provider subcommands and dangerous-command gating. The run path optionally checks whether the format blob already exists in `auto`, resolves search prefixes, lists blobs under those prefixes, attempts recovery from each blob, and writes the recovered bytes back as the repository format blob unless dry-run is set.

State/persistence behavior: can create the format blob in repository storage. Dry-run performs discovery without writing. It never modifies pack blobs.

Dependencies/integration: depends on low-level blob storage access and legacy format replicas. Risks/test signals: intentionally dangerous and hidden; a false positive recovery or wrong storage target could write an invalid format blob.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_repair.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_set_client.go -->
# sources/sync-backup/kopia/cli/command_repository_set_client.go

Purpose: implements `repository set-client`, mutating local client options stored in the repository config file.

Important APIs/types/functions: `commandRepositorySetClient`, `rep.ClientOptions`, `repo.SetClientOptions`, read-only/read-write flags, description/username/hostname list flags, permissive cache loading, and format-blob cache flags.

Control flow: setup registers client option flags and uses a repository-reader action. `run` copies current client options, applies requested changes, rejects no-op invocations, and persists the changed options to the local config file.

State/persistence behavior: updates local config only; repository storage and format parameters are not changed. Read-only mode, user/host identity, description, permissive cache loading, and format cache duration affect future opens.

Dependencies/integration: integrates app config path services and repo config persistence. Risks/test signals: the permissive cache loading branch appears inverted in its condition/logging, so setting it when currently false logs that the repository fails on bad index blobs without enabling the option.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_set_client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_set_parameters.go -->
# sources/sync-backup/kopia/cli/command_repository_set_parameters.go

Purpose: implements `repository set-parameters`, mutating repository-wide format parameters, blob retention config, epoch-manager settings, and test-only required features.

Important APIs/types/functions: `commandRepositorySetParameters`, `updateRepositoryParameters`, `updateEpochParameters`, `disableBlobRetention`, `addRemoveUpdateRequiredFeatures`, `FormatManager().SetParameters`, `maintenance.CheckExtendRetention`, and `ContentManager().PrepareUpgradeToIndexBlobManagerV1`.

Control flow: setup registers max pack size, index version, retention mode/period, `--upgrade`, epoch tuning flags, and hidden required-feature flags. `run` loads mutable parameters, blob config, and required features; applies requested changes; prevents index-format downgrade; validates retention against maintenance; migrates to epoch manager when needed; persists parameters and optionally writes a legacy-index poison blob.

State/persistence behavior: changes the repository format blob and may rewrite index state during epoch-manager upgrade. Blob retention settings are stored in blob storage configuration. Required features can block future clients that do not understand them.

Dependencies/integration: touches format, epoch, feature gating, maintenance retention, and content index migration. Risks/test signals: high blast radius; the command warns that other clients must disconnect and reconnect after updates.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_set_parameters.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_set_parameters_test.go -->
# sources/sync-backup/kopia/cli/command_repository_set_parameters_test.go

Purpose: format-specific integration tests for repository parameter mutation, retention settings, format upgrades, downgrade prevention, required features, and server reaction to new unsupported features.

Important APIs/types/functions: `setupInMemoryRepo`, `TestRepositorySetParameters`, `TestRepositorySetParametersRetention`, `TestRepositorySetParametersUpgrade`, `TestRepositorySetParametersDowngrade`, `TestRepositorySetParametersRequiredFeatures`, and `TestRepositorySetParametersRequiredFeatures_ServerMode`.

Control flow: tests create in-memory repositories, inspect status defaults, check no-op output, validate failure cases, set index/max-pack settings, enable/update/disable retention, upgrade to latest epoch format, set epoch tunables, reject invalid tunables, prevent index downgrades, add/remove unknown required features, and verify a running server exits when it encounters a new required feature.

State/persistence behavior: mutates repository format and retention metadata repeatedly and checks state through `repository status` and `index epoch list`.

Dependencies/integration: spans format versions, in-memory reconnectable storage, maintenance validation, server start, policy scheduling, and required-feature gates. Risks/test signals: server-mode test is timing-sensitive because it waits for scheduled snapshot activity to notice the unsupported feature.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_set_parameters_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_status.go -->
# sources/sync-backup/kopia/cli/command_repository_status.go

Purpose: implements `repository status`, displaying local client options, storage information, content/object format, epoch/retention/upgrade state, required features, and optional reconnect tokens.

Important APIs/types/functions: `commandRepositoryStatus`, `RepositoryStatus`, `outputJSON`, `dumpUpgradeStatus`, `dumpRetentionStatus`, `run`, `outputRequiredFeatures`, `scanCacheDir`, `scrubber.ScrubSensitiveData`, and `dr.Token`.

Control flow: setup registers reconnect-token flags and JSON output. Text mode prints config path, client options, storage type/capacity/config, unique ID, hash/encryption/splitter, format version, content compression, password-change support, required features, pack/index settings, epoch manager details, retention, and upgrade lock status. Token mode optionally includes password and prints a reconnect command.

State/persistence behavior: read-only, except it may request the password to include in a reconnect token. JSON mode scrubs sensitive storage config before output.

Dependencies/integration: integrates direct repository introspection, blob volume capacity, format manager, epoch manager, upgrade lock intent, and output scrubbing. Risks/test signals: reconnect tokens with password are explicitly sensitive and trivially decodable.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_sync.go -->
# sources/sync-backup/kopia/cli/command_repository_sync.go

Purpose: implements `repository sync-to`, copying raw repository blobs from the currently connected direct repository to another storage provider, optionally updating newer blobs, deleting extras, and preserving timestamps.

Important APIs/types/functions: `commandRepositorySyncTo`, `runSyncWithStorage`, `listDestinationBlobs`, `runSyncBlobs`, `sliceToChannel`, `syncCopyBlob`, `syncDeleteBlob`, `ensureRepositoriesHaveSameFormatBlob`, `parseUniqueID`, `errgroup`, `gather.WriteBuffer`, and `blob.Storage`.

Control flow: setup registers sync flags and provider subcommands. The run path opens the source as a direct repository, verifies destination format blob is missing or has the same unique ID, lists destination metadata, lists source blobs to compute copy/update/in-sync sets, optionally builds delete set, exits on dry-run, then parallel workers copy blobs first and delete extra blobs second.

State/persistence behavior: writes the destination repository format blob when absent unless `--must-exist` is set, copies blob bytes, optionally sets modification times, and deletes destination-only blobs only with `--delete`.

Dependencies/integration: raw blob storage APIs, progress reporting, format JSON parsing, and direct repository access. Risks/test signals: sync is storage-level replication; incompatible unique IDs are blocked, but concurrent source mutation can still race with blob listing/copying.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_sync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_throttle.go -->
# sources/sync-backup/kopia/cli/command_repository_throttle.go

Purpose: groups repository throttling subcommands under `repository throttle`.

Important APIs/types/functions: `commandRepositoryThrottle`, `commandRepositoryThrottleGet`, `commandRepositoryThrottleSet`, and `setup`.

Control flow: setup creates the parent command and delegates registration to `get` and `set`. There is no execution logic in this file.

State/persistence behavior: none directly; child commands read or mutate throttler limits on the active direct repository.

Dependencies/integration: thin command-tree integration point. Risks/test signals: if either child setup is omitted, throttle operations become unreachable despite their implementations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_throttle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_throttle_get.go -->
# sources/sync-backup/kopia/cli/command_repository_throttle_get.go

Purpose: implements `repository throttle get`, displaying current repository throttling limits.

Important APIs/types/functions: `commandRepositoryThrottleGet`, `commonThrottleGet`, `repo.DirectRepository`, `rep.Throttler().Limits`, and `ctg.output`.

Control flow: setup registers common output flags and a direct repository read action. `run` obtains current throttler limits and delegates text/JSON output formatting to the shared throttle output helper.

State/persistence behavior: read-only over runtime/repository throttler state.

Dependencies/integration: depends on direct repository access and common throttle formatting shared with server throttling. Risks/test signals: output behavior is covered by repo and server throttle integration tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_throttle_get.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_throttle_set.go -->
# sources/sync-backup/kopia/cli/command_repository_throttle_set.go

Purpose: implements `repository throttle set`, changing direct repository throttling limits.

Important APIs/types/functions: `commandRepositoryThrottleSet`, `commonThrottleSet`, `repo.DirectRepositoryWriter`, `Throttler().Limits`, `cts.apply`, and `Throttler().SetLimits`.

Control flow: setup registers common throttle-set flags and a direct repository write action. `run` copies current limits, applies requested flag changes while counting mutations, logs no-op when nothing changed, and persists the new limits through the throttler.

State/persistence behavior: mutates repository throttler limits. The limits affect repository blob/content IO throttling after the update.

Dependencies/integration: shares validation and parsing with server throttle setters. Risks/test signals: only changed when common helper increments change count; invalid negative values are rejected by helper logic before persistence.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_throttle_set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_upgrade.go -->
# sources/sync-backup/kopia/cli/command_repository_upgrade.go

Purpose: hidden experimental repository format upgrade workflow, with explicit lock intent, client drain, epoch index migration, validation, commit, and rollback commands.

Important APIs/types/functions: `commandRepositoryUpgrade`, `setLockIntent`, `drainOrCommit`, `drainAllClients`, `upgrade`, `validateAction`, `commitUpgrade`, `forceRollbackAction`, `runPhase`, `ignoreErrorOnAlwaysCommit`, `CheckIndexInfo`, `loadIndexBlobs`, `format.UpgradeLockIntent`, and `ContentManager().PrepareUpgradeToIndexBlobManagerV1`.

Control flow: setup gates use on `KOPIA_UPGRADE_LOCK_ENABLED`, registers `begin`, `rollback`, and `validate`. `begin` chains phases: place lock intent, wait for drain or proceed, migrate indexes to epoch format when needed, compare old/new index blobs, and commit the upgrade unless test commit mode says never. Errors set a `skip` flag to stop subsequent phases.

State/persistence behavior: writes upgrade lock intent, may block non-owner clients, rewrites index metadata to V1/epoch format, updates mutable format parameters, commits or rolls back upgrade state, and cleans rollback backups through format manager.

Dependencies/integration: high-risk integration with repository clocks, format blob cache timings, owner IDs, index readers, and content managers. Risks/test signals: explicitly warns of corruption/data-loss risk; validation compares critical `content.Info` fields but stops at first mismatch per pair due switch structure.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_upgrade.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_upgrade_test.go -->
# sources/sync-backup/kopia/cli/command_repository_upgrade_test.go

Purpose: format-specific integration and unit coverage for experimental repository upgrade behavior.

Important APIs/types/functions: `TestRepositoryUpgrade`, `TestRepositoryCorruptedUpgrade`, `TestRepositoryUpgradeCommitNever`, `TestRepositoryUpgradeCommitAlways`, `TestRepositoryUpgradeStatusWhileLocked`, `lockRepositoryForUpgrade`, and `TestRepositoryUpgrade_checkIndexInfo`.

Control flow: tests create repositories across format versions, enable the upgrade environment gate, run upgrade begin with short unsafe timing, verify format-version-specific messages and final status, leave locks with commit-mode never, corrupt migrated indexes to force validation failure, force always commit, inspect locked status as owner/non-owner, rollback locks, wait for drain, finalize upgrade, and unit-test each `CheckIndexInfo` mismatch field.

State/persistence behavior: mutates repository format, upgrade locks, and index blobs; one test intentionally corrupts repository files for validation coverage.

Dependencies/integration: spans filesystem storage, format versions, upgrade owner IDs, lock timing, index epoch status, and status command. Risks/test signals: `TestRepositoryUpgradeStatusWhileLocked` includes a real 62-second sleep for drain behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_upgrade_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_validate_provider.go -->
# sources/sync-backup/kopia/cli/command_repository_validate_provider.go

Purpose: implements `repository validate-provider`, running blob storage validation against the connected direct repository storage.

Important APIs/types/functions: `commandRepositoryValidateProvider`, `blobtesting.Options`, `blobtesting.Verify`, `repo.DirectRepositoryWriter`, and `dr.BlobStorage()`.

Control flow: setup registers the command with the advanced direct repository write action and exposes validation flags from `blobtesting.Options`. `run` passes the direct repository's blob storage to `blobtesting.Verify`.

State/persistence behavior: validation may write, read, list, and delete test blobs in repository storage according to blobtesting behavior. It does not change repository format metadata intentionally.

Dependencies/integration: depends on direct storage access, provider capabilities, and blobtesting validation logic. Risks/test signals: intended after repository creation to verify provider compatibility; running against production storage still performs live storage operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_validate_provider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_restore.go -->
# sources/sync-backup/kopia/cli/command_restore.go

Purpose: implements `kopia restore`, restoring snapshot/object contents to local filesystem or archive outputs, and expanding shallow placeholder files in place.

Important APIs/types/functions: `commandRestore`, `restoreSourceTarget`, `RestoreProgress`, `constructTargetPairs`, `restoreOutput`, `detectRestoreMode`, `setupPlaceholderExpansion`, `run`, `tryToConvertPathToID`, `createSnapshotTimeFilter`, `computeMaxTime`, `findLastManifestWithPath`, `restore.Entry`, and `snapshotfs`.

Control flow: setup registers source args and restore flags for overwrite, sparse files, attributes, mode, parallelism, skip metadata, incremental/delete-extra, shallow placeholders, snapshot time, and flushing. `run` builds an output, resolves each source either from placeholders or object IDs/paths, obtains a root filesystem entry, invokes `restore.Entry` with progress callback and options, flushes progress, and logs stats.

State/persistence behavior: writes restored files/directories/symlinks, zip/tar/tgz archives, or placeholder expansions on local disk. Repository is read-only. Path-source restore resolves latest/oldest/time-bounded complete snapshot manifests before restoring.

Dependencies/integration: integrates localfs, snapshot manifests, object IDs, restore outputs, progress UI, archive writers, time parsing, and policy-independent snapshotfs lookup. Risks/test signals: restore can overwrite/delete local files depending on flags; archive outputs are created with `os.Create`, truncating existing target files.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_restore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_restore_test.go -->
# sources/sync-backup/kopia/cli/command_restore_test.go

Purpose: unit tests for restore snapshot-time parsing and latest/oldest filter construction.

Important APIs/types/functions: `TestRestoreSnapshotMaxTime`, `TestRestoreSnapshotFilter`, `computeMaxTime`, `createSnapshotTimeFilter`, and `clock.Now`.

Control flow: the max-time test computes expected boundary times for `yesterday`, day/month/year ago spellings, compound ago expressions, `last-month`, `last-year`, and partial absolute timestamps from year down to seconds. The filter test verifies `latest` selects index 0 and `oldest` selects the last candidate.

State/persistence behavior: no repository or filesystem mutation. Tests operate entirely on time values and filter closures.

Dependencies/integration: validates local time assumptions and supported input formats for path-based restore. Risks/test signals: tests depend on `clock.Now()` and local timezone, but compare derived values from the same clock snapshot to reduce flakiness.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_restore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server.go -->
# sources/sync-backup/kopia/cli/command_server.go

Purpose: top-level server command registrar and common server-control flag definitions.

Important APIs/types/functions: `commandServer`, `serverFlags`, `serverClientFlags`, `serverAPIClientOptions`, `apiclient.Options`, and server subcommand fields for start, ACL, user, status, refresh, flush, shutdown, snapshot/upload, cancel, pause, resume, and throttle.

Control flow: `serverFlags.setup` registers server start/listen credentials. `serverClientFlags.setup` registers address, control credentials, backwards-compatible aliases, and trusted certificate fingerprint. `commandServer.setup` registers all server subcommands. `serverAPIClientOptions` validates address and returns API client options.

State/persistence behavior: none directly; it builds command options for server start/control paths. Credentials may come from environment variables.

Dependencies/integration: central integration point for HTTP API server CLI and `internal/apiclient`. Risks/test signals: default address and default control username shape all server-control commands; missing password is allowed at option construction and handled by server authentication.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_cancel.go -->
# sources/sync-backup/kopia/cli/command_server_cancel.go

Purpose: implements `server cancel`, cancelling in-progress uploads for server-managed snapshot sources.

Important APIs/types/functions: `commandServerCancel`, embedded `commandServerSourceManagerAction`, `runServerCancelUpload`, and API endpoint `control/cancel-snapshot`.

Control flow: setup registers the command, common source/all flags, server client flags, and a server action. The run method delegates to `triggerActionOnMatchingSources` with the cancel endpoint.

State/persistence behavior: sends a control API request to the running server; any state mutation occurs server-side by cancelling source-manager work.

Dependencies/integration: depends on server API authentication, source matching, and `MultipleSourceActionResponse` handling. Risks/test signals: cancel requires either `--all` or a source path; endpoint failures are wrapped as server errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_cancel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_control_test.go -->
# sources/sync-backup/kopia/cli/command_server_control_test.go

Purpose: end-to-end tests for server control commands over HTTP and Unix domain sockets.

Important APIs/types/functions: `TestServerControl`, `TestServerControlUDS`, `hasLine`, `testutil.ServerParameters`, `RunAndProcessStderr`, server status/refresh/flush/snapshot/cancel/pause/resume/throttle/shutdown commands, and `throttling.Limits`.

Control flow: the main test creates snapshots under two repository identities, starts an insecure server on a random port, waits for managed sources to appear, checks remote source display, refreshes after an external snapshot, flushes, triggers snapshots for all and one source, checks invalid source/no-source failures, cancels, pauses/resumes, sets/gets throttle limits including JSON, shuts down, and verifies later control calls fail. The UDS test starts the server on `unix:<path>` and verifies status/shutdown.

State/persistence behavior: creates repository snapshots, starts/stops a server, mutates server throttling, and sends source-manager control actions.

Dependencies/integration: broad coverage of server API client flags, authentication, source manager, throttle endpoints, shutdown, and platform-specific Unix sockets. Risks/test signals: timing-sensitive waits use `Eventually` and startup/shutdown timeouts.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_control_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_flush.go -->
# sources/sync-backup/kopia/cli/command_server_flush.go

Purpose: implements `server flush`, asking a running Kopia server to flush in-memory state to persistent storage.

Important APIs/types/functions: `commandServerFlush`, `serverClientFlags`, `apiclient.KopiaAPIClient`, `serverapi.Empty`, and endpoint `control/flush`.

Control flow: setup registers the command, server client flags, and a server action. `run` performs a POST with empty request and response bodies to the control endpoint.

State/persistence behavior: local CLI is stateless; server-side flush may persist source manager state, caches, or other server-maintained data.

Dependencies/integration: depends on authenticated server control API. Risks/test signals: no response payload is inspected, so success is purely HTTP/API success.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_flush.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_notifications_test.go -->
# sources/sync-backup/kopia/cli/command_server_notifications_test.go

Purpose: end-to-end test that server-triggered snapshots emit configured webhook notifications and KopiaUI JSON notifications.

Important APIs/types/functions: `TestServerNotifications`, `httptest.NewServer`, `notification profile configure webhook`, `sender.Message`, `RunAndProcessStderrAsync`, and server snapshot control.

Control flow: the test starts an HTTP webhook receiver, creates a repository and snapshots under two identities, configures a webhook notification profile, starts the server with KopiaUI notifications enabled and a short shutdown grace period, triggers a server snapshot for one source, waits for an HTML webhook payload containing success CSS, and waits for a stderr JSON notification that decodes into `sender.Message`.

State/persistence behavior: configures notification profile state in the repository and starts a live server. Notification side effects are outbound HTTP POST and stderr JSON lines.

Dependencies/integration: spans notification profiles, server snapshot execution, webhook sender, UI notification output, and async server lifecycle. Risks/test signals: timing-sensitive 5-second waits; it validates success notification shape but not every notification field.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_notifications_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_pause.go -->
# sources/sync-backup/kopia/cli/command_server_pause.go

Purpose: implements `server pause`, pausing scheduled snapshots for matching server-managed sources.

Important APIs/types/functions: `commandServerPause`, embedded `commandServerSourceManagerAction`, `run`, and endpoint `control/pause-source`.

Control flow: setup registers source/all flags and server client options, then wires a server action. `run` delegates source matching and POST handling to `triggerActionOnMatchingSources`.

State/persistence behavior: local CLI is stateless; server-side source state is marked paused for matched sources.

Dependencies/integration: depends on source manager control API and path matching. Risks/test signals: source paths are normalized to absolute paths unless `--all` is used, so relative-path expectations must account for the client's cwd.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_pause.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_refresh.go -->
# sources/sync-backup/kopia/cli/command_server_refresh.go

Purpose: implements `server refresh`, asking a running server to refresh its source/cache view.

Important APIs/types/functions: `commandServerRefresh`, `serverClientFlags`, `apiclient.KopiaAPIClient`, `serverapi.Empty`, and endpoint `control/refresh`.

Control flow: setup registers server client flags and a server action. `run` posts an empty request to `control/refresh` and expects an empty response.

State/persistence behavior: local CLI is stateless; server may rescan repository manifests or source definitions and update in-memory state.

Dependencies/integration: used when snapshots are created outside the server and the server must observe them. Risks/test signals: no polling occurs here; callers/tests must wait for refreshed state to appear in `server status`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_refresh.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_resume.go -->
# sources/sync-backup/kopia/cli/command_server_resume.go

Purpose: implements `server resume` with alias `unpause`, resuming scheduled snapshots for matching sources.

Important APIs/types/functions: `commandServerResume`, embedded `commandServerSourceManagerAction`, `run`, and endpoint `control/resume-source`.

Control flow: setup registers the command alias, source/all flags, server client options, and a server action. `run` delegates to the shared source-manager action helper.

State/persistence behavior: local CLI is stateless; matched server-managed source state is resumed server-side.

Dependencies/integration: depends on server source manager and authenticated control API. Risks/test signals: shares the same source matching constraints and response logging behavior as pause/snapshot/cancel.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_resume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_shutdown.go -->
# sources/sync-backup/kopia/cli/command_server_shutdown.go

Purpose: implements `server shutdown`, requesting graceful shutdown of a running Kopia server.

Important APIs/types/functions: `commandServerShutdown`, `serverClientFlags`, `textOutput`, `apiclient.KopiaAPIClient`, `serverapi.Empty`, and endpoint `control/shutdown`.

Control flow: setup registers server client flags and output, then uses a server action. `run` posts an empty request to the shutdown endpoint.

State/persistence behavior: local CLI is stateless; server-side state transitions toward shutdown and should stop accepting later control requests.

Dependencies/integration: depends on server control API and graceful shutdown implementation in the server process. Risks/test signals: the command returns after the POST succeeds, while the server may still need time to exit; tests wait on server process completion.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_shutdown.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_snapshot.go -->
# sources/sync-backup/kopia/cli/command_server_snapshot.go

Purpose: implements `server snapshot` with alias `upload`, triggering snapshots for matching server-managed sources.

Important APIs/types/functions: `commandServerUpload`, embedded `commandServerSourceManagerAction`, `run`, and endpoint `control/trigger-snapshot`.

Control flow: setup registers command aliases, source/all flags, server client options, and a server action. `run` delegates to the shared source-manager action helper for POST construction, response handling, and success/failure logging.

State/persistence behavior: local CLI is stateless; server-side action queues or starts snapshot uploads that create repository snapshot manifests and content.

Dependencies/integration: integrates server authentication, source manager, scheduler/upload pipeline, and notification behavior. Risks/test signals: triggering all sources can start multiple uploads; command success only reflects server acceptance/response per source, not necessarily long-term repository health.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_source_manager_action.go -->
# sources/sync-backup/kopia/cli/command_server_source_manager_action.go

Purpose: shared helper for server commands that act on one source or all sources managed by the server, used by snapshot/upload, cancel, pause, and resume.

Important APIs/types/functions: `commandServerSourceManagerAction`, `setup`, `triggerActionOnMatchingSources`, `serverClientFlags`, `serverapi.MultipleSourceActionResponse`, `url.Values`, and `filepath.Abs`.

Control flow: setup registers `--all`, optional source argument, server client flags, and output. `triggerActionOnMatchingSources` rejects calls without `--all` or source, converts source to an absolute path, sends a POST to the supplied endpoint with optional `path` query parameter, and logs success or failure for each source in the response.

State/persistence behavior: local helper is stateless; all mutations happen in server-side control endpoints. It normalizes source paths before sending them.

Dependencies/integration: shared by several server control commands and therefore centralizes source matching semantics. Risks/test signals: response failures per source are logged as warnings but do not become command errors unless the API request itself fails.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_source_manager_action.go -->
