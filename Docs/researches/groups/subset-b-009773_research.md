# Research: subset-b-009773

Grouped research for rclone config, filter, fs feature, error, and HTTP helper files. Each source-tree-aligned section is wrapped for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/crypt_test.go -->
# sources/user-network-fs/rclone/fs/config/crypt_test.go

## Purpose
External-package tests for encrypted rclone config loading and password-command integration. The file validates the public `config` package behavior against encrypted and malformed fixture files rather than private crypt helpers.

## Important APIs, Types, And Control Flow
Tests exercise `config.SetConfigPath`, `SetConfigPassword`, `IsEncrypted`, `Data().Load`, `ClearConfigPassword`, and `GetPasswordCommand`. The password-command cases mutate `fs.ConfigInfo.PasswordCommand` via context config, then load `testdata/encrypted.conf` with correct and incorrect command output. Failure tests rotate through short, invalid-base64, too-new, and missing config paths.

## State And Persistence
The tests temporarily replace the global config path and global config info, clear the in-memory config password, and restore both in defers. One case writes a temporary Go program to verify that `RCLONE_PASSWORD_CHANGE` is not leaked to direct password-command execution.

## Dependencies And Integration Points
Depends on `fs.GetConfig`, the configfile-backed storage installed elsewhere, encrypted fixture files, `go run` for the environment probe, and testify assertions. It integrates encryption handling with the user-visible config loader.

## Risks And Test Signals
The tests guard wrong passwords, unsupported encryption versions, short payloads, invalid base64, and missing files. Residual risk is that fixture passwords and encrypted blob format are fixed examples, so they do not fuzz all corrupt ciphertext or key-derivation paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/crypt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/default_storage.go -->
# sources/user-network-fs/rclone/fs/config/default_storage.go

## Purpose
Provides `defaultStorage`, an in-memory implementation of the config `Storage` interface used when configuration is not backed by an on-disk config file or when tests need ephemeral storage.

## Important APIs, Types, And Control Flow
`defaultStorage` is a mutex-protected `map[section]map[key]value`. It implements section discovery, section existence/deletion, key listing, value get/set/delete, no-op `Load` and `Save`, and JSON `Serialize`. `SetValue` lazily creates missing sections; delete methods are idempotent where possible.

## State And Persistence
All state lives in memory and is guarded by an RWMutex. `Load` and `Save` deliberately do no persistence; `Serialize` emits a JSON snapshot of the map rather than rclone's normal config-file syntax.

## Dependencies And Integration Points
Only depends on `encoding/json` and `sync`. The compile-time `var _ Storage` check ties it to the wider config storage abstraction.

## Risks And Test Signals
The JSON serialization differs from file-backed INI serialization, so callers must not rely on it for encrypted or configfile-compatible output. Tests cover section/key CRUD and serialization success, but not concurrent access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/default_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/default_storage_test.go -->
# sources/user-network-fs/rclone/fs/config/default_storage_test.go

## Purpose
Unit coverage for the in-memory `defaultStorage` implementation.

## Important APIs, Types, And Control Flow
`TestDefaultStorage` creates storage, writes two sections, checks `GetValue`, section enumeration, `HasSection`, key enumeration, `Serialize`, `DeleteKey`, and `DeleteSection`. It verifies both positive paths and missing section/key behavior.

## State And Persistence
State is local to one storage instance. No filesystem state is used; `Serialize` is called only to assert it does not error.

## Dependencies And Integration Points
Uses testify assertions and the unexported constructor because the test is in package `config`.

## Risks And Test Signals
The test confirms basic interface semantics but does not exercise the mutex under concurrent readers/writers or verify exact serialized JSON ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/default_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/flags/flags.go -->
# sources/user-network-fs/rclone/fs/config/flags/flags.go

## Purpose
Wraps `spf13/pflag` with rclone-specific environment-variable defaults, option-to-flag conversion, and documentation grouping.

## Important APIs, Types, And Control Flow
`Groups` and `Group` collect flag sets by named categories. `installFlag` locates a flag, reads its `RCLONE_*` environment default, applies special CSV parsing for `[]string` `fs.Option` values, updates `DefValue`, and registers global flags into `All`. Wrapper functions (`StringP`, `BoolP`, `DurationP`, `VarP`, `StringArrayP`, `CountP`, etc.) create flags then call `installFlag`. `AddFlagsFromOptions` converts `fs.Options` into pflag values, trims help to the first sentence, marks password flags as obscured, sets bool `NoOptDefVal`, and respects command-line hiding.

## State And Persistence
Global `All` is initialized with standard documentation groups. Runtime state is pflag registration plus process environment-derived defaults; no files are persisted.

## Dependencies And Integration Points
Integrates pflag, `fs.Option`, `fs.CommaSepList`, option hiding, environment naming, and rclone command documentation grouping.

## Risks And Test Signals
Unknown groups and malformed env values are fatal, so command initialization can abort early. Duplicate option names are skipped/logged. Risk areas are env CSV quoting for arrays, prefix/no-prefix lookup consistency, and global mutation during tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/flags/flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/obscure/obscure.go -->
# sources/user-network-fs/rclone/fs/config/obscure/obscure.go

## Purpose
Implements rclone's reversible password/value obscuring format. It is intended to prevent casual inspection in config files, not to provide strong secret storage.

## Important APIs, Types, And Control Flow
`Obscure` prepends a random AES block-size IV, encrypts plaintext with AES-CTR using a package static key, and encodes with raw URL-safe base64. `Reveal` decodes, validates minimum length, splits IV and ciphertext, and applies the same CTR operation in place. `MustObscure` and `MustReveal` fatal-log on failure.

## State And Persistence
Package globals hold the static key, lazily initialized AES block, and `cryptRand` reader. Obscured strings are stored by config callers; this file itself persists nothing.

## Dependencies And Integration Points
Uses Go crypto AES/CTR, crypto random, raw URL base64, and `fs.Fatalf`. Config UI and remote update/password paths call these helpers for password options.

## Risks And Test Signals
Because the key is embedded in source, obscuring is reversible by anyone with rclone. In-place reveal mutates the decoded buffer but not caller input. Tests pin deterministic IV outputs, bidirectionality, and decode/short-input errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/obscure/obscure.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/obscure/obscure_test.go -->
# sources/user-network-fs/rclone/fs/config/obscure/obscure_test.go

## Purpose
Verifies the obscuring codec with deterministic IVs and malformed input cases.

## Important APIs, Types, And Control Flow
Tests temporarily replace package `cryptRand` with fixed byte buffers, assert exact `Obscure` output for empty and non-empty strings, round-trip through `Reveal`, and exercise `MustObscure`/`MustReveal`. Error cases cover illegal base64 and ciphertext shorter than the AES block IV.

## State And Persistence
The only mutated state is package-level `cryptRand`, restored to `rand.Reader` after deterministic calls. No filesystem persistence is used.

## Dependencies And Integration Points
Uses `bytes.Buffer`, `crypto/rand`, and testify. It directly tests unexported package state because it is in package `obscure`.

## Risks And Test Signals
Good signal for format stability and failure messages. It does not test random-reader failure or oversized values, both handled in production code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/obscure/obscure_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/rc.go -->
# sources/user-network-fs/rclone/fs/config/rc.go

## Purpose
Registers Remote Control API endpoints for inspecting and mutating rclone configuration.

## Important APIs, Types, And Control Flow
Multiple `init` blocks register `config/unlock`, `config/dump`, `config/get`, `config/listremotes`, `config/providers`, `config/create`, `config/update`, `config/password`, `config/delete`, `config/setpath`, and `config/paths`. Handlers parse `rc.Params`, call config functions such as `CreateRemote`, `UpdateRemote`, `PasswordRemote`, `DeleteRemote`, `SetConfigPath`, and return JSON-shaped `rc.Params`. `rcConfig` handles backwards-compatible `obscure` and `noObscure` top-level flags and reshapes non-interactive `fs.ConfigOut`.

## State And Persistence
Handlers mutate global config storage and the selected config path. Create/update/password/delete may save config via lower-level helpers. Unlock changes process-local config password state.

## Dependencies And Integration Points
Integrates `fs.Registry`, `rc.Calls`, config storage, remote creation/update helpers, and OS temp/cache/config paths.

## Risks And Test Signals
Mis-shaped RC params return errors; legacy param names remain accepted. Risks include global config-path mutation and unintended persistence from remote mutation endpoints. Tests cover endpoint registration and representative CRUD, providers, paths, setpath, and unlock behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/rc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/rc_test.go -->
# sources/user-network-fs/rclone/fs/config/rc_test.go

## Purpose
External-package tests for config RC endpoints.

## Important APIs, Types, And Control Flow
`TestRc` installs a temp config path, creates a local remote through `config/create`, then subtests dump, get, list remotes including env-defined remotes, update, password-obscuring behavior, delete, and empty list shape. Separate tests validate `config/providers`, `config/setpath`, `config/paths`, and both current and legacy unlock password params.

## State And Persistence
The test swaps the global config path and installs configfile storage, restoring the previous path. Environment variable `RCLONE_CONFIG_MY-LOCAL_TYPE` is temporarily set for listremotes.

## Dependencies And Integration Points
Imports the local backend to ensure provider registration. Uses `rc.Calls.Get` and direct handler invocation instead of HTTP.

## Risks And Test Signals
Strong signal for RC JSON contracts and global config mutation. It does not exercise non-interactive continuation state in `rcConfig` beyond basic nil-output behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/rc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/enc-invalid.conf -->
# sources/user-network-fs/rclone/fs/config/testdata/enc-invalid.conf

## Purpose
Fixture for encrypted config load failure when the encrypted payload contains invalid base64 characters.

## Important APIs, Types, And Control Flow
The file has the encrypted config header and `RCLONE_ENCRYPT_V0:` marker followed by a payload containing non-base64 characters. `crypt_test.go` points `SetConfigPath` at this file and expects `Data().Load()` to return an error.

## State And Persistence
Static test data only. It is never modified by tests.

## Dependencies And Integration Points
Consumed by config encryption tests and the configfile loader's encrypted-file parser.

## Risks And Test Signals
Good regression signal for rejecting corrupt encoded data before decryption. It is a minimal fixture and does not describe every possible malformed encrypted file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/enc-invalid.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/enc-short.conf -->
# sources/user-network-fs/rclone/fs/config/testdata/enc-short.conf

## Purpose
Fixture for encrypted config load failure when the payload is too short to contain required encryption metadata/ciphertext.

## Important APIs, Types, And Control Flow
The file uses the encrypted config header and `RCLONE_ENCRYPT_V0:` marker with a truncated base64-looking payload. The config load test expects an error when decoding/decrypting it.

## State And Persistence
Static immutable test data.

## Dependencies And Integration Points
Used by `TestConfigLoadEncryptedFailures` in the external config tests.

## Risks And Test Signals
Confirms short encrypted files do not silently load as empty configs. It does not cover all boundary lengths around the minimum encrypted payload size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/enc-short.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/enc-too-new.conf -->
# sources/user-network-fs/rclone/fs/config/testdata/enc-too-new.conf

## Purpose
Fixture for encrypted config load failure when the encryption version marker is newer than the loader supports.

## Important APIs, Types, And Control Flow
The file is shaped like an encrypted config but uses `RCLONE_ENCRYPT_V1:` rather than the supported V0 marker. Tests set this as the config path and expect load failure.

## State And Persistence
Static fixture with no runtime mutation.

## Dependencies And Integration Points
Connects encrypted config parser version checks to public load behavior.

## Risks And Test Signals
Good signal for forward-version rejection. It does not validate a future migration path, only fail-fast behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/enc-too-new.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/encrypted.conf -->
# sources/user-network-fs/rclone/fs/config/testdata/encrypted.conf

## Purpose
Known-good encrypted config fixture used to validate password-based and password-command-based config loading.

## Important APIs, Types, And Control Flow
The fixture has the encrypted config header, `RCLONE_ENCRYPT_V0:` marker, and a payload that decrypts with password `asdf` into remotes `nounc` and `unc`.

## State And Persistence
Static test data. Tests read it repeatedly and clear the process config password afterward.

## Dependencies And Integration Points
Used by `crypt_test.go` with both direct `SetConfigPassword` and `PasswordCommand` flows.

## Risks And Test Signals
It is the main positive signal for encrypted config compatibility. Since it is a single encrypted blob, it does not exercise large configs, many sections, or alternate password encodings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/encrypted.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/plain.conf -->
# sources/user-network-fs/rclone/fs/config/testdata/plain.conf

## Purpose
Plaintext config fixture representing the decrypted content expected from the encrypted fixture.

## Important APIs, Types, And Control Flow
Defines a `RCLONE_ENCRYPT_V0` local section plus `nounc` and `unc` local remotes with boolean `nounc` values. It provides a readable baseline for config parser behavior and encrypted fixture semantics.

## State And Persistence
Static INI-style config data with no mutation.

## Dependencies And Integration Points
May be used by config load tests and as human-readable companion data for encrypted config tests.

## Risks And Test Signals
Validates simple section/key parsing shape. It does not include comments, duplicate keys, escaped values, or password fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/plain.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/ui.go -->
# sources/user-network-fs/rclone/fs/config/ui.go

## Purpose
Implements rclone's textual interactive configuration UI for creating, editing, copying, renaming, deleting, displaying, and password-protecting remotes.

## Important APIs, Types, And Control Flow
Input helpers include `ReadLine`, `ReadNonEmptyLine`, `CommandDefault`, `Confirm`, `Choose`, `Enter`, `ChoosePassword`, and `ChooseNumber`. Remote operations include `ShowRemotes`, `ChooseRemote`, `ShowRemote`, `ShowRedactedRemote`, `OkRemote`, `NewRemoteName`, `NewRemote`, `EditRemote`, `DeleteRemote`, `RenameRemote`, `CopyRemote`, `ShowConfig`, `ShowRedactedConfig`, and `EditConfig`. Backend configuration loops through `fs.BackendConfig` states, prompting for `fs.Option` values via `ChooseOption`, then calls create/update/post-config helpers. Password functions validate UTF-8, trim warnings, NFKC-normalize, double-enter confirmation, and toggle config encryption.

## State And Persistence
Uses global `ReadLine`, buffered stdin state, global loaded config data, config encryption key state, and `SaveConfig`. Remote create/edit/delete/rename/copy persist through config storage; display functions only print.

## Dependencies And Integration Points
Integrates terminal/liner input, backend registry, configmap/configstruct conversion, obscure password storage, drive-letter and config-name validation, and filesystem `ConfigInfo` for auto-confirm.

## Risks And Test Signals
Interactive loops can fatal on input errors and mutate global state. Sensitive output is redacted only when backend options mark fields password/sensitive. Tests script `ReadLine` to cover CRUD, option parsing, required/default choice rules, password generation, and exclusive examples.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/ui.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/ui_test.go -->
# sources/user-network-fs/rclone/fs/config/ui_test.go

## Purpose
External-package scripted tests for the interactive config UI and programmatic remote update/password helpers.

## Important APIs, Types, And Control Flow
`testConfigFile` installs temp configfile storage, redirects stdout, registers a fake backend, and restores global config. `makeReadLine` feeds scripted answers. Tests cover `NewRemote`, `RenameRemote`, `DeleteRemote`, `ChooseOption`, generated passwords, `NewRemoteName`, `CreateRemote`, `UpdateRemote`, `PasswordRemote`, and required/default/multiple-choice/exclusive option semantics.

## State And Persistence
The tests create temporary config files, mutate global `config.ReadLine`, `config.Password`, `fs.ConfigInfo`, environment variables for config keys, and the global config storage, then restore them.

## Dependencies And Integration Points
Uses configfile storage, obscure codec, fake `fs.RegInfo` backend options, RC parameter maps, and testify.

## Risks And Test Signals
Good signal for user-facing config prompts without an actual terminal. Because stdout is nil and assertions focus on stored values, prompt formatting regressions may pass unnoticed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/ui_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config_list.go -->
# sources/user-network-fs/rclone/fs/config_list.go

## Purpose
Defines reusable flag/config value types for comma-separated and space-separated string lists using CSV quoting rules.

## Important APIs, Types, And Control Flow
`CommaSepList` and `SpaceSepList` implement `String`, `Set`, `Type`, and `fmt.Scanner`. Shared `genericList` serializes through `csv.Writer` with configurable comma rune, parses one CSV record from bytes, strips line-number context from parse errors, and scans all remaining token text.

## State And Persistence
List values are in-memory slices. Empty input resets the list to nil. No persistence is performed directly; callers store string representations in flags/config.

## Dependencies And Integration Points
Used by flag wrappers, password-command config, and any option needing shell-like space lists with quotes. Depends on `encoding/csv`.

## Risks And Test Signals
CSV space-separated semantics are not shell parsing; backslashes and single quotes are literal in many cases. Tests document quoting behavior and invalid bare quotes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config_list_test.go -->
# sources/user-network-fs/rclone/fs/config_list_test.go

## Purpose
Documents and verifies `SpaceSepList` and `CommaSepList` parsing/formatting.

## Important APIs, Types, And Control Flow
Examples show quoted spaces and doubled quotes for both separators. `TestSpaceSepListSet` table-drives empty input, backslashes, single quotes, double-quoted fields, multi-field input, and CSV parse errors.

## State And Persistence
Only local list values are mutated. No filesystem or global config state is touched.

## Dependencies And Integration Points
Uses `fmt` examples as documentation tests and testify `require` for assertions.

## Risks And Test Signals
The test is strong for current CSV behavior but mostly focused on space lists; comma list parsing is covered by examples rather than exhaustive invalid cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config_test.go -->
# sources/user-network-fs/rclone/fs/config_test.go

## Purpose
Tests context-scoped global `fs.ConfigInfo` behavior and RC request context propagation.

## Important APIs, Types, And Control Flow
`TestGetConfig` checks nil context fallback, default global config, `AddConfig` shallow copy behavior, and retrieving context-local config. `TestRCRequestContext` verifies `WithRCRequest`, `IsRCRequest`, and `CopyConfig` preserve or omit the marker correctly with and without an embedded config.

## State And Persistence
No persistent state. Contexts carry copied config and marker values; one context-local config mutates `Transfers` to prove independence.

## Dependencies And Integration Points
Targets package `fs` configuration context helpers, which are consumed across command, RC, and backend code.

## Risks And Test Signals
Good regression signal for detached RC contexts. It does not deeply test every `ConfigInfo` field copied by `AddConfig`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/configmap.go -->
# sources/user-network-fs/rclone/fs/configmap.go

## Purpose
Builds layered config lookup maps for backend/global options, merging connection strings, explicit option values, environment variables, config file values, and defaults.

## Important APIs, Types, And Control Flow
Getter types include `configEnvVars` for `RCLONE_CONFIG_REMOTE_KEY`, `optionEnvVars` for backend/global `RCLONE_*` options with no-prefix fallback, `regInfoValues` for defaults or non-default flags, and `getConfigFile`. `setConfigFile` writes values through `ConfigFileSet`. `ConfigMap` orders getters from highest priority connection-string/flag/remote-env/backend-env/config-file/default and attaches the config-file setter.

## State And Persistence
Reads process environment and config-file storage. Setters persist to the active config file/storage layer via config helpers.

## Dependencies And Integration Points
Depends on `fs/config/configmap`, option metadata, environment naming helpers, and config file get/set functions. Backend initialization uses this to resolve option values.

## Risks And Test Signals
Priority order is critical: changing it can alter compatibility. Empty config-file values are treated as absent. No direct tests here, but many backend/config tests indirectly depend on this resolution path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/configmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/countsuffix.go -->
# sources/user-network-fs/rclone/fs/countsuffix.go

## Purpose
Implements `CountSuffix`, an int64 flag/config type for decimal count units (`k`, `M`, `G`, `T`, `P`, `E`) and `off`.

## Important APIs, Types, And Control Flow
`String` and `Unit` scale values to the largest decimal suffix with integer or three-decimal formatting. `Set` parses empty/error cases, `off`, byte suffixes, plain numbers defaulting to kilo, decimal values, and rejects negative values/bad suffixes. It implements `Type`, `Scan`, JSON unmarshalling through `UnmarshalJSONFlag`, and sortable `CountSuffixList`.

## State And Persistence
Pure value parsing/formatting with no external state. Negative values render as `off`.

## Dependencies And Integration Points
Used by flags/options needing count quantities rather than binary byte sizes. Integrates with rclone's flagger interfaces and JSON config parsing.

## Risks And Test Signals
Defaulting bare numbers to kilo can surprise callers expecting raw counts. Float-to-int truncation is implicit. Tests cover rendering, parsing, scanning, and string/numeric JSON.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/countsuffix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/countsuffix_test.go -->
# sources/user-network-fs/rclone/fs/countsuffix_test.go

## Purpose
Table-driven tests for `CountSuffix` formatting, parsing, scanning, and JSON unmarshalling.

## Important APIs, Types, And Control Flow
Tests assert interface satisfaction, `String`, `Unit`, `Set`, `fmt.Sscan`, and `json.Unmarshal` behavior. Tables include decimal suffixes, byte suffixes, bare numbers, `off`, empty string, invalid suffixes, negative values, and malformed JSON.

## State And Persistence
Local values only; no global state.

## Dependencies And Integration Points
Uses testify and Go `encoding/json`/`fmt`. Confirms compatibility with rclone `Flagger` and `FlaggerNP`.

## Risks And Test Signals
Strong signal for accepted grammar. It does not test overflow near `math.MaxInt64` despite constants documenting limits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/countsuffix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/cutoffmode.go -->
# sources/user-network-fs/rclone/fs/cutoffmode.go

## Purpose
Defines the `CutoffMode` enum controlling transfer cutoff behavior.

## Important APIs, Types, And Control Flow
`cutoffModeChoices` supplies choices `HARD`, `SOFT`, and `CAUTIOUS` to the generic `Enum` implementation. Constants map iota values to names and set `CutoffModeDefault` to hard.

## State And Persistence
Pure typed constants with no runtime state.

## Dependencies And Integration Points
Depends on the generic `Enum` helper for flag, scan, JSON, string, and help behavior. Used by configuration options that control cutoff semantics.

## Risks And Test Signals
Choice order is serialized by integer value, so reordering would break numeric compatibility. Tests cover string, set, and JSON paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/cutoffmode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/cutoffmode_test.go -->
# sources/user-network-fs/rclone/fs/cutoffmode_test.go

## Purpose
Verifies `CutoffMode` enum behavior.

## Important APIs, Types, And Control Flow
Tests assert flagger interface satisfaction, `String` on known and unknown values, case-insensitive `Set`, and JSON unmarshalling from strings and numeric enum indexes.

## State And Persistence
No external state.

## Dependencies And Integration Points
Uses the generic `Enum` implementation through the concrete alias.

## Risks And Test Signals
Good signal for accepted values and invalid ranges. It does not test JSON marshal because that is covered by `enum_test.go` generically.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/cutoffmode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/daemon_other.go -->
# sources/user-network-fs/rclone/fs/daemon_other.go

## Purpose
Non-Unix daemonization adapter for Windows, Plan 9, and JavaScript builds.

## Important APIs, Types, And Control Flow
`IsDaemon` always returns false because these build targets do not use the Unix daemon marker protocol in this file.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Selected by build tags `windows || plan9 || js`; paired with `daemon_unix.go` for other platforms.

## Risks And Test Signals
Correctness depends on build tags. There are no direct tests in this subset; platform builds are the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/daemon_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/daemon_unix.go -->
# sources/user-network-fs/rclone/fs/daemon_unix.go

## Purpose
Unix daemonization marker helper.

## Important APIs, Types, And Control Flow
Defines `DaemonMarkVar` and `DaemonMarkChild`. `IsDaemon` returns true when the process environment variable `_RCLONE_DAEMON_` equals `_rclone_daemon_`.

## State And Persistence
Reads process environment only; no files are touched.

## Dependencies And Integration Points
Selected on non-Windows, non-Plan9, non-JS builds. The process-spawning daemon code sets the marker for child processes.

## Risks And Test Signals
Any external process can set the env var, so this is a role marker, not a security boundary. Platform builds and daemon integration are the relevant tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/daemon_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/deletemode.go -->
# sources/user-network-fs/rclone/fs/deletemode.go

## Purpose
Defines delete timing constants for sync/delete operations.

## Important APIs, Types, And Control Flow
`DeleteMode` is a byte enum with values off, before, during, after, only, and default after. This file contains only the type and constants; parsing/string behavior likely lives elsewhere or through option metadata.

## State And Persistence
Pure constants, no state.

## Dependencies And Integration Points
Consumed by higher-level operations and config options controlling when destination deletions occur.

## Risks And Test Signals
Numeric ordering is compatibility-sensitive. No direct tests in this subset, so behavior relies on consumers and option parsing tests elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/deletemode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dir.go -->
# sources/user-network-fs/rclone/fs/dir.go

## Purpose
Provides `Dir`, a generic implementation of rclone's `Directory`/`DirEntry` interfaces for unspecialized directories, buckets, or containers.

## Important APIs, Types, And Control Flow
Constructors `NewDir` and `NewDirCopy` initialize remote path, modtime, size/items defaults, filesystem info, and optional IDs. Methods expose and fluently mutate remote, ID, parent ID, size, and items. `ModTime` returns stored time or configured default directory time when unknown.

## State And Persistence
Each `Dir` is an in-memory value. It references `fs.ConfigInfo.DefaultTime` when modtime is zero.

## Dependencies And Integration Points
Implements `DirEntry` and `Directory`; used by list results, dirtree synthesis, and backends that need simple directory objects.

## Risks And Test Signals
`NewDirCopy` copies ID but not parent ID. Unknown modtimes depend on context config. Interface compile checks are present; behavior is tested indirectly by dirtree and directory entry tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dir_wrapper.go -->
# sources/user-network-fs/rclone/fs/dir_wrapper.go

## Purpose
Wraps a backend `Directory` while overriding its remote path and forwarding optional directory capabilities.

## Important APIs, Types, And Control Flow
`NewDirWrapper` and `NewLimitedDirWrapper` create wrappers; limited wrappers silently ignore missing `SetMetadata` and `SetModTime`. `Remote`, `String`, and `SetRemote` use the override. `Metadata`, `SetMetadata`, and `SetModTime` type-assert optional interfaces and return nil or `ErrorNotImplemented` when unsupported.

## State And Persistence
In-memory wrapper state consists of the wrapped directory, override remote, and fail-silently flag. Persistence is delegated to the wrapped directory's optional methods.

## Dependencies And Integration Points
Implements `DirEntry`, `Directory`, and `FullDirectory`, supporting overlay/combine backends that rewrite paths.

## Risks And Test Signals
Silent failure mode can hide unsupported metadata/modtime changes by design. Compile-time interface checks exist; direct behavior tests are not in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dir_wrapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/direntries.go -->
# sources/user-network-fs/rclone/fs/direntries.go

## Purpose
Defines helpers for slices of directory entries returned by list operations.

## Important APIs, Types, And Control Flow
`DirEntries` implements `sort.Interface` using `CompareDirEntries`. Iteration helpers run callbacks over only objects or only directories, with error-short-circuiting variants. `DirEntryType` classifies entries as object, directory, or unknown. `CompareDirEntries` sorts by remote path and then type, placing directories before objects for identical names because `directory` sorts before `object`.

## State And Persistence
Pure slice operations; no external state.

## Dependencies And Integration Points
Used by listing, operations, dirtree, and tests with mock objects/directories.

## Risks And Test Signals
Unknown entry types sort by formatted type string, which is mainly diagnostic. Tests cover stable sorting with duplicate object names and same-name directory/object pairs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/direntries.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/direntries_test.go -->
# sources/user-network-fs/rclone/fs/direntries_test.go

## Purpose
Tests `DirEntries` sort ordering.

## Important APIs, Types, And Control Flow
Creates mock objects and directories with names `a`, `b`, and `c`, sorts stably, and expects directories before objects for equal remote names while preserving duplicate object order.

## State And Persistence
No persistence; local mock entries only.

## Dependencies And Integration Points
Uses `fstest/mockdir`, `fstest/mockobject`, standard `sort`, and testify.

## Risks And Test Signals
Focused signal for ordering. It does not cover callback helper methods or unknown entry classification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/direntries_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dirtree/dirtree.go -->
# sources/user-network-fs/rclone/fs/dirtree/dirtree.go

## Purpose
Builds an in-memory directory tree mapping directory paths to their child `fs.DirEntries`.

## Important APIs, Types, And Control Flow
`DirTree` is `map[string]fs.DirEntries`. `Add` inserts an entry under its parent, `AddDir` also ensures the directory has a key, and `AddEntry` adds files/directories plus missing parents. `Find` searches a parent slice. `checkParent` and `CheckParents` synthesize missing parent `fs.Dir` entries. `Sort`, `Dirs`, `Prune`, and `String` provide deterministic traversal, subtree removal, and display.

## State And Persistence
All state is in-memory map/slices. Synthesized parents use `time.Now()` modtimes. `Prune` mutates both the tree and the caller-provided directory map.

## Dependencies And Integration Points
Depends on `fs.DirEntries`, `fs.NewDir`, and path utilities. Used by recursive listing and sync logic that needs a materialized hierarchy.

## Risks And Test Signals
`Find` is O(N), and `Prune` deliberately mutates during map iteration to avoid recursion. Unknown entry types cause errors or panic depending on path. Tests cover add, parent synthesis, sorting, dirs, pruning, and a parent-check benchmark.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dirtree/dirtree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dirtree/dirtree_test.go -->
# sources/user-network-fs/rclone/fs/dirtree/dirtree_test.go

## Purpose
Unit and benchmark coverage for `DirTree`.

## Important APIs, Types, And Control Flow
Tests validate `New`, `parentDir`, `Add`, `AddDir`, `AddEntry`, `Find`, `checkParent`, `CheckParents`, `Sort`, `Dirs`, and `Prune` using string snapshots. The benchmark measures `CheckParents` over increasing flat directory counts.

## State And Persistence
Only in-memory mock entries and trees are used.

## Dependencies And Integration Points
Uses `fstest/mockdir` and `mockobject`, plus testify.

## Risks And Test Signals
Snapshot strings give strong structural coverage, though synthesized parent modtimes are not asserted. Benchmark highlights scalability risk in parent synthesis.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dirtree/dirtree_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/driveletter/driveletter.go -->
# sources/user-network-fs/rclone/fs/driveletter/driveletter.go

## Purpose
Non-Windows implementation of drive-letter detection.

## Important APIs, Types, And Control Flow
`IsDriveLetter` always returns false because single-letter remote names are not ambiguous with Windows drive letters on non-Windows platforms.

## State And Persistence
No state.

## Dependencies And Integration Points
Selected by `!windows` build tag. Config UI uses it to reject names that could be confused with drive letters only where relevant.

## Risks And Test Signals
Build-tag selection is the key behavior. Direct tests are platform-dependent and not present here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/driveletter/driveletter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/driveletter/driveletter_windows.go -->
# sources/user-network-fs/rclone/fs/driveletter/driveletter_windows.go

## Purpose
Windows implementation of drive-letter detection for config remote names.

## Important APIs, Types, And Control Flow
`IsDriveLetter` returns true only for one-character ASCII letters `a-z` or `A-Z`; all other strings are false.

## State And Persistence
Pure function with no state.

## Dependencies And Integration Points
Selected by `windows` build tag and used by config UI name validation to avoid ambiguity with paths like `C:`.

## Risks And Test Signals
Only ASCII letters count; Unicode drive-like characters are rejected. Cross-platform builds are the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/driveletter/driveletter_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dump.go -->
# sources/user-network-fs/rclone/fs/dump.go

## Purpose
Defines bit flags for rclone's `--dump` diagnostics.

## Important APIs, Types, And Control Flow
`DumpFlags` aliases generic `Bits[dumpChoices]`. Constants define headers, bodies, requests, responses, auth, filters, goroutines, open files, mapper, curl, errors, and trace. `dumpChoices.Choices` maps bits to CLI strings, `Type` returns `DumpFlags`, and `DumpFlagsList` is generated from help text.

## State And Persistence
Pure constants and generated help string.

## Dependencies And Integration Points
Consumed by HTTP dump/logging code, filter dump output, and global config options. Relies on generic bit flag parsing.

## Risks And Test Signals
Bit values are serialized and compatibility-sensitive. Tests cover string, set, type, and JSON behavior including unknown bits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dump.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dump_test.go -->
# sources/user-network-fs/rclone/fs/dump_test.go

## Purpose
Tests `DumpFlags` bitset parsing and rendering.

## Important APIs, Types, And Control Flow
Assertions cover empty and combined `String`, unknown bit rendering, comma-separated `Set`, invalid choice preservation of the previous value, `Type`, and JSON unmarshalling from strings and integers.

## State And Persistence
Local flag values only.

## Dependencies And Integration Points
Uses the generic `Bits` implementation through `DumpFlags`.

## Risks And Test Signals
Good coverage for CLI/JSON syntax. It does not test actual dump logging behavior; `fshttp/dump_test.go` covers part of that integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dump_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/enum.go -->
# sources/user-network-fs/rclone/fs/enum.go

## Purpose
Generic enum helper for byte-backed option types with string choices.

## Important APIs, Types, And Control Flow
`Enum[C Choices]` obtains choices from zero value `C`. It implements `String`, `Choices`, `Help`, case-insensitive `Set`, `Type` with optional `typer` override, `Scan`, JSON unmarshal from strings or numeric indexes, and JSON marshal as the string form.

## State And Persistence
Pure value methods. Numeric JSON values directly set enum indexes after range validation.

## Dependencies And Integration Points
Used by `CutoffMode` and other typed config options. Integrates with rclone flagger interfaces and `UnmarshalJSONFlag`.

## Risks And Test Signals
Choice order is ABI/config compatible because numeric input maps to indexes. Unknown enum values stringify as `Unknown(n)` and will marshal that string. Generic tests cover the core behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/enum.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/enum_test.go -->
# sources/user-network-fs/rclone/fs/enum_test.go

## Purpose
Generic tests for `Enum`.

## Important APIs, Types, And Control Flow
Defines example choices A/B/C and validates string rendering, type fallback and type override, help text, set errors, scanning, JSON string/numeric unmarshal, out-of-range errors, and JSON marshal.

## State And Persistence
No external state.

## Dependencies And Integration Points
Confirms compatibility with rclone flagger interfaces and JSON config parsing.

## Risks And Test Signals
Good coverage for all exported methods. It does not test an enum with no choices beyond the custom Type override case.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/enum_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/features.go -->
# sources/user-network-fs/rclone/fs/features.go

## Purpose
Centralizes optional filesystem capabilities and the interfaces backends implement to advertise them.

## Important APIs, Types, And Control Flow
`Features` contains boolean capability flags and function pointers for optional operations such as purge, server-side copy/move, directory metadata, change notify, wrapping, public links, unchecked/stream/chunked upload, recursive listing, quota, backend commands, disconnect, and shutdown. `Fill` detects optional interfaces on an `Fs`, stores methods, marks wrappers as overlays, and applies disabled-feature config. `Mask` intersects capabilities with another Fs for wrappers. `Wrap` and `WrapsFs` preserve wrapper relationships. `UnWrapFs`, `UnWrapObject`, and `UnWrapObjectInfo` peel wrapper layers.

## State And Persistence
Feature structs are in-memory descriptors with function pointers. They read `ConfigInfo.DisableFeatures` but do not persist data.

## Dependencies And Integration Points
Defines many public optional interfaces used by all backends and operations. It depends on core Fs/Object/Directory types, metadata, durations, listing callbacks, writer interfaces, and context.

## Risks And Test Signals
Reflection-based disable/list/enabled is string-name sensitive. Mask deliberately does not propagate some flags (`IsLocal`, `Overlay`) and keeps wrapper functions. Tests cover disable/list/enabled; broader behavior is exercised by backend integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/features.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/filter.go -->
# sources/user-network-fs/rclone/fs/filter/filter.go

## Purpose
Implements rclone's runtime file, directory, metadata, age, size, hash-partition, exclude-if-present, and files-from filtering.

## Important APIs, Types, And Control Flow
`OptionsInfo` defines global filter flags; `Options` stores parsed config. `NewFilter` copies options, computes age windows, parses hash filters, parses file and metadata rules, enforces files-from exclusivity, reads files-from lists, and optionally dumps filters. `Filter` tracks file/dir/meta rules, files-from maps, and hash partition parameters. Inclusion flow checks files-from first, then hash, path rules, directory rules, exclude marker files, age/size, and metadata rules. Context helpers manage global or context-local filters and a `use filter` marker. `MakeListR` converts files-from into a concurrent `ListR` callback producer.

## State And Persistence
Global `Opt` and `globalConfig` hold process-wide defaults. Individual filters store parsed maps and time windows. Rule files and stdin may be read; no filter state is written to disk.

## Dependencies And Integration Points
Integrates `fs.Options`, global options registration/reload, glob/rules parsing, metadata extraction, `fs.FileExists`, object listing callbacks, errgroup concurrency, and config context.

## Risks And Test Signals
Files-from overrides most other filters, hash filter uses normalized lower-case MD5 partitions, and metadata filtering treats absent metadata with a sentinel. Tests cover many construction and inclusion scenarios, docs examples, directory filters, metadata filters, and context config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/filter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/filter_test.go -->
# sources/user-network-fs/rclone/fs/filter/filter_test.go

## Purpose
Comprehensive tests for filter option parsing and inclusion behavior.

## Important APIs, Types, And Control Flow
Tests cover default filters, hash-filter parsing, forbidden mixing of files-from with other filters, files-from/raw list loading, include/exclude/filter rules, directory include decisions, files-from `ListR`, min/max size and age, case-insensitive matching, regex globs, metadata include/exclude, adding directory/file rules, line reading from files/stdin with raw and non-raw modes, documentation examples, directory-filter usage detection, and context config helpers.

## State And Persistence
Uses temporary files and temporarily replaces stdin in line-reading tests. Context-local filter configs avoid mutating only global state where possible.

## Dependencies And Integration Points
Uses mock objects/filesystems, filter rule files, metadata maps, and testify. It exercises `glob.go` and `rules.go` through public filter construction.

## Risks And Test Signals
Strong behavioral coverage. Remaining risks are time-dependent age boundaries, random `@/n` hash partitions, and backend-specific filter-aware listing interactions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/filter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/filterflags/filterflags.go -->
# sources/user-network-fs/rclone/fs/filter/filterflags/filterflags.go

## Purpose
Small adapter that registers filter options as command-line flags.

## Important APIs, Types, And Control Flow
`AddFlags` calls `flags.AddFlagsFromOptions(flagSet, "", filter.OptionsInfo)`, letting the generic config flag layer create all filter flags without backend prefixes.

## State And Persistence
Mutates the provided pflag set; no persistence.

## Dependencies And Integration Points
Connects `fs/filter.OptionsInfo` to `fs/config/flags` and command initialization.

## Risks And Test Signals
Behavior depends entirely on `OptionsInfo` and `AddFlagsFromOptions`. No direct tests; command flag registration and filter tests provide indirect signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/filterflags/filterflags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/glob.go -->
# sources/user-network-fs/rclone/fs/filter/glob.go

## Purpose
Converts rclone/rsync-style glob syntax into Go regular expressions and derives directory globs from file globs.

## Important APIs, Types, And Control Flow
`GlobPathToRegexp` enables path mode with anchors; `GlobStringToRegexp` supports string mode with optional anchors and case-insensitivity. `globToRegexp` parses `*`, `**`, `?`, character classes, `{a,b}` alternation, raw `{{regexp}}`, backslashes, path separators, anchors, and regexp metacharacter escaping while detecting mismatched/nested constructs. `globToDirGlobs` returns possible directory globs unless the expression is too hard, in which case it logs and scans all directories.

## State And Persistence
Pure parsing plus logging for too-hard directory derivation. No persistent state.

## Dependencies And Integration Points
Used by filter rule compilation and directory-pruning optimization. Depends on regexp and fs logging.

## Risks And Test Signals
Subtle syntax compatibility risk around braces, raw regexps, and path-mode `**`. Tests cover many accepted and rejected patterns plus directory glob derivation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/glob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/glob_test.go -->
# sources/user-network-fs/rclone/fs/filter/glob_test.go

## Purpose
Table-driven coverage for glob-to-regexp and glob-to-directory-glob conversion.

## Important APIs, Types, And Control Flow
Tests compare exact regexp strings for string mode with/without anchors and ignore-case, path mode, invalid star/bracket/brace/regexp cases, escaped metacharacters, and raw regexp blocks. `TestGlobToDirGlobs` validates directory-pruning globs for absolute, relative, slash-squashed, brace, and `**` patterns.

## State And Persistence
No state beyond compiled regexps.

## Dependencies And Integration Points
Directly tests helpers used by filters.

## Risks And Test Signals
Strong syntax regression signal. It asserts regexp strings, so intentional parser representation changes require test updates even if matching semantics remain equivalent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/glob_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/rules.go -->
# sources/user-network-fs/rclone/fs/filter/rules.go

## Purpose
Parses and evaluates ordered include/exclude rule lists for paths and metadata.

## Important APIs, Types, And Control Flow
`RulesOpt` stores CLI/config lists and rule files. `rule` wraps include bool plus regexp and formats as `+/- regexp`. `rules.add` deduplicates by formatted rule, `include` returns the first matching rule or true, and `includeMany` applies ordered rules across many strings. `forEachLine` reads files or stdin, optionally trimming comments/blank lines. `addRule` parses `+ glob`, `- glob`, and `!` clear. `parseRules` applies include/include-from, exclude/exclude-from, filter/filter-from, logs mixed include/exclude warning, and adds implicit `- /**` after includes.

## State And Persistence
Rules are in-memory slices plus a dedup map. Rule files/stdin are read but not written.

## Dependencies And Integration Points
Used by `Filter.NewFilter` for file and metadata rules. Depends on glob conversion and `fs.CheckClose` for file close errors.

## Risks And Test Signals
Rule order is user-visible. Include plus exclude option ordering is intentionally warned as indeterminate. Tests in `filter_test.go` exercise parsing, line reading, dedup, clear, and inclusion semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/rules.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fingerprint.go -->
# sources/user-network-fs/rclone/fs/fingerprint.go

## Purpose
Builds a compact change fingerprint for an object from size, optional modtime, and optional hash.

## Important APIs, Types, And Control Flow
`Fingerprint(ctx, o, fast)` always writes object size. It includes modtime when not in fast mode or when the backend does not mark modtime slow, and only if precision supports modtime. It includes one available hash when not in fast mode or hash is not marked slow, ignoring hash errors.

## State And Persistence
Pure computation over an `ObjectInfo`; no persistent state. It may call object methods that perform remote operations depending on backend feature flags.

## Dependencies And Integration Points
Used by operations that need a same-object change detector. Depends on `Fs.Features`, precision, hashes, object modtime/hash APIs.

## Risks And Test Signals
Not intended for cross-remote identity comparisons. Fast mode can omit important attributes for slow backends. Tests cover combinations of slow modtime/hash flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fingerprint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fingerprint_test.go -->
# sources/user-network-fs/rclone/fs/fingerprint_test.go

## Purpose
Tests object fingerprint composition under fast/slow feature combinations.

## Important APIs, Types, And Control Flow
Creates a mock Fs with MD5 support and a mock object containing `data`, toggles `Features().SlowModTime` and `SlowHash`, and asserts exact fingerprint strings for fast and non-fast calls.

## State And Persistence
Local mock state only.

## Dependencies And Integration Points
Uses `fstest/mockfs`, `mockobject`, and hash registry support.

## Risks And Test Signals
Good coverage of feature gating. It does not test unsupported modtime precision, hash errors, or a backend with no hashes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fingerprint_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fs.go -->
# sources/user-network-fs/rclone/fs/fs.go

## Purpose
Defines core filesystem constants, common errors, a multipart minimum-size error type, and small utility helpers.

## Important APIs, Types, And Control Flow
Constants include unsupported modtime precision, infinite listing level, and symlink suffix. Exported errors cover config lookup, copy/move/purge capability failures, listing/object/directory conditions, deletion safeguards, immutability, permission, not-implemented, command, filename, root listing, and multipart size. `FileTooSmallError` wraps `ErrorFileTooSmall`. `CheckClose` preserves close errors only when no prior error exists. `FileExists` calls `NewObject` and maps not-found/not-file/permission to false. `GetModifyWindow` returns the max of config modify window and all Fs precisions, short-circuiting unsupported modtime.

## State And Persistence
No persistent state. `GetModifyWindow` reads context config.

## Dependencies And Integration Points
These errors and helpers are used throughout backends and operations as common contracts.

## Risks And Test Signals
Error identity comparisons matter. `FileExists` treating permission denied as non-existence is a deliberate semantic choice. Tests in this subset focus on `Features`, not these helpers directly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fs_test.go -->
# sources/user-network-fs/rclone/fs/fs_test.go

## Purpose
Tests feature reflection helpers defined in `features.go`.

## Important APIs, Types, And Control Flow
Tests verify `Disable` clears function and bool features case-insensitively, `List` includes known feature names, `Enabled` reports bool/function status for all fields, and `DisableList` applies multiple names.

## State And Persistence
Local `Features` instances only.

## Dependencies And Integration Points
Uses function fields matching optional feature signatures.

## Risks And Test Signals
Good signal for reflection helpers. It does not test `Fill`, `Mask`, wrapper propagation, or unwrapping helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/enospc_error.go -->
# sources/user-network-fs/rclone/fs/fserrors/enospc_error.go

## Purpose
Non-Plan9 implementation for detecting disk-full errors in wrapped error chains.

## Important APIs, Types, And Control Flow
`IsErrNoSpace` walks an error chain with `lib/errors.Walk` and returns true if any cause equals `syscall.ENOSPC`.

## State And Persistence
Pure error inspection with no state.

## Dependencies And Integration Points
Used by operations that need to classify no-space failures specially. Depends on syscall `ENOSPC` and rclone error walking.

## Risks And Test Signals
Only exact `syscall.ENOSPC` is detected; string-only errors are not. Plan9 has a separate false implementation. Tests for wrapped syscall causes cover this area indirectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/enospc_error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/enospc_error_notsupported.go -->
# sources/user-network-fs/rclone/fs/fserrors/enospc_error_notsupported.go

## Purpose
Plan9 fallback for no-space detection.

## Important APIs, Types, And Control Flow
`IsErrNoSpace` always returns false because Plan9 lacks `syscall.ENOSPC` support in this code path.

## State And Persistence
No state.

## Dependencies And Integration Points
Selected by the `plan9` build tag and shares the same public function as other platforms.

## Risks And Test Signals
Plan9 cannot classify disk-full errors through this helper. Platform build coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/enospc_error_notsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/error.go -->
# sources/user-network-fs/rclone/fs/fserrors/error.go

## Purpose
Provides rclone's error classification wrappers and retry decision helpers.

## Important APIs, Types, And Control Flow
Defines interfaces and wrappers for high-level retry, fatal, no-retry, no-low-level-retry, retry-after, and countable errors. Constructors wrap nil with default messages where needed and implement `Unwrap` for `errors` compatibility. Detection helpers walk error chains with `lib/errors.Walk`. `Cause` records the root cause and flags `Timeout`/`Temporary`. `ShouldRetry` rejects no-low-level-retry, accepts timeout/temporary causes, known retriable errors, and selected network error string fragments. `ShouldRetryHTTP` checks configured status codes. `ContextError` promotes context cancellation/deadline errors into a pending error pointer.

## State And Persistence
Global retriable error/string slices are initialized here and extended by platform files. Countable wrappers carry mutable counted state.

## Dependencies And Integration Points
Used by low-level HTTP, backend, and operations retry loops. Integrates standard errors, HTTP responses, context cancellation, and rclone's cause walker.

## Risks And Test Signals
String matching is fragile but needed for unexported stdlib errors. Wrapper detection order matters when multiple classifications exist. Tests cover causes, retry decisions, retry-after, context errors, syscall wrapping, and countable behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/error_syscall_test.go -->
# sources/user-network-fs/rclone/fs/fserrors/error_syscall_test.go

## Purpose
Tests retry and cause behavior for wrapped syscall/network errors.

## Important APIs, Types, And Control Flow
`makeNetErr` constructs a `net.OpError` around a `os.SyscallError`. Tests assert `Cause` reaches the syscall errno and `ShouldRetry` returns true for retriable syscall causes.

## State And Persistence
No persistence; local error values only.

## Dependencies And Integration Points
Uses platform syscall constants through the current build and the fserrors classifier.

## Risks And Test Signals
Coverage depends on platform-specific errno availability. Windows-specific extra codes are covered by build-specific initialization rather than this table alone.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/error_syscall_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/error_test.go -->
# sources/user-network-fs/rclone/fs/fserrors/error_test.go

## Purpose
Unit tests for fserrors wrappers, cause walking, retry decisions, retry-after, and context handling.

## Important APIs, Types, And Control Flow
Defines custom wrapper and temporary error types to test `Cause`, `RetryError`, `FatalError`, `NoRetryError`, `NoLowLevelRetryError`, `FsError`, `Count`, `IsCounted`, `ShouldRetry`, `RetryAfterErrorTime`, `IsRetryAfterError`, and `ContextError`. Tables include EOFs, temporary errors, closed network string, no-low-level-retry override, and context cancellation/deadline.

## State And Persistence
Local errors only, except countable wrappers mutate their counted flag.

## Dependencies And Integration Points
Uses rclone error walking and standard context/errors behavior.

## Risks And Test Signals
Strong classifier coverage. It does not exhaust every string phrase in `retriableErrorStrings` or every platform retriable errno.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/error_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/retriable_errors.go -->
# sources/user-network-fs/rclone/fs/fserrors/retriable_errors.go

## Purpose
Adds common non-Plan9 syscall errors to the package-level retriable error list.

## Important APIs, Types, And Control Flow
An `init` function appends `EPIPE`, `ETIMEDOUT`, `ECONNREFUSED`, `EHOSTDOWN`, `EHOSTUNREACH`, `ECONNABORTED`, `EAGAIN`, `EWOULDBLOCK`, and `ECONNRESET` to `retriableErrors`.

## State And Persistence
Mutates the package global retriable error slice at initialization.

## Dependencies And Integration Points
Selected by `!plan9` build tag and feeds `ShouldRetry`.

## Risks And Test Signals
Classification is platform and errno identity dependent. Tests for syscall causes provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/retriable_errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/retriable_errors_windows.go -->
# sources/user-network-fs/rclone/fs/fserrors/retriable_errors_windows.go

## Purpose
Adds Windows-specific Winsock and handle/network errors to retriable classification.

## Important APIs, Types, And Control Flow
Defines selected WSA errno constants not provided uniformly by Go and appends them, along with Go syscall Windows errors, to `retriableErrors` in `init`.

## State And Persistence
Mutates the package global retry list during Windows builds.

## Dependencies And Integration Points
Selected by `windows` build tag and consumed by `ShouldRetry`.

## Risks And Test Signals
The list mirrors Windows socket error semantics and can drift as Go/syscall support changes. Coverage requires Windows test runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/retriable_errors_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fshttp/dialer.go -->
# sources/user-network-fs/rclone/fs/fshttp/dialer.go

## Purpose
Builds rclone's HTTP/network dialer with connect timeout, idle timeout, local bind address, DSCP traffic class, and transport bandwidth accounting.

## Important APIs, Types, And Control Flow
`NewDialer` reads `fs.ConfigInfo` for connect timeout, IO timeout, bind address, and traffic class. `DialContext` forces tcp4/tcp6 when binding unspecified IPv4/IPv6 addresses, dials, applies IPv4 TOS or IPv6 traffic class with one-time warnings, and wraps the connection in `timeoutConn`. `timeoutConn` refreshes deadlines after successful reads/writes and accounts transport RX/TX through the accounting token bucket.

## State And Persistence
Dialer instances hold timeout/tclass config. Package `sync.Once` values suppress repeated DSCP warnings. No persistent files.

## Dependencies And Integration Points
Used by fshttp transports and clients. Integrates net.Dialer, x/net ipv4/ipv6 socket options, global config, logging, and accounting bandwidth limits.

## Risks And Test Signals
DSCP support varies by OS and can fail silently on Windows IPv4. Deadline updates only occur after nonzero successful IO. Tests in this subset target dump behavior, not dialer sockets directly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fshttp/dialer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fshttp/dump_test.go -->
# sources/user-network-fs/rclone/fs/fshttp/dump_test.go

## Purpose
Tests HTTP dump logging behavior for retryable errors and trace logging.

## Important APIs, Types, And Control Flow
`TestIsRetryableResponse` checks transport errors and selected HTTP status codes. `TestDumpErrors` uses an httptest server and captured slog output to verify `--dump errors` gates request/response/curl dumps to retryable responses, with body inclusion controlled by `DumpBodies`. `TestDumpTrace` verifies `DumpTrace` emits httptrace events for HTTP and HTTPS without dumping bodies.

## State And Persistence
Temporarily replaces the global logger and mutates global config dump/log/insecure flags, restoring them in defers. Starts ephemeral HTTP/TLS servers and resets transports around trace tests.

## Dependencies And Integration Points
Exercises fshttp client construction, dump flags from `fs/dump.go`, retryable response classification, slog logging, and httptrace integration.

## Risks And Test Signals
Strong signal for logging gates. It does not verify exact full dump text, only key substrings, and depends on transport reuse for one trace assertion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fshttp/dump_test.go -->
