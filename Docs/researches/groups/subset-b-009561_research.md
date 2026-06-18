# subset-b-009561 research

Grouped research report for the subset-b-009561 work item. Each section is delimited for reconciliation into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mountv1_test.go -->
## sources/user-network-fs/blobfuse2/cmd/mountv1_test.go

Purpose: this is the broad regression suite for the `mountv1` compatibility/conversion command. It verifies that v1-style blobfuse config files and v1 CLI flags are converted into v2 YAML config and component options, and that invalid legacy inputs are rejected with useful errors.

Important APIs and helpers: `generateConfigTestSuite`, `executeCommandC`, `resetCLIFlags`, `randomString`, and `generateFileName` provide isolated Cobra command execution around the global `rootCmd` and global Viper state. Tests unmarshal generated YAML through `common/config` into `azstorage.AzStorageOptions`, `file_cache.FileCacheOptions`, `block_cache.StreamOptions`, `attr_cache.AttrCacheOptions`, `LogOptions`, and `mountOptions`.

Control flow and state: every test creates temporary v1/v2 files, invokes `rootCmd mountv1 --convert-config-only=true`, reads the generated config with Viper, and resets flags plus `viper.Reset()` in cleanup. The cases cover config-file key parsing, SAS/SPN/MSI auth, account type endpoint selection, proxy fields, logging fields, comment stripping, CLI override precedence, file cache and stream component selection, attr cache options, azstorage retry/concurrency fields, libfuse option validation, environment fallback for `AZURE_STORAGE_ACCOUNT`, and invalid account type/name handling.

Dependencies and integration points: the suite depends on Cobra global command registration, Viper global config state, component option structs, temporary filesystem files, and a silent logger. It indirectly exercises `mountv1` parsing/conversion code not in this subset.

Risks: global flags and Viper state make tests order-sensitive if cleanup is missed. The suite asserts generated values but mostly not full YAML shape, so field omissions outside asserted options may escape. Some test names ending in `Error` expect no error for ignored legacy flags, which can confuse maintenance.

Test signals: this file is itself test coverage. It provides strong signal for legacy-to-v2 migration behavior, command-line precedence, invalid FUSE option failures, and environment fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mountv1_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/root.go -->
## sources/user-network-fs/blobfuse2/cmd/root.go

Purpose: defines the top-level `blobfuse2` Cobra command, global version-check behavior, fstab/CLI argument normalization, HTTP transport construction, and the public `Execute` entrypoint.

Important APIs/functions: `rootCmd`, `disableVersionCheck`, `checkVersionExists`, `beginDetectNewVersion`, `VersionCheck`, `ignoreCommand`, `parseArgs`, `getTransport`, and `Execute`. `rootCmd` advertises `common.Blobfuse2Version` and returns a mount suggestion when invoked without a subcommand. `parseArgs` rewrites `os.Args` before Cobra sees them.

Control flow: `Execute` calls `parseArgs(os.Args)`, sets those args on `rootCmd`, executes Cobra, and exits with status 1 on errors. `parseArgs` strips the binary name, asks Cobra to resolve the command, injects `mount` for implicit fstab-style invocations that are not built-in Cobra commands, and splits `-o` comma lists into libfuse options versus blobfuse `--` options. Version checking starts a goroutine, validates the compiled version with `common.ParseVersion`, checks raw GitHub sentinel files for warnings/blocked/latest state, prints warnings to stderr, and may `os.Exit(1)` for blocked versions.

State and persistence: global Cobra command and `disableVersionCheck` flag are process state. Version checks perform outbound HEAD requests and write to stderr/log. No local persistent files are changed.

Dependencies/integration: uses `common` constants/version parsing, `common/log`, Cobra, `net/http`, GitHub raw release metadata, environment-sensitive `http.DefaultTransport`, and `os.Args`.

Risks: version checking is network-dependent and can block command startup up to 8 seconds. `beginDetectNewVersion` can call `os.Exit`, which is hard to test and abrupt. `parseArgs` relies on string-prefix splitting of `-o` options and Cobra command discovery, so new commands or flag forms can affect mount injection.

Test signals: `root_test.go` covers missing command behavior, live sentinel URL checks, older-version detection, invalid URL handling, and fstab argument rewriting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/root.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/root_test.go -->
## sources/user-network-fs/blobfuse2/cmd/root_test.go

Purpose: validates top-level command behavior, version metadata probing, and fstab-style argument normalization.

Important APIs/helpers: `rootCmdSuite`, `osArgs`, `executeCommandC` from `mountv1_test.go`, `getDummyVersion`, and `cleanupTest`. Setup installs a silent logger; cleanup clears `rootCmd` output/error/args.

Control flow: tests execute `rootCmd` with no args and with `--disable-version-check`, expecting the missing command message. HTTP tests call `checkVersionExists` against invalid URLs and live `common.GitHubReleaseBaseURL` sentinel paths for security warnings, blocked versions, and absent latest metadata. `TestDetectNewVersionCurrentOlder` temporarily overrides `common.Blobfuse2Version`, reads from `beginDetectNewVersion`, and expects an upgrade message. `TestParseArgs` feeds synthetic `os.Args` strings through `parseArgs` and compares the normalized argument string.

State and persistence: mutates global `common.Blobfuse2Version` in one test and restores it. Uses global `rootCmd` and logger state. No persistent file outputs.

Dependencies/integration: depends on live internet access to raw GitHub metadata for several tests, so CI behavior may vary with network and metadata state. It also depends on Cobra command registrations from package init.

Risks: tests that assert remote sentinel files for version `1.1.1` are brittle if repository metadata changes or network calls fail. Channel receive from `beginDetectNewVersion` assumes the goroutine sends a value; a latest-version path with no send could deadlock if re-enabled incorrectly. Shared command state requires cleanup discipline.

Test signals: gives direct coverage of root argument compatibility for `/etc/fstab` forms and validates the newer raw-file version-check strategy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/root_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/secure.go -->
## sources/user-network-fs/blobfuse2/cmd/secure.go

Purpose: implements the `blobfuse2 secure` command group for encrypting and decrypting YAML config files with a user-provided AES passphrase.

Important APIs/types/functions: `secureOptions`, `SecureConfigEnvName`, `SecureConfigExtension`, global `secOpts`, `secureCmd`, `encryptCmd`, `decryptCmd`, `validateOptions`, `encryptConfigFile`, `decryptConfigFile`, `saveToFile`, and `init` command/flag registration.

Control flow: subcommands first call `validateOptions`, which fills `PassPhrase` from `BLOBFUSE2_SECURE_CONFIG_PASSPHRASE` if needed, requires a config path, checks file existence, and requires a passphrase. `encryptConfigFile` reads plaintext, calls `common.EncryptData`, and optionally writes the ciphertext to either `--output-file` or `$HOME/.blobfuse2/<basename>.azsec`; default encryption deletes the source. `decryptConfigFile` reads ciphertext, calls `common.DecryptData`, and optionally writes plaintext to either `--output-file` or a default path with the original extension stripped; default decryption does not delete the encrypted source. `saveToFile` writes mode `0777` and may remove `secOpts.ConfigFile`.

State and persistence: all options live in global `secOpts`, shared by secure subcommands. The command reads, writes, and sometimes deletes config files. Defaults use `common.DefaultWorkDir`, expanded with `common.ExpandPath` for encrypt and `os.ExpandEnv` for decrypt.

Dependencies/integration: Cobra, filesystem APIs, `common.EncryptData`/`DecryptData`, `common.DefaultWorkDir`, and env var passphrase support.

Risks: output files are world-writable (`0777`), risky for decrypted secrets. Default encrypt deletes the original file after write. Global `secOpts` can leak between tests/commands unless flags are reset. No key derivation is performed; the passphrase bytes must already be a valid AES key length.

Test signals: `secure_test.go` covers help, encrypt/decrypt round trips, missing config/key, nonexistent file, invalid key length, get, set, and invalid key lookup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/secure.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/secure_get.go -->
## sources/user-network-fs/blobfuse2/cmd/secure_get.go

Purpose: implements `blobfuse2 secure get`, which decrypts an encrypted config and prints the requested config key/value.

Important APIs/functions: global `getKeyCmd` with `RunE`; it uses `validateOptions`, `decryptConfigFile(false)`, Viper YAML loading, `viper.Get(secOpts.Key)`, and `reflect.TypeOf` classification.

Control flow: after validation, the command decrypts into memory without saving plaintext. It sets Viper's config type to YAML and reads the plaintext buffer. It then queries `secOpts.Key`. Missing keys return `key not found in config`. Existing values are classified as group-level maps, option-level slices, or scalar values, then printed as `<key> = <value>` to stdout.

State and persistence: reads encrypted config from disk and mutates global Viper state. It does not write files. It uses global `secOpts` populated by persistent secure flags and the `--key` flag.

Dependencies/integration: Cobra, Viper, reflection, string readers, and `secure.go` encryption helpers.

Risks: Viper global state can retain data across command invocations if tests or callers do not reset it. The type classification relies on `reflect.TypeOf(value).String()` prefixes rather than structured type checks. Output goes directly to process stdout rather than Cobra's command output writer, which makes capture less consistent.

Test signals: `secure_test.go` exercises successful scalar retrieval and missing-key error after encrypting a temporary config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/secure_get.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/secure_set.go -->
## sources/user-network-fs/blobfuse2/cmd/secure_set.go

Purpose: implements `blobfuse2 secure set`, updating a scalar value inside an encrypted config and rewriting the encrypted file.

Important APIs/functions: global `setKeyCmd` with `RunE`, `viper.Get`, `viper.Set`, `viper.AllSettings`, `yaml.Marshal`, `common.EncryptData`, and `saveToFile`.

Control flow: the command validates secure options, decrypts the current file into memory, reads it as YAML with Viper, checks the existing value for `secOpts.Key`, rejects map or slice values because only scalar edits are allowed, prints current/target values or an add-new-key message, sets the new value as a string, marshals all Viper settings back to YAML, encrypts the YAML with the same passphrase, and writes ciphertext over `secOpts.ConfigFile` without deleting it.

State and persistence: mutates global Viper and `secOpts`, and persistently rewrites the encrypted config file. YAML output is generated from `viper.AllSettings`, so formatting, key order, comments, and some original scalar types may not be preserved.

Dependencies/integration: Cobra, Viper, `gopkg.in/yaml.v2`, reflection, and `common.EncryptData`.

Risks: all set values are strings, even if the original scalar was boolean or numeric. Re-marshalling through Viper can normalize config shape and drop comments. Direct stdout printing bypasses Cobra output capture. The scalar check uses string prefixes from reflection rather than kind checks.

Test signals: `secure_test.go` covers a get/set/get flow for `logging.level`; it does not assert the changed value text or type preservation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/secure_set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/secure_test.go -->
## sources/user-network-fs/blobfuse2/cmd/secure_test.go

Purpose: provides regression coverage for secure config command registration and encryption/decryption/get/set behavior.

Important APIs/helpers: `secureConfigTestSuite`, `executeCommandSecure`, `resetSecureCLIFlags`, `testPlainTextConfig`, and `TestSecureConfig`. Tests invoke the real global `rootCmd` with secure subcommands and temporary files.

Control flow: setup installs a silent logger. Tests cover help, encrypting to a provided output file, nonexistent config, missing config, missing passphrase, invalid AES key length, decrypting a previously encrypted config to `./tmp.yaml`, getting an existing key, getting an invalid key, and setting `logging.level` before getting it again. Temporary config files are removed with defers.

State and persistence: tests write plaintext and encrypted temporary files and one fixed `./tmp.yaml` file. They mutate global Cobra command args/outputs and secure flags. Cleanup currently resets `generateConfigCmd` flags, which appears unrelated to secure flags and may leave some secure flag state to Cobra's own test execution behavior.

Dependencies/integration: uses actual `common.EncryptData`/`DecryptData`, filesystem temp files, Cobra command execution, and global Viper behavior inside secure get/set.

Risks: fixed `./tmp.yaml` can collide if tests run concurrently or fail before cleanup. The flag reset helper targets `generateConfigCmd`, not `secureCmd`/subcommands, which is a maintainability hazard. Output from `secure get/set` uses stdout, but tests mostly assert only error/no-error rather than exact output or final decrypted value.

Test signals: confirms valid AES key length, passphrase requirement, round-trip byte equality for decrypt, and scalar update command path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/secure_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/unmount.go -->
## sources/user-network-fs/blobfuse2/cmd/unmount.go

Purpose: implements `blobfuse2 unmount <mount path>` with exact path, wildcard path, lazy unmount, and shell completion support.

Important APIs/functions: global `unmountCmd`, `unmountBlobfuse2`, and `init` registration of the `--lazy/-z` persistent flag plus `umntAllCmd`.

Control flow: the command requires one argument and reads the `lazy` flag. If the path contains `*`, it treats the argument as a regexp pattern, lists blobfuse mount points with `common.ListMountPoints`, and unmounts matches. Otherwise it unmounts the given path. `unmountBlobfuse2` tries `fusermount3` then `fusermount`, adds `-z` for lazy mode, runs `-u <path>`, logs and prints success, and returns the stderr plus exec error on failure. It only tries the second binary when the previous error says the executable was not found.

State and persistence: changes OS mount state. It does not persist local files. It writes user-visible success to stdout unless `silent` is true and logs success/failure.

Dependencies/integration: Cobra, `common.ListMountPoints`, `fusermount3`/`fusermount`, regexp matching, and the logger.

Risks: wildcard matching passes the user path directly to `regexp.MatchString`; literal paths containing regex metacharacters can match unexpectedly. The shared `errb` buffer is not reset between binary attempts. Error detection depends on the text `executable file not found`. Mount listing is Linux `/etc/mtab` based.

Test signals: `unmount_test.go` mounts loopbackfs instances with the built binary and checks normal, busy, wildcard, completion, lazy, and invalid mount flag behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/unmount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/unmount_all.go -->
## sources/user-network-fs/blobfuse2/cmd/unmount_all.go

Purpose: implements `blobfuse2 unmount all`, which enumerates all blobfuse2 mounts and attempts to unmount each one.

Important APIs/functions: global `umntAllCmd` with its `RunE`, using `common.ListMountPoints`, `unmountBlobfuse2`, and the inherited `lazy` flag from `unmountCmd`.

Control flow: the command reads the lazy flag, lists mount points, and initializes counters plus an aggregate error message. It increments `mountfound` for each mount, calls `unmountBlobfuse2`, increments `unmounted` on success, and appends per-mount error details on failure. If no mounts are found it prints `Nothing to unmount`; otherwise it prints a success count. Any partial failure returns a combined error.

State and persistence: changes OS mount state and emits stdout. No local files are written.

Dependencies/integration: Linux mount-table parsing through `common.ListMountPoints`, the unmount helper in `unmount.go`, Cobra subcommand registration, and process-level fusermount commands.

Risks: a failure on one mount does not stop attempts for later mounts, which is good operationally, but errors are plain string aggregation without structured detail. Behavior depends on `common.ListMountPoints` only returning lines prefixed by `blobfuse2`. The command assumes inherited flag lookup succeeds.

Test signals: direct coverage is mostly through `util_test.go` calling `../blobfuse2 unmount all` and `unmount_test.go` covering inherited lazy behavior through the parent command.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/unmount_all.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/unmount_test.go -->
## sources/user-network-fs/blobfuse2/cmd/unmount_test.go

Purpose: integration-oriented tests for mounting loopbackfs and unmounting via the Cobra command paths.

Important APIs/helpers: `unmountTestSuite`, `configUnMountLoopback`, `confFileUnMntTest`, `currentDir`, `SetupTest`, `cleanupTest`, and `TestUnMountCommand`. Tests use `executeCommandC` and reset root/mount/unmount flags.

Control flow: `TestUnMountCommand` creates a temporary loopback config and backing directory, then runs the suite. Individual tests invoke `../blobfuse2 mount`, wait, and then exercise `rootCmd unmount`: normal unmount, busy-directory failure followed by success after leaving the directory, wildcard unmount success/failure, shell completion returning mount points, lazy unmount through both `--lazy` and `-z` before/after the path, and unknown mount flags.

State and persistence: creates temporary mount directories, a temp config file, changes process working directory in busy-mount cases, and mutates real FUSE mount state through the built `../blobfuse2` binary. Sleeps are used to wait for mount/unmount state.

Dependencies/integration: requires a built binary at `../blobfuse2`, functioning FUSE/loopbackfs environment, fusermount tools, `/etc/mtab`, and permissions allowing mounts. Uses silent logger.

Risks: slow and environment-sensitive; CI without FUSE support or the expected binary will fail. Working-directory changes can leak if an assertion aborts before cleanup. Time-based waits can be flaky. Tests use global command state and flags.

Test signals: strong end-to-end coverage for unmount semantics, including lazy unmount and busy mount failure behavior, but it is not a pure unit test suite.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/unmount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/version.go -->
## sources/user-network-fs/blobfuse2/cmd/version.go

Purpose: implements `blobfuse2 version`, printing the current version and optionally checking remote release metadata.

Important APIs/functions: global `check` flag and `versionCmd`. `init` registers the command under `rootCmd` and adds `--check`.

Control flow: when executed, the command prints `blobfuse2 version: <common.Blobfuse2Version>`. If `--check` was supplied, it calls `VersionCheck()` from `root.go`; otherwise it returns nil.

State and persistence: reads the global version string and global `check` flag. It writes to stdout and may perform network I/O through `VersionCheck`. No files are changed.

Dependencies/integration: Cobra command tree, `common.Blobfuse2Version`, and root version-check helpers. The command participates in `parseArgs` handling from `root.go`, including normal CLI use and `--version`.

Risks: the global `check` variable is process state, so tests or repeated command execution must reset flags. With `--check`, command latency and success depend on the remote sentinel files and network availability.

Test signals: `root_test.go` includes parse-args cases for `version` and `version --check=true`; direct execution of `versionCmd` is not separately asserted in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/cache_policy/lru_policy.go -->
## sources/user-network-fs/blobfuse2/common/cache_policy/lru_policy.go

Purpose: provides an LRU cache for `common.Block` objects used by block-oriented cache flows.

Important APIs/types/functions: `KeyPair`, `LRUCache`, `NewLRUCache`, `Get`, `Resize`, `Put`, `Keys`, `RecentlyUsed`, `LeastRecentlyUsed`, `Remove`, `Purge`, `getKeyPair`, and `evict`.

Control flow: `Put` evicts one clean least-recently-used block when `Occupied >= Capacity`, then pushes a new list element to the front and records its pointer in `Elements`. `Get` finds a block, moves it to the front, and returns it. `Resize` updates `EndIndex` and adjusts `Occupied` by the size delta. `Remove` locks the block, adjusts occupancy, clears data, deletes map entry, and removes the list node. `evict` walks from the back toward the front until it finds a non-dirty block; dirty blocks are skipped.

State and persistence: all state is in memory: doubly linked list, map, capacity, occupied byte count, and block mutation (`Data = nil`, flags consulted). The struct embeds `sync.RWMutex`, but exported methods do not acquire the cache-level lock.

Dependencies/integration: depends on `container/list`, `common.Block` and its `Dirty`/lock behavior, and `common/log` for `Print`.

Risks: the unusual list storage wraps a manually allocated `*list.Element` inside the list's element; callers must use `getKeyPair`. Cache-level concurrency is not actually protected despite the embedded mutex. `Put` only evicts before insertion and may allow `Occupied` to exceed `Capacity`, especially for large blocks. `RecentlyUsed`/`LeastRecentlyUsed` panic on empty cache.

Test signals: `lru_policy_test.go` covers construction, put/get, purge, resize, LRU ordering, clean eviction, and dirty-block eviction refusal/selection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/cache_policy/lru_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/cache_policy/lru_policy_test.go -->
## sources/user-network-fs/blobfuse2/common/cache_policy/lru_policy_test.go

Purpose: unit tests for the `LRUCache` behavior in `lru_policy.go`.

Important APIs/helpers: `typesTestSuite`, `assertBlockCached`, `assertBlockNotCached`, and tests for construction, put, purge, not-found, resize, ordering, eviction, and dirty-block eviction.

Control flow: tests create small `common.Block` instances with start/end index ranges, insert them into caches of limited capacity, call `Get` to update recency, and assert `RecentlyUsed`, `LeastRecentlyUsed`, `Keys`, and `Occupied`. Dirty-block tests set and clear `common.DirtyBlock` flags to verify `Put` refuses insertion when all candidates are dirty, then evicts the clean candidate after flags are cleared.

State and persistence: tests are in-memory only. They mutate `Block.Flags` and cache internals but do not touch filesystem or external services.

Dependencies/integration: depends on `common.Block`, `common.BitMap64`, and testify suite/assert.

Risks: the suite does not exercise cache-level concurrent access despite `LRUCache` embedding `sync.RWMutex`. It does not cover duplicate keys, empty `RecentlyUsed`/`LeastRecentlyUsed`, oversized single-block insertion beyond capacity, or nil block values. Test suite type is named `typesTestSuite`, which can be confusing in the cache package.

Test signals: strong behavioral signal for current eviction policy: capacity is a trigger threshold, not a hard post-insertion limit, and dirty blocks are protected from eviction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/cache_policy/lru_policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/config/config_parser.go -->
## sources/user-network-fs/blobfuse2/common/config/config_parser.go

Purpose: central configuration wrapper around Viper that enforces blobfuse precedence: flags, environment variables, then config file.

Important APIs/types/functions: `ConfigChangeEventHandler`, `ConfigChangeEventHandlerFunc`, `KeysTree`, internal `options`/`userOptions`, `SetSecureConfigOptions`, `SetConfigFile`, `ReadFromConfigFile`, `ReadFromConfigBuffer`, `DecryptConfigFile`, `WatchConfig`, `ReadConfigFromReader`, `AddConfigChangeEventListener`, `BindEnv`, `BindPFlag`, `UnmarshalKey`, `Unmarshal`, `Set`, `SetBool`, `IsSet`, flag creation helpers, `RegisterFlagCompletionFunc`, and `ResetConfig`.

Control flow: config files or buffers are loaded into global Viper, then `WatchConfig` installs an fsnotify callback. `Unmarshal`/`UnmarshalKey` first decode Viper data with the `config` struct tag, then overlay environment values from `envTree`, then changed flags from `flagTree`. Secure configs are decrypted on file-change events before notifying listeners. Flag helpers add options to a shared pflag set that can be attached to Cobra commands.

State and persistence: `userOptions` and Viper are global mutable state. `DecryptConfigFile` reads encrypted files and loads plaintext into Viper but does not write. Watchers/listeners persist for process lifetime unless `ResetConfig` is called.

Dependencies/integration: Viper, pflag, Cobra completions, fsnotify, mapstructure, `common.EncryptData`/`DecryptData`, and `common/log`.

Risks: `IsSet` walks `flagTree` and assumes the final node value is a `*pflag.Flag`, which can panic for malformed intermediate state. `ResetConfig` omits reinitializing `completionFuncMap`, unlike `init`, so registering completions after reset can panic unless another initializer restores it. Viper global state and watchers make tests and command reuse sensitive to cleanup.

Test signals: `config_test.go` covers config-only decode, env shadowing, flag shadowing, flag-over-env precedence, flag helper creation, and encrypted config loading.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/config/config_parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/config/config_test.go -->
## sources/user-network-fs/blobfuse2/common/config/config_test.go

Purpose: verifies the configuration parser's unmarshalling, nested-key behavior, env/flag precedence, flag creation helpers, and encrypted config loading.

Important APIs/types: local nested structs `Labels`, `Metadata`, `Selector`, `Template`, `Spec`, `Config1`, `Config2`; fixtures `config1`, `config2`, `metaconf`, `specconf`; and `ConfigTestSuite`.

Control flow: tests load YAML from readers, call `Unmarshal` and `UnmarshalKey` for root and nested subtrees, bind environment variables with `BindEnv`, bind changed pflags with `BindPFlag`, and verify precedence. `TestOverlapShadowConfigReader` demonstrates flags winning over env for the same key while env overrides config for another key. `TestAddFlags` calls all typed flag helper functions and basic setters. `TestConfigFileDecryption` writes a plaintext config, encrypts it with `common.EncryptData`, writes ciphertext, and loads it with `DecryptConfigFile`.

State and persistence: uses global Viper and `userOptions`; cleanup calls `ResetConfig`. Some tests set environment variables but do not explicitly unset them, relying on unique names and later process state not caring. Encryption test writes `test.yaml` and `test_enc.yaml` in the working directory and removes them.

Dependencies/integration: testify, Viper wrapper APIs, pflag, environment variables, filesystem, and AES-GCM utilities.

Risks: `TestAddFlags` passes untyped `5.0` constants to integer helpers; this compiles because constants are representable, but it is visually misleading. Environment variables can leak across tests. The suite does not cover config watchers/listener callbacks or `RegisterFlagCompletionFunc` after `ResetConfig`.

Test signals: strong signal for intended precedence and nested `config` tag mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/config/keys_tree.go -->
## sources/user-network-fs/blobfuse2/common/config/keys_tree.go

Purpose: implements a dot-key tree used by the config layer to map env vars and flags onto nested config structs after Viper unmarshalling.

Important APIs/types/functions: `STRUCT_TAG`, `TreeNode`, `Tree`, `NewTree`, `NewTreeNode`, `Insert`, `Print`, `GetSubTree`, `parseValue`, `MergeWithKey`, `Merge`, `isPrimitiveType`, `assignToField`, and `getIdxFromField`.

Control flow: `Insert` splits keys on `.` and creates child nodes down to the leaf value. `Merge` starts at root and recursively overlays matching tree values onto struct fields; `MergeWithKey` does the same for a subtree. Field names come from the `config` tag or lowercased field name. For struct fields it recurses; for pointer fields it recurses into `Elem`; for primitives it calls `getValue`, parses string values into the target kind when needed, and sets the field.

State and persistence: all state is in-memory tree nodes storing arbitrary values, typically env var names or pflag pointers. No persistence.

Dependencies/integration: reflection, strconv parsing, and config parser merge callbacks.

Risks: pointer handling assumes non-nil pointers and can panic on nil pointer fields. `assignToField` silently ignores unparseable string values. `parseValue` uses bit sizes matching target kinds, but `int`/`uint` use bit size 0, which is platform-dependent. `Print` writes directly to stdout and is diagnostic only.

Test signals: `keys_tree_test.go` covers primitive parsing success/failure and primitive kind classification. Integration with `Merge` is covered indirectly by `config_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/config/keys_tree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/config/keys_tree_test.go -->
## sources/user-network-fs/blobfuse2/common/config/keys_tree_test.go

Purpose: unit tests for the low-level parsing and primitive-kind helpers in `keys_tree.go`.

Important APIs/helpers: `keysTreeTestSuite`, `parseVal`, `TestParseValue`, `TestParseValueErr`, `TestIsPrimitiveType`, and `TestIsNotPrimitiveType`.

Control flow: `TestParseValue` iterates through strings representing booleans, signed/unsigned integers, floats, complex numbers, and strings, calling `parseValue` for each `reflect.Kind` and asserting the typed result. `TestParseValueErr` feeds non-parsable strings to all non-string primitive kinds and expects nil. The primitive tests assert the exact kinds considered primitive by `isPrimitiveType`.

State and persistence: no external state; pure in-memory tests.

Dependencies/integration: reflect, testify suite/assert, and the unexported helpers because the tests live in the same `config` package.

Risks: tests do not cover `Tree.Insert`, `GetSubTree`, `Merge`, `MergeWithKey`, struct tags, pointer fields, nil pointer behavior, or `assignToField` directly. Complex expected values are untyped constants and rely on `EqualValues`.

Test signals: confirms the accepted primitive surface and that parse failures return nil rather than errors, which is important because config overlay silently ignores invalid env/flag strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/config/keys_tree_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/exectime/exectime.go -->
## sources/user-network-fs/blobfuse2/common/exectime/exectime.go

Purpose: provides lightweight execution-time instrumentation with a package-level default timer.

Important APIs/types/functions: `Timer`, global `timer`, package functions `StatTimeCurrentBlock`, `PrintStats`, `TimeCurrentBlock`, `SwitchOnDebug`, `SwitchOffDebug`, `Start`, `Stop`, `New`, and `SetDefault`, plus matching methods on `Timer`.

Control flow: `TimeCurrentBlock` and `StatTimeCurrentBlock` return defer-friendly closures. When debug is enabled, the closure records elapsed time or pushes it into a `RunningStatistics` bucket; when disabled, it is a no-op. `PrintStats` writes a separator and per-key average/stddev/total/ops-per-sec. `Start` stores `time.Now()` by key and `Stop` writes elapsed time since that key. `init` defaults to stdout with debug enabled.

State and persistence: global mutable timer contains writer, debug flag, `timeMap`, and `statsMap`. No locking is used around maps, so concurrent instrumentation can race. Output is written to the configured writer but not otherwise persisted by this package.

Dependencies/integration: uses `RunningStatistics`, `io.Writer`, stdout, and `time`.

Risks: debug defaults to true, so instrumentation may write unexpectedly unless disabled. `Stop` on an unknown key uses zero `time.Time`, producing a huge duration. `PrintStats` divides by mean seconds; a zero-duration mean can create invalid rates. Maps are not concurrency-safe.

Test signals: no dedicated tests in this subset; behavior is simple but concurrency and unknown-key cases are untested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/exectime/exectime.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/exectime/runningstats.go -->
## sources/user-network-fs/blobfuse2/common/exectime/runningstats.go

Purpose: implements online running mean, variance, and standard deviation for duration samples.

Important APIs/types/functions: `RunningStatistics`, `NewRunningStatistics`, `Push`, `Mean`, `Variance`, and `StandardDeviation`.

Control flow: `Push` increments sample count. The first sample initializes old/new mean and zero variance accumulator. Subsequent samples apply Welford-style update formulas for mean and sum of squared deviations using `time.Duration` arithmetic. `Variance` returns sample variance (`N-1` denominator) for at least two samples, otherwise zero. `StandardDeviation` converts variance to float64, square-roots it, and converts back to duration.

State and persistence: stores only counters and duration accumulators in memory. No synchronization; callers must serialize access if shared across goroutines.

Dependencies/integration: used by `exectime.Timer.StatTimeCurrentBlock` and `PrintStats`.

Risks: duration multiplication/subtraction can overflow for very large durations or many samples. Converting a duration variance to float64 and back loses precision. No tests cover numerical behavior in this subset.

Test signals: indirect only through any manual use of `exectime`; no unit tests here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/exectime/runningstats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/lock_map.go -->
## sources/user-network-fs/blobfuse2/common/lock_map.go

Purpose: provides a keyed lock registry for file-level exclusive locking, handle counts, and download timestamps.

Important APIs/types/functions: `LockMapItem`, `LockMap`, `NewLockMap`, `Get`, `Delete`, `Locked`, and item methods `Lock`, `Unlock`, `Inc`, `Dec`, `Count`, `SetDownloadTime`, `DownloadTime`.

Control flow: `LockMap.Get` uses `sync.Map.LoadOrStore` to return an existing or new `LockMapItem` for a name. `Lock` acquires the item mutex and marks `exLocked`; `Unlock` clears the flag then releases the mutex. `Inc`/`Dec` adjust `handleCount`, and timestamp methods write/read `downloadTime`.

State and persistence: all state is in memory. `sync.Map` protects map operations, and the item mutex protects the lock critical section, but `handleCount`, `exLocked`, and `downloadTime` are read/written without consistent locking outside `Lock`/`Unlock`.

Dependencies/integration: standard `sync` and `time`; likely used by filesystem/cache components to coordinate per-path operations.

Risks: `Locked`, `Inc`, `Dec`, `Count`, and timestamp methods are not concurrency-safe relative to each other. `Dec` can underflow the uint32 count. `Delete` can remove an item while callers still hold references. No tests are present in this subset.

Test signals: absent direct tests; concurrency semantics need review in callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/lock_map.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/log/base_logger.go -->
## sources/user-network-fs/blobfuse2/common/log/base_logger.go

Purpose: implements asynchronous file/stdout logging with log levels and size-based rotation.

Important APIs/types/functions: `LogFileConfig`, `BaseLogger`, `newBaseLogger`, getter methods, level methods `Debug`/`Trace`/`Info`/`Warn`/`Err`/`Crit`, setters, `init`, `Destroy`, `logEvent`, `logDumper`, and `LogRotate`.

Control flow: initialization sets defaults for log file, level, size, and count, opens the file or stdout, creates a `log.Logger`, and starts a goroutine consuming a buffered channel of log strings. Each level method compares configured level and enqueues via `logEvent`, which formats timestamp, tag, pid, mount path, caller file/line, and optional goroutine ID. The dumper writes each message and triggers rotation when accumulated size exceeds the limit. Rotation closes the file, deletes the oldest numbered file, renames numbered files upward, renames current to `.1`, and opens a new file.

State and persistence: persists log files and rotated backups. Maintains current log size, file handle, logger, pid, channel, and worker wait group. `Destroy` closes the channel, waits, then closes the handle.

Dependencies/integration: `common.LogLevel`, `common.MountPath`, `common.GetGoroutineID`, filesystem, runtime caller info, and Go's `log` package.

Risks: channel buffer is large but sends can block under heavy logging. `SetLogFile` swaps file handles without closing the old one. `Destroy` closes stdout when logging to stdout. Rotation errors from remove/rename are ignored. Size accounting uses message length, not newline or actual bytes.

Test signals: `logger_test.go` stress logs enough messages to exercise rotation and `Destroy`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/log/base_logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/log/logger.go -->
## sources/user-network-fs/blobfuse2/common/log/logger.go

Purpose: exposes the package-level logging facade and logger factory used across blobfuse2.

Important APIs/types/functions: `Logger` interface, `NewLogger`, global `logObj`, global `timeTracker`, getters, `SetDefaultLogger`, `SetConfig`, setters, `Destroy`, level functions `Debug`/`Trace`/`Info`/`Warn`/`Err`/`Crit`, `LogRotate`, `TimeTrack`, and `TimeTrackDiff`.

Control flow: `NewLogger` chooses `base`, `silent`, or `syslog`/default. Syslog creation falls back to base logging only for `ErrNoSyslogService`. `SetDefaultLogger` replaces global `logObj`. `SetConfig` mutates the current logger's file, level, max size, count, and time tracking. Package-level level functions delegate directly to `logObj`. `init` defaults to syslog with debug level, falling back internally if needed.

State and persistence: global logger instance and time-tracker flag are mutable process state. Depending on logger type, output may go to syslog, files, stdout, or nowhere.

Dependencies/integration: `BaseLogger`, `SilentLogger`, `SysLogger`, `common.LogConfig`, and `time`.

Risks: package-level logging functions panic if `logObj` is nil, though init normally sets it. Replacing loggers does not automatically destroy the previous logger. `SetConfig` on syslog silently ignores file/size/count settings. Time tracking logs at critical level, which may be surprising.

Test signals: `logger_test.go` covers base, silent, syslog/fallback, invalid logger type, level changes, and high-volume logging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/log/logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/log/logger_test.go -->
## sources/user-network-fs/blobfuse2/common/log/logger_test.go

Purpose: validates the logger factory/facade across base, silent, syslog, and invalid logger types.

Important APIs/helpers: `LoggerTestSuite`, `fastTestDebug`, `fastTestCrit`, `simpleTest`, and suite tests `TestBaseLogger`, `TestSilentLogger`, `TestSysLogger`, `TestNegative`.

Control flow: `simpleTest` cycles through debug/info/warning levels and emits all severity methods. `TestBaseLogger` configures file logging to `./logfile.txt`, runs simple logging, emits 100k debug lines then 100k critical lines to drive rotation, and calls `Destroy`. `TestSilentLogger` ensures no-op logging accepts calls. `TestSysLogger` requests syslog at debug level and accepts factory fallback if syslog is unavailable. `TestNegative` expects an invalid type error.

State and persistence: writes `./logfile.txt` and rotated logs but does not remove them. Mutates package-global `logObj` and `timeTracker`.

Dependencies/integration: syslog availability, filesystem write permissions, asynchronous base logger goroutine, and testify.

Risks: high-volume logging makes the test relatively expensive. Leftover log files can dirty working directories. Syslog behavior may differ across platforms, but factory fallback avoids failing when service is absent. No assertions inspect log contents or rotation file count.

Test signals: confirms factory selection and that the async logger can survive large message volume plus destruction without returning errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/log/logger_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/log/silent_logger.go -->
## sources/user-network-fs/blobfuse2/common/log/silent_logger.go

Purpose: implements a no-op logger that satisfies the `Logger` interface for tests or intentionally silent operation.

Important APIs/types/functions: `SilentLogger` and its methods `GetLoggerObj`, `GetType`, `GetLogLevel`, all severity methods, `LogRotate`, `Destroy`, and configuration setters.

Control flow: every logging/configuration method either returns a static value or does nothing. `GetType` returns `silent`, `GetLogLevel` returns `LOG_OFF`, `GetLoggerObj` returns nil, and error-returning methods return nil.

State and persistence: no state and no persistence.

Dependencies/integration: satisfies the `Logger` interface from `logger.go` and uses `common.LogLevel` constants.

Risks: callers that assume `GetLoggerObj()` is non-nil can panic when using silent logging. Configuration setters silently discard changes, which is intended but can hide mistaken logger selection.

Test signals: `logger_test.go` calls logging methods through the facade after selecting the silent logger and expects no error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/log/silent_logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/log/sys_logger.go -->
## sources/user-network-fs/blobfuse2/common/log/sys_logger.go

Purpose: implements syslog-backed logging for production/default logging paths.

Important APIs/types/functions: `SysLogger`, `ErrNoSyslogService`, `newSysLogger`, getters/setters, `init`, `getSyslogLevel`, `write`, severity methods, and no-op file/rotation methods.

Control flow: construction creates a syslog writer with a priority mapped from blobfuse log level and wraps it in a standard logger. Severity methods compare configured level and call `write`, which formats optional goroutine ID, mount path, severity, caller file/line, and message. `SetLogLevel` updates level and emits a critical reset message. File-oriented methods are no-ops because syslog manages persistence.

State and persistence: holds level, tag, goroutine-ID option, and syslog logger. Log records persist according to the host syslog service.

Dependencies/integration: Unix syslog, `common.LogLevel`, `common.MountPath`, `common.GetGoroutineID`, runtime caller info, and package factory fallback in `logger.go`.

Risks: syslog may be unavailable in containers or non-Unix environments; factory fallback handles only `ErrNoSyslogService`. The syslog priority is fixed at writer construction, so changing `level` later changes filtering but not the writer's facility/priority. Destroy/rotation do nothing.

Test signals: `logger_test.go` requests syslog and runs generic log calls, but it does not inspect syslog output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/log/sys_logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/types.go -->
## sources/user-network-fs/blobfuse2/common/types.go

Purpose: defines common constants, log-level enum, logging config, block metadata structures, block-list helpers, UUID/block-id helpers, and default path initialization.

Important APIs/types/functions: version/default constants, `FuseIgnoredFlags`, `Blobfuse2Version`, `DefaultWorkDir`, `LogLevel` and `ELogLevel`, `LogConfig`, block flags, `Block`, `Dirty`, `Truncated`, `BlockOffsetList`, `BinarySearch`, `FindBlocks`, `FindBlocksToModify`, `uuid`, `NewUUIDWithLength`, `NewUUID`, `GetBlockID`, `GetIdLength`, and `azureSpecialContainers`.

Control flow: log levels are enum-style methods over `LogLevel` with string parsing through `github.com/JeffreyRichter/enum`. Block helpers search sorted block ranges, mark dirty blocks that overlap write ranges, report append-only and larger-than-file cases, and validate file size against the last block end. UUID helpers generate random bytes and set RFC4122 version/variant bits before base64 encoding block IDs. `init` derives default work/log/stats paths from `$HOME` or `./`.

State and persistence: package globals hold version, default paths, monitoring flags, pipes, and mount path. Block helpers mutate block flags. No direct persistence.

Dependencies/integration: used broadly by logging, config, cache, mount, storage, and utility code.

Risks: `FindBlocks` and `FindBlocksToModify` assume sorted non-overlapping blocks. `FindBlocksToModify` can panic on empty `BlockList` when a found path later references the last element, though no-found append case returns earlier. `Blobfuse2Version` is mutable, which aids tests but can affect runtime if changed. Random UUID errors are ignored.

Test signals: `types_test.go` covers binary search, block modification calculations, append-only detection, and default path initialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/types_test.go -->
## sources/user-network-fs/blobfuse2/common/types_test.go

Purpose: unit tests for common block-list behavior and default path initialization.

Important APIs/helpers: `typesTestSuite`, `TestBinarySearch`, `TestFindBlocksToModify`, and `TestDefaultWorkDir`.

Control flow: tests build a three-block `BlockOffsetList`, assert binary search finds offsets inside blocks and returns insertion position for offsets beyond the list, and assert `FindBlocksToModify` returns expected first index, modified size, larger-than-file flag, and append-only flag for overlapping and append ranges. Default path test compares `DefaultWorkDir`, `DefaultLogFilePath`, and `StatsConfigFilePath` with `os.UserHomeDir()`.

State and persistence: no files are written. Tests rely on package init having already derived defaults from the environment.

Dependencies/integration: `os.UserHomeDir`, filepath, testify.

Risks: test package uses the same suite type name `typesTestSuite` as some other packages, harmless but confusing. It does not assert dirty flags after `FindBlocksToModify`, `FindBlocks`, validation helpers, UUID/block ID helpers, or log-level parsing.

Test signals: gives focused coverage for write-range calculations that are important to block-cache modification flows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/types_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/util.go -->
## sources/user-network-fs/blobfuse2/common/util.go

Purpose: collects cross-cutting utilities for mount detection, filesystem cleanup, encryption, path expansion, disk usage, checksums, pipeline validation, flag formatting, and goroutine IDs.

Important APIs/functions: mount helpers `IsDirectoryMounted`, `IsMountActive`, `ListMountPoints`; filesystem helpers `IsDirectoryEmpty`, `TempCacheCleanup`, `DirectoryExists`, `WriteToFile`; identity/path helpers `GetCurrentUser`, `NormalizeObjectName`, `ExpandPath`, `NotifyMountToParent`; crypto/checksum helpers `EncryptData`, `DecryptData`, `GetCRC64`, `GetMD5`; system helpers `GetCurrentDistro`, `GetUsage`, `GetFuseMinorVersion`; concurrency helpers `BitMap64`, `KeyedMutex`, `GetGoroutineID`; pipeline helpers `ComponentInPipeline`, `ValidatePipeline`, `UpdatePipeline`, and `PrettyOpenFlags`.

Control flow: mount functions parse `/etc/mtab`, call `pidof`/`ps`, or shell out to system tools. AES-GCM helpers use the raw passphrase bytes as the AES key, prepend nonce to ciphertext, and split nonce/ciphertext on decrypt. `ExpandPath` handles `~/`, environment expansion, preserves Azure special `$web`/`$logs`/`$changefeed`, and returns an absolute path. `BitMap64` uses atomic CAS loops. Pipeline validation rejects mutually exclusive cache/xload components; update swaps cache components with xload/block-cache.

State and persistence: global booleans `RootMount`, `ForegroundMount`, `IsStream`, selected `du` path cache, and monitoring globals are mutated/read. Utilities may delete directory contents, write files, signal parent processes, or read system files.

Dependencies/integration: Linux `/etc/mtab`, `pidof`, `ps`, `du`, `fusermount3`, `/etc/os-release`, AES, CRC64/MD5, goid, ini parser, and syscall signals.

Risks: `DecryptData` slices `cipherData` before checking length, so too-short ciphertext can panic. `IsMountActive` uses substring matching on command line args, which can false-positive. `WriteToFile` defaults to `0777`. `UpdatePipeline` does not append missing components except replacement cases. Many helpers are Linux-specific.

Test signals: `util_test.go` covers atomic bitmap behavior, mount-active integration, directory existence/cleanup, encryption errors and round trip, path expansion, disk usage, checksums, pipeline validation/update, open flag formatting, goroutine ID behavior, and `SetFrsize`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/util_32.go -->
## sources/user-network-fs/blobfuse2/common/util_32.go

Purpose: provides ARM 32-bit-specific assignment for `syscall.Statfs_t.Frsize`.

Important API/function: `SetFrsize(st *syscall.Statfs_t, v uint64)` under build tag `arm`.

Control flow: if the requested value exceeds `math.MaxInt32`, it clamps to `MaxInt32` to avoid silent truncation; otherwise it converts the value to `int32` and assigns `st.Frsize`.

State and persistence: mutates only the passed `Statfs_t` struct in memory.

Dependencies/integration: build tags, `math`, and `syscall`. This function shares the same public name as the 64-bit implementation, selected by architecture at build time.

Risks: only the ARM build uses this clamping behavior; callers relying on exact large values get saturation instead. The general `util_test.go` assertion expects `int64` field behavior and is primarily suited to 64-bit builds, so 32-bit-specific clamping needs separate architecture-aware coverage.

Test signals: indirect through `util_test.go TestSetFrsize` when tests run on an ARM 32-bit target, though that test only checks a small value.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/util_32.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/util_64.go -->
## sources/user-network-fs/blobfuse2/common/util_64.go

Purpose: provides 64-bit architecture assignment for `syscall.Statfs_t.Frsize`.

Important API/function: `SetFrsize(st *syscall.Statfs_t, v uint64)` under build tag `amd64 || arm64`.

Control flow: casts the provided `uint64` to `int64` and assigns it to `st.Frsize`.

State and persistence: mutates only the passed `Statfs_t` struct in memory.

Dependencies/integration: build tags and `syscall`. Selected for common 64-bit Linux targets used by blobfuse2.

Risks: very large `uint64` values above `math.MaxInt64` wrap when cast to `int64`; there is no clamp on 64-bit builds. This is probably acceptable for realistic filesystem fragment sizes but is not guarded.

Test signals: `util_test.go TestSetFrsize` validates assigning `4096` on the active 64-bit build.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/util_64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/util_test.go -->
## sources/user-network-fs/blobfuse2/common/util_test.go

Purpose: broad test coverage for common utility functions.

Important APIs/helpers: `utilTestSuite`, shared `randomString`, and tests for bitmaps, mount detection, directories, encryption, path expansion, usage, cleanup, file writing, checksums, FUSE version parsing, pipeline helpers, open flag formatting, goroutine IDs, and `SetFrsize`.

Control flow: tests exercise concurrent `BitMap64` operations, deterministic set/clear/reset semantics, shell out to `../blobfuse2` for mount-active cases, create temporary loopback mount configs, create/delete directories and files, encrypt/decrypt random data, expand multiple path forms including Azure special containers, measure disk usage after writing MB-sized files, and validate pipeline conflict rules.

State and persistence: creates directories under the user's home and working directory, writes `config.yaml`, `abc.txt`, `.blobfuse2/test_*.txt`, and temporary mount directories, changes working directory during mount tests, and invokes real mount/unmount commands.

Dependencies/integration: requires built `../blobfuse2`, FUSE support, `pidof`, `du`, `fusermount3`, home directory write access, and Linux system behavior.

Risks: environment-sensitive integration tests can fail without FUSE or the binary. Some tests use `typesTestSuite` receiver methods in this file, relying on another suite type in the same package, which is legal but surprising. File cleanup is mostly manual and can leave artifacts on assertion failure. `DecryptData` too-short ciphertext panic is not tested.

Test signals: strong mixed unit/integration signal for utility behavior and known external dependencies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/version.go -->
## sources/user-network-fs/blobfuse2/common/version.go

Purpose: parses and compares blobfuse2 version strings and defines release metadata URLs for warning/block/latest checks.

Important APIs/types/functions: `BlobFuse2WarningsURL`, `BlobFuse2BlockingURL`, `GitHubReleaseBaseURL`, `Version`, `ParseVersion`, `compare`, `OlderThan`, `NewerThan`, and `String`.

Control flow: `ParseVersion` accepts three-segment stable versions or four raw dot segments when the third segment includes `-` or `~` preview marker. It stores four numeric segments, marks preview versions, strips the prerelease marker from the patch segment, and parses numeric pieces. `compare` short-circuits identical original strings, compares major/minor/patch numerically, then treats GA as newer than preview and compares preview numeric segment when both are previews.

State and persistence: no mutable state in this file. Constants feed root version checks.

Dependencies/integration: used by `cmd/root.go` before version metadata checks and by tests. Release constants point to raw GitHub benchmark-branch sentinel files and aka.ms warning/blocking pages.

Risks: parser only models a subset of semantic versioning. Preview type names such as beta/alpha are ignored; different prerelease labels with the same numeric suffix can compare equal. The four-segment acceptance condition is tied to dots and marker placement. Comments still include a TODO about preview-vs-GA, although the code handles that case.

Test signals: `version_test.go` covers equality, superiority, and inferiority for stable, `-preview`, `~preview`, and beta-like strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/version_test.go -->
## sources/user-network-fs/blobfuse2/common/version_test.go

Purpose: validates `Version.compare` ordering for stable and prerelease version strings.

Important APIs/helpers: `versionTestSuite`, `TestVersionEquality`, `TestVersionSuperiority`, `TestVersionInferiority`, and `TestVersionTestSuite`.

Control flow: tests parse pairs of version strings and assert raw `compare` results. Equality covers identical stable, preview, beta, and tilde-preview forms. Superiority covers greater major/minor/patch, GA greater than preview, higher preview numeric suffix, and tilde/dash preview comparisons. Inferiority covers the inverse cases.

State and persistence: no external state or files.

Dependencies/integration: testify suite/assert and `ParseVersion`.

Risks: tests ignore parse errors by discarding them, so a future parser failure could lead to nil dereference rather than a clear parse assertion. They do not cover invalid strings, `OlderThan`, `NewerThan`, or `String` directly. Comparisons between different prerelease labels with the same numeric segment are not tested.

Test signals: confirms intended ordering semantics used by command version checking and release warnings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/common/version_test.go -->
