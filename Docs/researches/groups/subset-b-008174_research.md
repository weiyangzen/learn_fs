# Research Group subset-b-008174

This grouped report covers the requested MinIO mc command/configuration files. Each source file section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config-old.go -->
# sources/object-store/minio-mc/cmd/config-old.go

Purpose: Defines legacy MinIO Client configuration schemas from v1 through v9 so old JSON configs can still be represented during migration/compatibility paths. It does not perform I/O itself; it is a type catalog plus default constructors.

Important APIs/types/functions: `hostConfigV1` through `hostConfigV9`, `configV1` through `configV9`, and constructors `newConfigV*`. v7 and v8 add `loadDefaults` and `setHost`, while v9 introduces `SessionToken` and bucket `Lookup`.

Control flow: Each constructor allocates maps to avoid nil-map writes and sets the version string. v7/v8 default loaders insert known aliases only if missing, preserving user-provided entries.

State and persistence: In-memory structs mirror historic on-disk JSON layouts. Persistence is handled by newer config loaders elsewhere.

Dependencies/integration: Depends on `globalMCConfigVersion`, `defaultAccessKey`, and `defaultSecretKey` from the config package. Used by config migration code outside this subset.

Risks: Legacy field tags differ across versions, so migrations must preserve exact names. Defaults include public demo credentials and should not be treated as secure user secrets.

Test signals: No direct tests in this subset; behavior is indirectly covered by config loading/migration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config-old.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config-utils.go -->
# sources/object-store/minio-mc/cmd/config-utils.go

Purpose: Provides small validators and URL normalization helpers used by alias/config parsing and validation.

Important APIs/types/functions: `validAPIs`, `accessKeyMinLen`, `secretKeyMinLen`, `isValidAccessKey`, `isValidSecretKey`, `trimTrailingSeparator`, `isValidHostURL`, `isValidAPI`, `isValidLookup`, and `isValidPath`.

Control flow: Validation is mostly whitelist and minimum-length checks. Empty access/secret keys are allowed for anonymous endpoints. Host validation delegates parsing to `newClientURL` and accepts only `http` or `https` with root path.

State and persistence: Stateless helpers; no persistent state.

Dependencies/integration: Uses `newClientURL` and Go `slices`/`strings`. Called by config validation and alias setup flows.

Risks: Key validation checks length only, not character classes. `isValidHostURL` intentionally rejects URLs with non-root paths, which is correct for alias hosts but not general object paths.

Test signals: `config-utils_test.go` covers valid/invalid host URL, API names, and key lengths.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config-utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config-utils_test.go -->
# sources/object-store/minio-mc/cmd/config-utils_test.go

Purpose: Unit tests for basic config utility validators.

Important APIs/types/functions: `TestValidHostURL`, `TestIsValidAPI`, `TestValidSecretKeys`, `TestValidAccessKeys`, and helper `equalAssert`.

Control flow: Tests use small table-style inputs and fail on mismatches. They verify that `https://localhost:9000` is a host URL, `/` is not, mixed-case S3 API values are accepted, and key length minimums are enforced while empty keys are accepted.

State and persistence: No state or filesystem use.

Dependencies/integration: Uses Go `testing`; exercises functions from `config-utils.go`.

Risks: Coverage is narrow. It does not test `isValidLookup`, `isValidPath`, trailing separator trimming, malformed schemes, or URL path rejection.

Test signals: Positive signal for intended anonymous-key behavior and minimum-length boundaries.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config-utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config-v10.go -->
# sources/object-store/minio-mc/cmd/config-v10.go

Purpose: Defines and persists current config schema version 10 for mc aliases.

Important APIs/types/functions: `aliasConfigV10`, `configV10`, `newConfigV10`, `setAlias`, `loadDefaults`, `loadConfigV10`, and `saveConfigV10`. Globals `cacheCfgV10` and `cfgMutex` cache and synchronize config file access.

Control flow: `loadConfigV10` returns cached config when available, rejects missing config files, creates a quick config loader, loads `config.json`, caches it, and returns it. `saveConfigV10` locks for writing, updates the cache, and saves through `quick`.

State and persistence: Owns the in-memory v10 cache and writes/reads the JSON config path from `mustGetMcConfigPath`.

Dependencies/integration: Depends on `probe`, `quick`, config path helpers, and `globalMCConfigVersion`. Used by `loadMcConfigFactory` and `saveMcConfig`.

Risks: The load path takes an `RLock` while assigning `cacheCfgV10`; that relies on process ordering and could be a race under concurrent first loads. Cache invalidation only happens through `saveMcConfig`.

Test signals: Covered indirectly by config tests; no direct persistence test here.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config-v10.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config-validate.go -->
# sources/object-store/minio-mc/cmd/config-validate.go

Purpose: Validates loaded v10 configuration before use or reporting.

Important APIs/types/functions: `validateConfigVersion`, `validateConfigFile`, and `validateConfigHost`.

Control flow: Version validation compares `config.Version` to `globalMCConfigVersion`. File validation accumulates errors from the version and every alias. Host validation checks API signature and host URL through config utility helpers, returning all host-level messages.

State and persistence: Stateless. Reads only the provided `configV10` value.

Dependencies/integration: Uses `errInvalidAPISignature`, `errInvalidURL`, `isValidAPI`, and `isValidHostURL`. Integrates with config load/init paths elsewhere.

Risks: Does not validate access/secret key length, alias names, path mode, session token, license, or API key fields. It also assumes `config` is non-nil.

Test signals: No direct tests in this subset; utility validator tests cover some leaf behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config-validate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config.go -->
# sources/object-store/minio-mc/cmd/config.go

Purpose: Central config path, load/save, alias lookup, environment alias, and alias expansion logic for mc.

Important APIs/types/functions: `setMcConfigDir`, `getMcConfigDir`, `defaultMCConfigDir`, `createMcConfigDir`, `getMcConfigPath`, `newMcConfig`, `loadMcConfigFactory`, `saveMcConfig`, `isMcConfigExists`, `cleanAlias`, `isValidAlias`, `getAliasConfig`, `mustGetHostConfig`, `parseEnvURLStr`, `readAliasesFromFile`, `expandAliasFromEnv`, `expandAlias`, and `mustExpandAlias`.

Control flow: Config path resolution honors custom directory first, then home plus platform-specific default. `saveMcConfig` creates the directory, persists v10, and refreshes the cached loader closure. Alias expansion checks `MC_HOST_<alias>`, then aliases loaded from `MC_CONFIG_ENV_FILE`, then persisted config.

State and persistence: Maintains `mcCustomConfigDir`, `loadMcConfig`, and `aliasToConfigMap`. Persists `config.json` through v10 helpers and reads environment config files line by line.

Dependencies/integration: Uses `homedir`, `env`, URL parsing, alias path joining, and error helpers. It is a core dependency for client creation, encryption key validation, and command URL expansion.

Risks: `parseEnvURLStr` uses regex credential extraction to preserve special characters, but URL edge cases remain sensitive. `aliasToConfigMap` is global and unsynchronized. `mustGetHostConfig` suppresses some errors by returning nil.

Test signals: `config_test.go` covers credential and session-token parsing, including special `@`, `#`, and empty user/password cases.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config_test.go -->
# sources/object-store/minio-mc/cmd/config_test.go

Purpose: Tests environment URL parsing used for `MC_HOST_*` alias definitions.

Important APIs/types/functions: `TestParseEnvURLStr` and `TestParseEnvURLStrInvalid`.

Control flow: The main test iterates URL cases with embedded access key, secret key, optional session token, special characters, missing username, missing password, and no credentials. It asserts parsed credential fields plus hostname and port. The invalid test expects an empty string to fail.

State and persistence: No persistent state. The test only exercises parser output.

Dependencies/integration: Uses Go `testing` and `parseEnvURLStr` from `config.go`.

Risks: Does not cover paths, query strings, fragments, non-http schemes, IPv6, percent encoding, or malformed `MC_CONFIG_ENV_FILE` lines.

Test signals: Strong coverage for delimiter ambiguity in secrets and session tokens, which is a key compatibility behavior for env aliases.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cors-get.go -->
# sources/object-store/minio-mc/cmd/cors-get.go

Purpose: Implements `mc cors get` for retrieving a bucket CORS configuration.

Important APIs/types/functions: `corsGetCmd`, `checkCorsGetSyntax`, and `mainCorsGet`.

Control flow: The command requires exactly one `ALIAS/BUCKET` argument, initializes colors, creates a client with `newClient`, calls `GetBucketCors(globalContext)`, maps nil config to `not found`, and prints a shared `corsMessage`.

State and persistence: Does not persist local state. Reads remote bucket CORS configuration from object storage.

Dependencies/integration: Uses MinIO cli, console color, `newClient`, `fatalIf`, `printMsg`, and `corsMessage` from `cors-set.go`.

Risks: Only syntax validation is argument count; bucket/path validity is deferred to client creation and server response. Nil config is not treated as an error.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cors-get.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cors-main.go -->
# sources/object-store/minio-mc/cmd/cors-main.go

Purpose: Registers the top-level `mc cors` command and subcommands.

Important APIs/types/functions: `corsSubcommands`, `corsCmd`, and `mainCors`.

Control flow: The command wires `set`, `get`, and `remove` subcommands, applies `setGlobalsFromContext` and global flags, and delegates unknown invocations to `commandNotFound`.

State and persistence: No state or persistence.

Dependencies/integration: Integrates with the global CLI command tree through `github.com/minio/cli` and shared global flag handling.

Risks: Behavior is only dispatch. Missing subcommand help/usage depends on `commandNotFound` implementation outside this subset.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cors-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cors-remove.go -->
# sources/object-store/minio-mc/cmd/cors-remove.go

Purpose: Implements `mc cors remove` for deleting bucket CORS configuration.

Important APIs/types/functions: `corsRemoveCmd`, `checkCorsRemoveSyntax`, and `mainCorsRemove`.

Control flow: Requires one bucket argument, initializes a client, calls `DeleteBucketCors(globalContext)`, and prints success through `corsMessage`.

State and persistence: Mutates remote bucket configuration; no local persistence.

Dependencies/integration: Uses shared CLI/global setup, `newClient`, `fatalIf`, and `printMsg`.

Risks: Destructive operation has no confirmation flag in this file. Errors from the remote API are fatal.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cors-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cors-set.go -->
# sources/object-store/minio-mc/cmd/cors-set.go

Purpose: Implements `mc cors set` and the shared output message type for all CORS subcommands.

Important APIs/types/functions: `corsSetCmd`, `corsMessage`, `String`, `JSON`, `checkCorsSetSyntax`, and `mainCorsSet`.

Control flow: Requires `ALIAS/BUCKET CORSFILE`. The CORS file is read from a named file or stdin when `-` is used. It initializes a client and calls `SetBucketCors(globalContext, corsXML)`. `corsMessage.String` emits raw XML for get, success text for set/remove, and a not-found message for nil config.

State and persistence: Reads a local XML file/stdin and writes remote bucket CORS configuration.

Dependencies/integration: Uses `minio-go` CORS config, colorjson, console, and probe errors.

Risks: Local XML is passed to the client without pre-validation here. `String` fatals if converting returned CORS config to XML fails.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cors-set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cp-main.go -->
# sources/object-store/minio-mc/cmd/cp-main.go

Purpose: Implements `mc cp`, including flags, progress accounting, transfer scheduling, metadata/object-lock/tag/checksum setup, and move-mode hook support.

Important APIs/types/functions: `cpFlags`, `cpCmd`, `copyMessage`, `Progress`, `ProgressReader`, `doCopy`, `doCopyFake`, `printCopyURLsError`, `doCopySession`, `mainCopy`, and `doCopyOpts`.

Control flow: `mainCopy` validates syntax and encryption flags, then `doCopySession` prepares source/target URL pairs in one goroutine and schedules uploads through `newParallelManager` in another. It updates progress totals as objects are discovered, enriches `TargetContent` with storage class, retention, legal hold, tags, metadata, checksums, and multipart settings, then calls `uploadSourceToTargetURL` via `doCopy`.

State and persistence: Transfers data between local/object storage endpoints and may remove sources through `rmManager` when called for move. It does not persist local sessions in this file.

Dependencies/integration: Depends on copy URL preparation, encryption methods, progress bar/accounter, object lock checks, MinIO checksum types, upload helpers, and global cancellation.

Risks: `totalObjects`/`totalBytes` are shared between goroutines without synchronization. Error handling must coordinate channel closure, progress rollback, ignored errors, and cancellation. Metadata parsing error is discarded in the scheduling path after prior syntax validation assumptions.

Test signals: `cp-main_test.go` covers metadata parsing helper, not the transfer scheduler.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cp-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cp-main_contrib.go -->
# sources/object-store/minio-mc/cmd/cp-main_contrib.go

Purpose: Parses `mc cp --attr` custom metadata strings into canonical HTTP metadata keys and values.

Important APIs/types/functions: `getMetaDataEntry` and `ErrInvalidMetadata` from `cp-main.go`.

Control flow: A small rune parser alternates between key and value tokens, with normal, single-quoted, and double-quoted states. Unquoted `=` separates key/value, unquoted `;` separates entries, and delimiters inside quotes are preserved. EOF validates that the parser is in value state and not inside a quote, then emits the final entry.

State and persistence: Stateless parsing only.

Dependencies/integration: Uses `http.CanonicalHeaderKey` and probe errors. Called by copy transfer setup to populate `TargetContent.UserMetadata`.

Risks: Empty keys/values are not deeply validated beyond parser state. Parser panics on impossible internal states. Quoting support is custom and must remain compatible with shell quoting expectations.

Test signals: `cp-main_test.go` covers multiple delimiters, repeated `=`, quoted semicolons, quoted keys, and unterminated quotes.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cp-main_contrib.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cp-main_test.go -->
# sources/object-store/minio-mc/cmd/cp-main_test.go

Purpose: Unit tests for copy metadata parsing.

Important APIs/types/functions: `TestParseMetaData`.

Control flow: Table cases call `getMetaDataEntry`, then compare returned maps and error causes. Success cases cover semicolon-separated entries, values containing `=`, `Cache-Control`, quoted values with embedded semicolons/quotes, and quoted keys. Failure cases cover missing `=`, wrong delimiter, and unterminated quote states.

State and persistence: No I/O or persistent state.

Dependencies/integration: Uses `reflect.DeepEqual` and Go `testing`.

Risks: Does not test empty key names, duplicate keys, whitespace trimming, Unicode, or integration with actual `mc cp --attr`.

Test signals: Good focused regression coverage for the custom state-machine parser.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cp-main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cp-url-syntax.go -->
# sources/object-store/minio-mc/cmd/cp-url-syntax.go

Purpose: Validates command-line syntax for `mc cp` before transfers are prepared.

Important APIs/types/functions: `checkCopySyntax`.

Control flow: Requires at least two arguments, parses checksum flags, splits sources and target, rejects `--version-id` with multiple sources, rejects `--zip` with `--rewind`, ensures object-storage targets include a bucket, requires retention mode and duration to be paired, and rejects `--preserve` on Windows.

State and persistence: Stateless validation.

Dependencies/integration: Uses `newClientURL`, retention flag constants, `parseChecksum`, and fatal error helpers. Called by `mainCopy`.

Risks: Some validation is platform-specific and uses fatal exits, making it harder to unit test. Deeper source/target type validation happens later in URL preparation.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cp-url-syntax.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cp-url.go -->
# sources/object-store/minio-mc/cmd/cp-url.go

Purpose: Converts `mc cp` source/target arguments into concrete one-to-one copy jobs.

Important APIs/types/functions: `copyURLsType`, `guessCopyURLType`, `prepareCopyURLsTypeA/B/C/D`, `makeCopyContentTypeA/B/C`, `prepareCopyURLsOpts`, `copyURLsContent`, and `prepareCopyURLs`.

Control flow: The code classifies copy forms: file-to-file, file-to-directory, recursive directory-to-directory, and multi-source-to-directory. It stats sources/targets, verifies directory requirements, prevents copying a directory into itself, recursively lists source contents, constructs target paths, de-duplicates multi-source targets, and applies older/newer time filters.

State and persistence: No persistence; creates streams of `URLs` describing later transfer work.

Dependencies/integration: Depends on `newClient`, `url2Stat`, `firstURL2Stat`, `isAliasURLDir`, `Client.List`, `urlJoinPath`, and time filter helpers.

Risks: Correctness depends on sorted/listing semantics and path separator handling across filesystem and object storage. Recursive copy behavior is sensitive to trailing separators and source prefix trimming.

Test signals: No direct tests in this subset; copy behavior likely covered by integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/cp-url.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/diff-main.go -->
# sources/object-store/minio-mc/cmd/diff-main.go

Purpose: Implements `mc diff`, a directory/bucket comparison command.

Important APIs/types/functions: `diffCmd`, `diffMessage`, `String`, `JSON`, `checkDiffSyntax`, `doDiffMain`, and `mainDiff`.

Control flow: `mainDiff` parses encryption flags, validates two directory-like arguments, sets output colors, and calls `doDiffMain`. `doDiffMain` normalizes trailing separators, expands aliases, builds clients, then prints messages from `bucketObjectDifference`.

State and persistence: Read-only against source and target listings; no local persistence.

Dependencies/integration: Uses encryption key parsing, `url2Stat`, `newClientFromAlias`, `bucketObjectDifference`, global context, and console/json output.

Risks: The command compares names, size, type, and certain metadata, not object bytes. Missing destination can be accepted during syntax validation only for specific object-missing errors.

Test signals: No direct command tests; `difference_test.go` covers an exclude helper used by related comparison/mirror code.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/diff-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/difference.go -->
# sources/object-store/minio-mc/cmd/difference.go

Purpose: Core differ engine for comparing sorted source and target object/bucket streams.

Important APIs/types/functions: `differType`, `getSourceModTimeKey`, `activeActiveModTimeUpdated`, `metadataEqual`, `bucketObjectDifference`, `objectDifference`, `bucketDifference`, `differenceInternal`, and `difference`.

Control flow: `differenceInternal` merges two sorted channels, emits only-in-first/second messages, normalizes UTF-8/NFC path suffixes, compares object type, size, active-active source modtime metadata, and optionally metadata maps. It stops early for source-listing-only mode and propagates stream errors.

State and persistence: Stateless stream processing. Uses buffered output channel.

Dependencies/integration: Consumes `ClientContent` listings from `Client` implementations and `mirrorOptions`. Handles MinIO and filesystem error classes.

Risks: Requires both streams to be sorted consistently by normalized suffix. In the type-diff branch, the loop continues without advancing channels, which is a potential infinite loop if reached. Metadata comparison uses `&&` between user metadata and system metadata inequality, so a difference in only one map may be missed.

Test signals: No direct tests for `differenceInternal`; this is a high-risk area for focused regression tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/difference.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/difference_test.go -->
# sources/object-store/minio-mc/cmd/difference_test.go

Purpose: Tests exclude-pattern matching behavior used by difference/mirror style workflows.

Important APIs/types/functions: `testCases` and `TestExcludeOptions`.

Control flow: The table enumerates object storage and filesystem path suffixes, patterns, and expected booleans, then calls `matchExcludeOptions`.

State and persistence: No state or I/O.

Dependencies/integration: Depends on `matchExcludeOptions` and `ClientURLType` definitions outside this subset.

Risks: Despite the filename, it does not test the core `difference` merge/comparison logic, active-active modtime handling, metadata equality, error propagation, or Unicode normalization.

Test signals: Useful narrow signal for exclude pattern matching across object-storage and filesystem path styles.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/difference_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/du-main.go -->
# sources/object-store/minio-mc/cmd/du-main.go

Purpose: Implements `mc du`, summarizing object counts and sizes for folders/prefixes.

Important APIs/types/functions: `duFlags`, `duCmd`, `duMessage`, `du`, and `mainDu`.

Control flow: `mainDu` validates arguments, sets depth based on `--depth` and `--recursive`, parses rewind/version flags, verifies each target is a directory, and calls recursive `du`. `du` expands aliases, creates a client, lists with optional versions/time reference, recursively descends into subdirectories when depth allows, skips delete markers/directories, and prints totals.

State and persistence: Read-only listing. No local persistence.

Dependencies/integration: Uses `newClientFromAlias`, `Client.List`, `parseRewindFlag`, `isAliasURLDir`, `humanize`, and console/json output.

Risks: Recursive calls can be expensive for deep trees. Some filesystem errors are skipped while others abort. Prefix handling depends on path cleaning and URL parsing.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/du-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/duration.go -->
# sources/object-store/minio-mc/cmd/duration.go

Purpose: Extends Go duration parsing with days, weeks, and years for mc time filters.

Important APIs/types/functions: `Duration`, `Days`, unit constants, `leadingInt`, `unitMap`, and `ParseDuration`.

Control flow: `ParseDuration` mirrors Go's duration parser: optional sign, repeated numeric/fractional unit chunks, overflow checks, unit lookup, fractional scaling, and final sign application. It rejects empty, missing-unit, unknown-unit, and overflow inputs.

State and persistence: Stateless.

Dependencies/integration: Used by age/rewind-related helpers elsewhere for flags such as `--older-than`, `--newer-than`, and retention duration parsing.

Risks: Month/year-related constants are approximations, though only `y` appears in `unitMap`. `Duration.Days` appears to return hours plus fractional days due to dividing the remainder by day but not the main hour count by 24, which may be unintended.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/duration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/encrypt-clear.go -->
# sources/object-store/minio-mc/cmd/encrypt-clear.go

Purpose: Implements `mc encrypt clear` to remove bucket auto-encryption configuration.

Important APIs/types/functions: `encryptClearCmd`, `checkEncryptClearSyntax`, `encryptClearMessage`, and `mainEncryptClear`.

Control flow: Requires one target, creates a cancellable context, initializes a client, calls `DeleteEncryption`, and prints a success message.

State and persistence: Mutates remote bucket encryption configuration; no local persistence.

Dependencies/integration: Uses global context, `newClient`, client encryption API, colorjson/console, and fatal error handling.

Risks: Destructive operation has no local confirmation. All validation beyond argument count is delegated to client/server.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/encrypt-clear.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/encrypt-info.go -->
# sources/object-store/minio-mc/cmd/encrypt-info.go

Purpose: Implements `mc encrypt info` to display bucket auto-encryption status.

Important APIs/types/functions: `encryptInfoCmd`, `checkEncryptInfoSyntax`, `encryptInfoMessage`, and `mainEncryptInfo`.

Control flow: Requires one target, creates a client, calls `GetEncryption`, maps algorithm/key ID into output, and prints human or JSON output. String output distinguishes disabled, SSE-S3, and SSE-KMS with key ID.

State and persistence: Read-only against remote bucket encryption config.

Dependencies/integration: Uses client encryption API, global context, console/color, and colorjson.

Risks: String output assumes non-empty algorithm without key ID means SSE-S3, so future algorithms could be misreported.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/encrypt-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/encrypt-main.go -->
# sources/object-store/minio-mc/cmd/encrypt-main.go

Purpose: Registers the top-level `mc encrypt` command and its subcommands.

Important APIs/types/functions: `encryptSubcommands`, `encryptCmd`, and `mainEncrypt`.

Control flow: Wires `set`, `clear`, and `info` subcommands, applies global flags and setup, and routes missing/unknown subcommands through `commandNotFound`.

State and persistence: No direct state.

Dependencies/integration: Uses MinIO cli and shared command setup.

Risks: Dispatch-only file; behavior depends on subcommands and CLI framework.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/encrypt-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/encrypt-set.go -->
# sources/object-store/minio-mc/cmd/encrypt-set.go

Purpose: Implements `mc encrypt set` to enable bucket auto-encryption.

Important APIs/types/functions: `encryptSetCmd`, `checkEncryptSetSyntax`, `encryptSetMessage`, and `mainEncryptSet`.

Control flow: Accepts either `sse-s3 TARGET` or `sse-kms KEY TARGET`, lowercases the algorithm, validates it is `sse-s3` or `sse-kms`, creates a client, calls `SetEncryption`, and prints success.

State and persistence: Mutates remote bucket encryption configuration.

Dependencies/integration: Uses global context, `newClient`, client encryption API, probe errors, and console/json output.

Risks: Does not require a key ID for `sse-kms` in this file despite examples implying one. Does not reject a key ID for `sse-s3` if three args are supplied.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/encrypt-set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/encryption-methods.go -->
# sources/object-store/minio-mc/cmd/encryption-methods.go

Purpose: Parses and validates command-line server-side encryption options for object operations.

Important APIs/types/functions: `sseKeyType`, `prefixSSEPair`, `byPrefixLength`, `getSSE`, `validateAndCreateEncryptionKeys`, `validateAndParseKey`, `validateOverLappingSSEKeys`, `splitKey`, `parseSSEKey`, and `validKMSKeyName`.

Control flow: CLI string slices are parsed for KMS, S3, and SSE-C. Each key is split at the last `=`, validated, converted to a minio-go `encrypt.ServerSide`, checked for matching command args and configured aliases, checked for overlapping prefixes, then sorted by longest prefix for lookup.

State and persistence: Builds per-command in-memory maps from alias to prefix/SSE pairs. No persistence.

Dependencies/integration: Uses `mustGetHostConfig`, minio-go encryption constructors, global CLI args, and SSE-specific error helpers.

Risks: Alias existence is checked via config/env and can be nil if config is unavailable. Prefix matching uses simple `strings.HasPrefix`, so ambiguous path boundaries must be controlled by overlap validation. KMS key-name validation is intentionally restrictive.

Test signals: `encryption-methods_test.go` exercises parsing for SSE-C base64/hex, unusual prefixes, invalid keys, KMS names, and SSE-S3.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/encryption-methods.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/encryption-methods_test.go -->
# sources/object-store/minio-mc/cmd/encryption-methods_test.go

Purpose: Unit tests for encryption key string parsing.

Important APIs/types/functions: `TestParseEncryptionKeys`.

Control flow: A table feeds `parseSSEKey` with SSE-C, KMS, and S3 formats. Success cases assert alias/prefix/object reconstruction and decoded plaintext key. Failure cases cover invalid base64/hex, wrong lengths, spaces/symbols, and invalid KMS names.

State and persistence: No state or I/O.

Dependencies/integration: Uses Go `testing` and `fmt`.

Risks: Does not test `validateAndCreateEncryptionKeys`, alias existence, prefix overlap, sorting, or CLI argument matching.

Test signals: Strong focused coverage for the parser's last-`=` split behavior and 32-byte SSE-C key requirement.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/encryption-methods_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/error.go -->
# sources/object-store/minio-mc/cmd/error.go

Purpose: Central fatal/nonfatal error reporting, exit-status wrapping, and deprecated flag/command messaging.

Important APIs/types/functions: `causeMessage`, `errorMessage`, `fatalIf`, `fatal`, `exitStatus`, `errorIf`, `deprecatedError`, `deprecatedFlagError`, and `deprecatedFlagsWarning`.

Control flow: Fatal and nonfatal paths produce structured JSON when `globalJSON` is set, optionally adding call traces/sysinfo under `globalDebug`. Human output trims and punctuates messages, replaces details with context-canceled text when appropriate, and calls console fatal/error functions.

State and persistence: Reads global output/debug/cancellation state. No persistence.

Dependencies/integration: Used broadly across commands. Depends on `probe.Error`, `console`, `cli.ExitCoder`, and global context flags.

Risks: Fatal exits make unit tests harder. Formatting logic changes user-visible messages. `deprecatedFlagsWarning` scans args only, not normalized CLI flags.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/event-add.go -->
# sources/object-store/minio-mc/cmd/event-add.go

Purpose: Implements `mc event add` to add bucket notification targets.

Important APIs/types/functions: `eventAddFlags`, `eventAddCmd`, `checkEventAddSyntax`, `eventAddMessage`, and `mainEventAdd`.

Control flow: Requires target and ARN, parses event list plus prefix/suffix and ignore-existing flag, creates a client, requires it to be `S3Client`, calls `AddNotificationConfig`, and prints success.

State and persistence: Mutates remote bucket notification configuration.

Dependencies/integration: Uses S3-specific notification methods, CLI flags, global context, colorjson, and console output.

Risks: Event string is split without trimming/validation here. Non-S3 targets are rejected at runtime.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/event-add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/event-list.go -->
# sources/object-store/minio-mc/cmd/event-list.go

Purpose: Implements `mc event list`/`ls` for bucket notifications.

Important APIs/types/functions: `eventListCmd`, `checkEventListSyntax`, `eventListMessage`, and `mainEventList`.

Control flow: Accepts target plus optional ARN, creates an S3 client, calls `ListNotificationConfigs`, and prints each returned config with events and filters.

State and persistence: Read-only against remote notification config.

Dependencies/integration: Uses S3 notification client methods, colorjson, console colors, and global context.

Risks: Usage text says `TARGET ARN` even though ARN is optional. String output always prints `Filter:` even when no filter is present.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/event-list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/event-main.go -->
# sources/object-store/minio-mc/cmd/event-main.go

Purpose: Registers the top-level `mc event` command and subcommands.

Important APIs/types/functions: `eventFlags`, `eventSubcommands`, `eventCmd`, and `mainEvent`.

Control flow: Wires `add`, `remove`, and `list`, applies global flags, hides help command, and handles missing subcommands through `commandNotFound`.

State and persistence: None directly.

Dependencies/integration: MinIO cli command tree and global setup.

Risks: Dispatch-only; all behavior resides in subcommands.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/event-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/event-remove.go -->
# sources/object-store/minio-mc/cmd/event-remove.go

Purpose: Implements `mc event remove`/`rm` for deleting bucket notification configs.

Important APIs/types/functions: `eventRemoveFlags`, `eventRemoveCmd`, `checkEventRemoveSyntax`, `eventRemoveMessage`, and `mainEventRemove`.

Control flow: Requires target and optional ARN. If only target is supplied, `--force` is mandatory. It creates an S3 client, reads event/prefix/suffix filters, calls `RemoveNotificationConfig`, and prints success.

State and persistence: Mutates remote bucket notification configuration.

Dependencies/integration: Uses S3-specific notification APIs, global context, probe errors, and output helpers.

Risks: The `--force` guard protects remove-all behavior, but filtered removal with empty ARN depends on server method semantics. Event string is not split here, unlike add.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/event-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/find-main.go -->
# sources/object-store/minio-mc/cmd/find-main.go

Purpose: Defines `mc find` CLI flags, validates targets, parses typed options, and constructs `findContext`.

Important APIs/types/functions: `findFlags`, `findCmd`, `checkFindSyntax`, `findContext`, and `mainFind`.

Control flow: Validation defaults no args to `./`, normalizes `.`, rejects empty args, stats inputs, and allows alias-only object storage except in watch mode. `mainFind` parses encryption, size thresholds, versions, alias expansion, regex, metadata/tag regex maps, and delegates to `doFind`.

State and persistence: Builds in-memory search context only.

Dependencies/integration: Uses client stat/init, `humanize.ParseBytes`, `validateAndCreateEncryptionKeys`, alias expansion, and find execution helpers.

Risks: `regexp.MustCompile` on `--regex` panics on invalid regex instead of returning a controlled fatal error. Only the first target is used to construct the client/context.

Test signals: `find_test.go` covers downstream matching and substitutions, not CLI parsing.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/find-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/find.go -->
# sources/object-store/minio-mc/cmd/find.go

Purpose: Implements matching, listing, watch mode, formatting, external execution, presigned URL substitution, and metadata/tag regex filters for `mc find`.

Important APIs/types/functions: `findMessage`, `nameMatch`, `patternMatch`, `pathMatch`, `getExitStatus`, `execFind`, `watchFind`, `trimSuffixAtMaxDepth`, `getAliasedPath`, `find`, `doFind`, `stringsReplace`, `matchFind`, `getShareURL`, `getRegexMap`, `matchRegexMaps`, and `matchMetadataRegexMaps`.

Control flow: `doFind` recursively lists content, skips selected listing errors and Glacier objects, converts `ClientContent` to `contentMessage`, filters through `matchFind`, then either runs `--exec`, applies `--print`, or prints the path. Watch mode is deferred and consumes put events until cancellation.

State and persistence: Read-only listing/watch except `--exec`, which can run arbitrary user commands. Generates presigned URLs when `{url}` is requested.

Dependencies/integration: Uses `Client.List`, `Client.Watch`, share URL APIs, shlex, wildcard matching, regex, normalization, console, and global context.

Risks: `--exec` exits the whole process on command failure and executes user-provided programs. `doFind` lists with `globalContext` instead of the passed context. Regex map keys are exact/canonicalized only for metadata.

Test signals: `find_test.go` covers matching predicates, max depth trimming, substitution, and exit status extraction.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/find.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/find_test.go -->
# sources/object-store/minio-mc/cmd/find_test.go

Purpose: Unit tests for `mc find` matching, path trimming, format substitution, and command exit status handling.

Important APIs/types/functions: `TestMatchFind`, `TestSuffixTrimmingAtMaxDepth`, `TestFindMatch`, `TestStringReplace`, and `TestGetExitStatus`.

Control flow: Tests create lightweight `findContext` values with S3 client stubs, verify ignore/name/path/regex/time/size matching, exercise max-depth truncation, validate wildcard name/path behavior, assert substitution tokens such as `{base}`, `{dir}`, `{size}`, and `{time}`, and check Linux exit statuses.

State and persistence: Spawns local commands in `TestGetExitStatus`; otherwise no persistence.

Dependencies/integration: Uses Go testing, regexp, exec, runtime guards, and time.

Risks: Linux-only exit-status test is skipped elsewhere. No tests for watch mode, metadata/tag regex maps, `{url}`, or `--exec` substitutions with shlex.

Test signals: Good coverage of the most error-prone pure functions in `find.go`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/find_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/flags.go -->
# sources/object-store/minio-mc/cmd/flags.go

Purpose: Defines global CLI flags, encryption flag bundles, checksum flag, and checksum parsing.

Important APIs/types/functions: `envPrefix`, `globalFlags`, `encFlags`, `encCFlag`, `encKSMFlag`, `encS3Flag`, `checksumFlag`, and `parseChecksum`.

Control flow: Flags map command-line/environment values into global config. `parseChecksum` recognizes CRC32, CRC32C, full-object variants, SHA1, SHA256, CRC64NVME, and MD5, enables trailing headers for supported checksum types, and rejects MD5 combined with trailing-header checksums.

State and persistence: Defines CLI metadata only. `parseChecksum` mutates the package-level `useTrailingHeaders` atomic/value defined elsewhere.

Dependencies/integration: Used by most commands through `globalFlags` and by copy through `checksumFlag`.

Risks: Hidden `md5` flag is still active. Checksum aliases and error text must stay aligned with minio-go behavior.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/fs-pathutils_nix.go -->
# sources/object-store/minio-mc/cmd/fs-pathutils_nix.go

Purpose: Non-Windows implementation of filesystem path normalization.

Important APIs/types/functions: `normalizePath`.

Control flow: Returns the path unchanged on builds where `!windows` is true.

State and persistence: Stateless.

Dependencies/integration: Selected by Go build tags. Used wherever path normalization abstracts platform differences.

Risks: None significant in this file; behavior intentionally defers to native POSIX-like paths.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/fs-pathutils_nix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/fs-pathutils_windows.go -->
# sources/object-store/minio-mc/cmd/fs-pathutils_windows.go

Purpose: Windows-specific filesystem path normalization for root-relative paths.

Important APIs/types/functions: `normalizePath`.

Control flow: If the path has no volume name and starts with `\`, it calls `syscall.FullPath` to expand it. Other paths are returned unchanged. Errors panic.

State and persistence: Stateless, no persistence.

Dependencies/integration: Selected by the `windows` build tag. Uses `filepath.VolumeName`, `strings.HasPrefix`, and `syscall.FullPath`.

Risks: Panics on `FullPath` errors instead of returning an error. Root-relative path semantics depend on Windows current drive.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/fs-pathutils_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/get-main.go -->
# sources/object-store/minio-mc/cmd/get-main.go

Purpose: Implements `mc get`, a restricted S3-object-to-local download command.

Important APIs/types/functions: `getFlags`, `getCmd`, `mainGet`, and `printGetURLsError`.

Control flow: Requires `SOURCE TARGET`, parses encryption keys, prepares get URLs through `prepareGetURLs`, then calls shared `doCopy` for each result with progress accounting. It reports URL preparation/download errors and final progress.

State and persistence: Downloads remote S3 object data to local filesystem target.

Dependencies/integration: Reuses copy transfer machinery, encryption parsing, progress bar/accounter, and global context.

Risks: Only one source is supported by get URL type guessing. Some total byte progress is not accumulated in `mainGet` before calling `doCopy`, relying on transfer update behavior.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/get-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/get-url.go -->
# sources/object-store/minio-mc/cmd/get-url.go

Purpose: Prepares URL pairs for `mc get`.

Important APIs/types/functions: `prepareGetURLs` and `guessGetURLType`.

Control flow: `guessGetURLType` requires exactly one source, verifies the source client is `S3Client`, requires bucket and object path, creates source content from object info and optional version ID, verifies the target is an `fsClient`, then classifies target as file-to-file or file-to-directory. `prepareGetURLs` delegates to copy type A/B preparation.

State and persistence: Stateless preparation; no actual download here.

Dependencies/integration: Reuses copy URL structs and helpers, `newClient`, `S3Client`, `fsClient`, and minio object info.

Risks: Error strings are plain `fmt.Errorf` wrapped by probe in some cases. It constructs source content without an initial stat/read, so missing remote objects surface later.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/get-url.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/globals.go -->
# sources/object-store/minio-mc/cmd/globals.go

Purpose: Defines process-wide constants, global runtime settings, root context, terminal/pager state, and global flag application.

Important APIs/types/functions: config/session constants, global booleans/rates/context variables, `parsePagerDisableFlag`, and `setGlobalsFromContext`.

Control flow: `setGlobalsFromContext` merges local and global CLI flags, turns off color for no-color/quiet/json-line output, parses connection deadlines, upload/download limits, DNS resolve overrides, and custom HTTP headers with validation.

State and persistence: Mutates package-level globals used by clients, output, network transport, and cancellation. No persistence to disk.

Dependencies/integration: Used by nearly every command through `Before: setGlobalsFromContext`. Depends on console/lipgloss, humanize, netip, HTTP header validation, and madmin types.

Risks: Global mutable state can leak between tests and commands in the same process. Accumulative `globalQuiet = globalQuiet || quiet` style means flags only turn on, not off.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/globals.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/head-main.go -->
# sources/object-store/minio-mc/cmd/head-main.go

Purpose: Implements `mc head`, printing the first N lines of local/stdin/object content with optional decompression and version/rewind support.

Important APIs/types/functions: `headFlags`, `headCmd`, `headURL`, `headOut`, `parseHeadSyntax`, and `mainHead`.

Control flow: `mainHead` parses encryption and syntax, reads stdin when no args are supplied, otherwise calls `headURL` for each target. `headURL` obtains a stream and metadata, wraps gzip/bzip2 readers based on content type, and delegates to `headOut`. `headOut` uses a buffered reader and writes line by line to pretty stdout if terminal.

State and persistence: Read-only streams; writes to stdout.

Dependencies/integration: Uses `getSourceStreamMetadataFromURL`, encryption flags, rewind parsing, terminal detection, and pretty stdout.

Risks: Compression detection relies on `Content-Type`, not file extension or content encoding. `headURL` uses `context.Background()` rather than the command/global context.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/head-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/health.go -->
# sources/object-store/minio-mc/cmd/health.go

Purpose: Defines common interfaces and header structs for subnet health report output.

Important APIs/types/functions: `HealthReportInfo`, `HealthReportHeader`, `Health`, and `SchemaVersion`.

Control flow: No executable logic. The interface requires timestamp/status/error accessors plus the shared `message` interface for printable output.

State and persistence: Data structures only.

Dependencies/integration: Used by versioned health report implementations such as `ClusterHealthV1`.

Risks: Minimal; schema stability matters for consumers expecting `{"subnet":{"health":{"version":"v1"}}}` style headers.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/health.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/health_v1.go -->
# sources/object-store/minio-mc/cmd/health_v1.go

Purpose: Maps `madmin.HealthInfoV0` into mc's v1 cluster health report schema.

Important APIs/types/functions: hardware/software structs, `ClusterHealthV1`, `String`, `JSON`, getters, `MapHealthInfoToV1`, `parallelize`, `addKeysToSet`, and map helpers for CPU, drives, memory, network, and drive performance.

Control flow: `MapHealthInfoToV1` returns error status when input error is non-nil. Otherwise it maps subsystem data in parallel, builds a server address set from all maps, merges hardware per server, and copies MinIO software/config/process/OS fields.

State and persistence: Pure data transformation; no persistence.

Dependencies/integration: Uses `madmin-go`, `gopsutil`, MinIO set, reflect map keys, and JSON output.

Risks: Iterating a set/map produces nondeterministic server order. `parallelize` defers `Wait`, which works but is unusual. Missing data yields zero-value nested structs.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/health_v1.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/humanized-duration.go -->
# sources/object-store/minio-mc/cmd/humanized-duration.go

Purpose: Converts `time.Duration` values into compact human-readable duration components and strings.

Important APIs/types/functions: `humanizedDuration`, `StringShort`, `String`, and `timeDurationToHumanizedDuration`.

Control flow: Conversion chooses milliseconds, seconds, minutes, hours, or days based on duration magnitude and fills remainder fields using `math.Mod`. String methods format short or full strings from populated fields.

State and persistence: Stateless.

Dependencies/integration: Used by status/progress/reporting code elsewhere that needs user-friendly elapsed time.

Risks: Does not handle negative durations specially. Pluralization is not grammatically adjusted for singular units. Milliseconds under one second are truncated.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/humanized-duration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-create-with-login.go -->
# sources/object-store/minio-mc/cmd/idp-ldap-accesskey-create-with-login.go

Purpose: Implements LDAP access-key creation by interactively logging in with LDAP credentials and then creating a service account.

Important APIs/types/functions: `idpLdapAccesskeyCreateWithLoginFlags`, `idpLdapAccesskeyCreateWithLoginCmd`, `mainIDPLdapAccesskeyCreateWithLogin`, and `loginLDAPAccesskey`.

Control flow: The command requires a URL and interactive stdin. It prompts for missing LDAP username/password, creates LDAP STS credentials, fetches temporary credentials, initializes an admin client, builds service-account options with target user set to the temporary access key ID, calls `AddServiceAccountLDAP`, and prints generated credentials.

State and persistence: Reads credentials from flags/stdin and creates remote service-account credentials. No local persistence.

Dependencies/integration: Uses terminal password reading, minio-go LDAP identity credentials, madmin admin client, and shared create flags/options.

Risks: Interactive-only guard rejects non-terminal stdin. Password can still be supplied via CLI flag, which may expose it in shell history/process lists.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-create-with-login.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-create.go -->
# sources/object-store/minio-mc/cmd/idp-ldap-accesskey-create.go

Purpose: Implements LDAP service-account access-key creation and shared create option assembly.

Important APIs/types/functions: `idpLdapAccesskeyCreateFlags`, `idpLdapAccesskeyCreateCmd`, `mainIDPLdapAccesskeyCreate`, `commonAccesskeyCreate`, and `accessKeyCreateOpts`.

Control flow: Requires target and optional target user. It rejects deprecated `--login`, generates missing access/secret keys, validates mutually exclusive `--expiry` and `--expiry-duration`, optionally reads and validates a non-empty policy file, parses expiration by supported local time formats or duration, calls LDAP or generic admin service-account creation, and prints credentials.

State and persistence: Reads optional policy file and creates remote service account credentials.

Dependencies/integration: Uses `newAdminClient`, `madmin.AddServiceAccountReq`, credential generation, policy parser, supported time formats, and shared `accesskeyMessage`.

Risks: Generated secret is printed to output; callers must protect logs. Expiry parsing depends on local timezone. Policy validation happens client-side but enforcement is server-side.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-disable.go -->
# sources/object-store/minio-mc/cmd/idp-ldap-accesskey-disable.go

Purpose: Registers `mc idp ldap accesskey disable`.

Important APIs/types/functions: `idpLdapAccesskeyDisableCmd` and `mainIDPLdapAccesskeyDisable`.

Control flow: The command delegates to `enableDisableAccesskey(ctx, false)`.

State and persistence: Mutates remote service-account status through shared enable/disable code.

Dependencies/integration: Uses global flags and shared LDAP access-key command helpers.

Risks: Validation and error messages are entirely in the shared helper. Usage says `[TARGET]` although implementation expects target plus access key.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-disable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-edit.go -->
# sources/object-store/minio-mc/cmd/idp-ldap-accesskey-edit.go

Purpose: Implements editing properties of existing LDAP access keys/service accounts.

Important APIs/types/functions: `idpLdapAccesskeyEditFlags`, `idpLdapAccesskeyEditCmd`, `mainIDPLdapAccesskeyEdit`, `commonAccesskeyEdit`, and `accessKeyEditOpts`.

Control flow: Requires target and access key, builds update options, initializes admin client, calls `UpdateServiceAccount`, and prints success. Option parsing requires at least one editable property, rejects both expiry forms together, validates optional non-empty policy file, and parses absolute or duration expiry.

State and persistence: Reads optional policy file and mutates remote service-account metadata/secret/policy/expiration.

Dependencies/integration: Uses `madmin.UpdateServiceAccountReq`, policy parser, supported time formats, and shared output message.

Risks: Argument check allows one arg even though `accessKey` is then empty, likely causing server-side failure instead of local syntax help. Example contains `---expiry-duration` typo.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-edit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-enable.go -->
# sources/object-store/minio-mc/cmd/idp-ldap-accesskey-enable.go

Purpose: Implements enabling and shared enable/disable status changes for LDAP access keys.

Important APIs/types/functions: `idpLdapAccesskeyEnableCmd`, `mainIDPLdapAccesskeyEnable`, and `enableDisableAccesskey`.

Control flow: The helper accepts target and access key, initializes admin client, chooses operation/status (`on` for enable, `off` for disable), calls `UpdateServiceAccount` with `NewStatus`, and prints success.

State and persistence: Mutates remote service-account status.

Dependencies/integration: Used by both enable and disable command files. Depends on `newAdminClient`, `madmin.UpdateServiceAccountReq`, and `accesskeyMessage`.

Risks: Syntax check allows a single arg and leaves access key empty. Fatal message says "Unable to add service account" during status update, which is misleading.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-enable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-info.go -->
# sources/object-store/minio-mc/cmd/idp-ldap-accesskey-info.go

Purpose: Registers LDAP access-key info command and LDAP-specific string rendering for username.

Important APIs/types/functions: `idpLdapAccesskeyInfoCmd`, `ldapAccessKeyInfo`, `String`, and `mainIDPLdapAccesskeyInfo`.

Control flow: The command delegates to shared `commonAccesskeyInfo`. `ldapAccessKeyInfo.String` renders a green "Username:" label and username via lipgloss.

State and persistence: Read-only remote info through shared helper; no local persistence here.

Dependencies/integration: Uses global flags, shared access-key info implementation, and lipgloss for human output.

Risks: Most behavior is outside this file. Output styling is separate from JSON behavior defined elsewhere.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-info.go -->
