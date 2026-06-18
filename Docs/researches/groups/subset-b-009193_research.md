# subset-b-009193 research

Grouped research for the Syncthing config and connection files listed in work item `subset-b-009193`. Each source-file section is bounded by reconciliation markers and uses the original source path as its title.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/commit_test.go -->
## sources/sync-backup/syncthing/lib/config/commit_test.go

Purpose: Tests the `config.Wrapper` commit pipeline, especially validation rejection, subscriber commit notification, and restart-required propagation.

Important APIs/types/functions: `requiresRestart` implements both `Verifier` and `Committer`, returning `false` from `CommitConfiguration`; `validationError` rejects via `VerifyConfiguration`; `replace` wraps `Wrapper.Modify`; `TestReplaceCommit` exercises `RawCopy`, `Modify`, `Subscribe`, waiter synchronization, and `RequiresRestart`.

Control flow and state: A wrapper is started around an initial `Configuration{Version: 0}`. `Modify` queues replacement, `replaceLocked` prepares/migrates it to `CurrentVersion`, verifiers run before committers, and committers can set the atomic restart flag without blocking the config change. When a verifier returns an error, the config remains unchanged while any previous restart-required state remains set.

Dependencies and integration: Uses local test helpers from `config_test.go` (`wrap`, `testWrapper.stop`) and the production `Wrapper` interface. The test is a direct contract for consumers that subscribe to configuration changes.

Risks and test signals: The key risk is deadlock or partial state update in the config notification path. The test confirms waiter completion, verifier short-circuiting, and that restart-required is sticky after a subscriber requests it.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/commit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/compression.go -->
## sources/sync-backup/syncthing/lib/config/compression.go

Purpose: Defines the configuration-level compression enum and translates it to wire-protocol compression values.

Important APIs/types/functions: `Compression` has `CompressionMetadata`, `CompressionNever`, and `CompressionAlways`. `MarshalText` and `UnmarshalText` support XML/JSON text encoding; `ToProtocol` maps to `protocol.Compression`.

Control flow and state: The type is stateless. `UnmarshalText` uses a lookup table that preserves legacy `"true"` and `"false"` values; unknown text falls through to the zero value, `CompressionMetadata`. `MarshalText` emits the current canonical strings.

Dependencies and integration: Used by `DeviceConfiguration.Compression` and later by connection/protocol setup through `ToProtocol`. It depends only on `lib/protocol`.

Risks and test signals: Unknown inputs silently become metadata compression rather than erroring, which is compatibility-friendly but can hide typos. `compression_test.go` checks legacy and canonical text conversions.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/compression.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/compression_test.go -->
## sources/sync-backup/syncthing/lib/config/compression_test.go

Purpose: Verifies text marshal/unmarshal behavior for `Compression`.

Important APIs/types/functions: `TestCompressionMarshal` checks `Compression.UnmarshalText` and `Compression.MarshalText`.

Control flow and state: The test iterates legacy and current strings, expecting `"true"` to map to metadata and `"false"` to never. It also expects an arbitrary unknown string to map to `CompressionMetadata`, documenting the silent fallback behavior.

Dependencies and integration: Uses the production enum only, with no external services or filesystem state.

Risks and test signals: The test locks in backwards compatibility for old XML configs and catches regressions in canonical output strings (`never`, `metadata`, `always`).
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/compression_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/config.go -->
## sources/sync-backup/syncthing/lib/config/config.go

Purpose: Implements the core Syncthing configuration model, default construction, XML/JSON loading, XML writing, preparation, migration application, lookup/update helpers, and low-level normalization utilities.

Important APIs/types/functions: `Configuration`, `Defaults`, and `Ignores` are the root config structures. Public entry points include `New`, `ReadXML`, `ReadJSON`, `WriteXML`, `Copy`, `ProbeFreePorts`, `Device`, `DeviceMap`, `SetDevice(s)`, `Folder`, `FolderMap`, `FolderPasswords`, and `SetFolder(s)`. Internal helpers include `prepare`, `ensureMyDevice`, `prepareDeviceList`, `prepareFolders`, `prepareDevices`, `prepareIgnoredDevices`, `removeDeprecatedProtocols`, `applyMigrations`, duplicate filtering, untrusted-device share filtering, `filterURLSchemePrefix`, `getFreePort`, and tag-copy helpers.

Control flow and state: Loading sets struct defaults, decodes XML or JSON, applies per-item defaults for JSON folder/device arrays, then calls `prepare`. Preparation ensures the local device is present unless the local ID is empty, removes empty or duplicate devices, validates folders for non-empty unique IDs and paths, removes folder-device references to unknown devices, adds the local device to folder shares, prunes ignored devices/folders that are now configured or shared, prepares GUI/options/defaults, strips deprecated KCP protocols, fills nil slices, and finally applies migrations to `CurrentVersion`. The config persists as indented XML plus a trailing newline.

Dependencies and integration: Integrates with `structutil` for defaults/nil filling, `protocol.DeviceID`, `fs` for marker cleanup, `netutil` for address formatting, `sliceutil`, `slog`, and migration functions. `Wrapper` uses this file for every persisted config replacement; connection code consumes prepared listen addresses, devices, folders, bandwidth options, and defaults.

Risks and test signals: Preparation mutates configuration substantially, so ordering is critical: options prepare before migrations is explicitly protected by `TestIssue1750`. Duplicate folders are fatal, duplicate devices are silently pruned, empty folder paths are fatal, deprecated schemes are removed by prefix, and migration globals are protected by a mutex. `config_test.go` covers defaults, legacy XML migration, JSON validation, copy semantics, ignored devices/folders, untrusted shares, URL filtering, and persistence round trips.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/config_test.go -->
## sources/sync-backup/syncthing/lib/config/config_test.go

Purpose: Broad integration and compatibility test suite for the `config` package.

Important APIs/types/functions: Defines stable test device IDs, a fake filesystem populated from `testdata`, helpers `copyAndLoad`, `loadTest`, `loadWrapTest`, `wrap`, `startWrapper`, and `defaultConfigAsMap`. Tests cover `New`, XML/JSON load paths, wrapper save/load, folder filesystem behavior, GUI URL/password/session behavior, migrations, duplicates, ignored remote state, ID validation, folder defaults, xattr filters, untrusted devices, and tag copying.

Control flow and state: The suite copies fixtures into a fake filesystem before load so migrations and save paths can mutate temporary data. Wrapper tests start `Serve` in a goroutine and stop it via context cancellation. Many tests compare fully prepared configs against expected structs, which validates both default filling and migration side effects.

Dependencies and integration: Uses `messagediff`, `bcrypt`, fake filesystems, `events.NoopLogger`, `protocol`, `build` platform flags, and the real wrapper service. It is the primary regression guard for `config.go`, `migrations.go`, enum marshalers, `folderconfiguration.go`, and XML fixtures.

Risks and test signals: Strong signals include `TestDeviceConfig` loading historical versions to `CurrentVersion`, duplicate-folder failure, empty-path failure, ignored-folder pruning, `ReadJSON` invalid ID rejection, `TestUntrustedIntroducer`, and `TestCopy` deep-copy behavior. Some behavior is platform-specific (`TestIssue1262`, Windows line endings), and `TestSharesRemovedOnDeviceRemoval` is skipped due to a known hang.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/copyrangemethod.go -->
## sources/sync-backup/syncthing/lib/config/copyrangemethod.go

Purpose: Defines user-facing configuration values for file clone/copy-range strategy and maps them to filesystem-layer strategies.

Important APIs/types/functions: `CopyRangeMethod` enum supports `standard`, `ioctl`, `copy_file_range`, `sendfile`, `duplicate_extents`, and `all`. Methods are `String`, `ToFS`, `MarshalText`, `UnmarshalText`, and `ParseDefault`.

Control flow and state: Stateless enum conversion. Unknown strings default to `CopyRangeMethodStandard`, and unknown enum values stringify as `unknown` while `ToFS` falls back to filesystem standard behavior.

Dependencies and integration: Used by `FolderConfiguration.CopyRangeMethod` and passed down to `lib/fs` copy/clone operations. `structutil` can call `ParseDefault` for default tags.

Risks and test signals: Silent fallback prevents config-load failures but may mask invalid settings. No direct test in this subset, but it is exercised indirectly through folder default loading and XML/JSON serialization.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/copyrangemethod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/debug.go -->
## sources/sync-backup/syncthing/lib/config/debug.go

Purpose: Provides the package-local logging adapter for configuration loading and saving.

Important APIs/types/functions: Declares package variable `l = slogutil.NewAdapter("Configuration loading and saving")`.

Control flow and state: No control flow; it initializes an adapter at package load time.

Dependencies and integration: Used by config files for debug logging in GUI/STUN handling, migration marker cleanup, wrapper save errors, and Android filesystem detection.

Risks and test signals: Minimal risk. Logging category stability matters for debug filtering; no direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/deviceconfiguration.go -->
## sources/sync-backup/syncthing/lib/config/deviceconfiguration.go

Purpose: Defines per-remote-device configuration and preparation logic.

Important APIs/types/functions: `DeviceConfiguration` includes identity, addresses, compression, introducer flags, bandwidth limits, ignored folders, request limits, untrusted mode, GUI port, connection count, and group. Methods/functions include `Copy`, `prepare`, `NumConnections`, `IgnoredFolder`, `Description`, and observed-folder dedup/sorting helpers.

Control flow and state: `prepare` normalizes empty addresses to `dynamic`, deduplicates ignored folders by newest timestamp, removes ignored folders that are now shared, and disallows untrusted devices from being introducers or auto-accepting folders. `NumConnections` maps zero to the package default of three, negative to one, and positive to itself.

Dependencies and integration: Depends on `protocol.DeviceID`, sorting, and structured logging. `Configuration.prepareDevices` supplies shared folder IDs so device ignored-folder state remains consistent with folder sharing.

Risks and test signals: Untrusted-device flag interactions are security-sensitive because they prevent trusted sharing and auto-accept behavior. Tests cover dynamic address defaults, ignored folder pruning, duplicate observed folders indirectly, and untrusted introducer sanitization.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/deviceconfiguration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/filesystemtype.go -->
## sources/sync-backup/syncthing/lib/config/filesystemtype.go

Purpose: Defines configuration-level filesystem type names and maps them to `lib/fs` filesystem types.

Important APIs/types/functions: `FilesystemType` string enum has `basic` and `fake`; methods are `ToFS`, `String`, `MarshalText`, `UnmarshalText`, and `ParseDefault`.

Control flow and state: Empty string is treated as `basic` for legacy compatibility in all conversion paths. Unknown non-empty strings pass through to `fs.FilesystemType`, allowing extension by the filesystem layer.

Dependencies and integration: Used by `FolderConfiguration.FilesystemType` and `VersioningConfiguration.FSType`; `FolderConfiguration.Filesystem` calls `ToFS`.

Risks and test signals: Pass-through unknown values can be useful for extensions but may fail later when creating a filesystem. Historical fixtures and folder path tests exercise legacy empty/basic behavior indirectly.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/filesystemtype.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/folderconfiguration.go -->
## sources/sync-backup/syncthing/lib/config/folderconfiguration.go

Purpose: Defines folder-level configuration, filesystem construction, marker management, path health checks, preparation rules, restart filtering, free-space checks, and extended-attribute filters.

Important APIs/types/functions: Key types are `FolderConfiguration`, `FolderDeviceConfiguration`, `XattrFilter`, and `XattrFilterEntry`. Important methods include `Copy`, `Filesystem`, `ModTimeWindow`, `CreateMarker`, `RemoveMarker`, `CheckPath`, `CreateRoot`, `Description`, `LogAttr`, `DeviceIDs`, `prepare`, `RequiresRestartOnly`, `Device`, `SharedWith`, `CheckAvailableSpace`, `XattrFilter.Permit`, and XML/JSON unmarshal methods that set defaults.

Control flow and state: `Filesystem` builds an `fs.Filesystem` with options for junction handling and case-conflict detection. Marker creation validates the path first, creates `.stfolder` plus a hashed marker file, syncs the root, and hides the marker. Preparation removes invalid/duplicate device shares, ensures the local device is shared, removes untrusted devices from trusted shares, sorts devices, clamps rescan and version cleanup intervals, normalizes watcher delay, defaults marker name and max concurrent writes, and forces `IgnorePerms` for receive-encrypted folders.

Dependencies and integration: Integrates with `lib/fs`, `protocol`, `build`, `disk.Usage` on Android, `structutil`, logging, and helpers in `config.go`. Puller/scanner/model code consumes these settings for filesystem access, scheduling, xattrs, versioning, and safety checks.

Risks and test signals: Marker and free-space checks guard data loss; untrusted-device filtering is security-sensitive; path validation rejects missing marker/root cases distinctly. Tests cover path health, large interval clamping, receive-encrypted ignore permissions, xattr filter semantics, versioning serialization, untrusted shares, and empty path rejection.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/folderconfiguration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/foldertype.go -->
## sources/sync-backup/syncthing/lib/config/foldertype.go

Purpose: Defines configuration text forms for Syncthing folder synchronization modes.

Important APIs/types/functions: `FolderType` wraps `protocol.FolderType` values for send-receive, send-only, receive-only, and receive-encrypted. It implements `String`, `MarshalText`, and `UnmarshalText`.

Control flow and state: Legacy strings `"readwrite"` and `"readonly"` map to send-receive and send-only. Unknown values default to send-receive.

Dependencies and integration: Used by `FolderConfiguration.Type`, log attributes, metrics labels, migrations from old read-only configs, and protocol behavior.

Risks and test signals: Silent fallback to send-receive can be permissive if a config typo occurs. Historical fixtures and config tests exercise read-only/read-write migration and receive-encrypted behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/foldertype.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/guiconfiguration.go -->
## sources/sync-backup/syncthing/lib/config/guiconfiguration.go

Purpose: Defines GUI/API server configuration and helpers for address overrides, auth, TLS, API keys, password hashing, and session-cookie path normalization.

Important APIs/types/functions: `GUIConfiguration` fields include enablement, address, Unix socket permissions, user/password/auth mode, metrics auth bypass, TLS, API key, host/frame security flags, theme, basic-auth prompt, and cookie settings. Methods include `IsAuthEnabled`, `IsOverridden`, `Address`, `UnixSocketPermissions`, `Network`, `UseTLS`, `URL`, `SetPassword`, `CompareHashedPassword`, `IsValidAPIKey`, `prepare`, and `Copy`.

Control flow and state: Environment variable `STGUIADDRESS` overrides stored address, network, and TLS interpretation; Unix schemes return path/network `unix`. `URL` rewrites wildcard TCP hosts to loopback for browser-safe URLs. `prepare` generates a random API key if missing and normalizes non-empty session cookie paths to start with `/`. Passwords are bcrypt-hashed unless they already match a bcrypt-hash regex.

Dependencies and integration: Uses `bcrypt`, `net/url`, environment variables, and `lib/rand`. Consumed by API server startup, authentication middleware, and config defaults.

Risks and test signals: Env overrides can change runtime behavior without persisted config changes. Security-sensitive areas are password hashing, API-key override acceptance, insecure flags, and metrics-without-auth. Tests cover URL rewriting, cookie path normalization, bcrypt hashing/comparison, and default GUI behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/guiconfiguration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/ldapconfiguration.go -->
## sources/sync-backup/syncthing/lib/config/ldapconfiguration.go

Purpose: Defines LDAP authentication configuration for the GUI.

Important APIs/types/functions: `LDAPConfiguration` contains server address, bind DN, transport, TLS verification skip flag, search base DN, and search filter. `Copy` returns the value unchanged.

Control flow and state: Pure data holder; defaults are supplied by `structutil` through struct tags when the root configuration is loaded or created.

Dependencies and integration: Used by `GUIConfiguration.AuthMode == AuthModeLDAP` and wrapper accessors. It depends on `LDAPTransport` for transport encoding.

Risks and test signals: `InsecureSkipVerify` is security-sensitive. There are no direct tests in this subset beyond default/copy behavior through configuration load and wrapper methods.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/ldapconfiguration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/ldaptransport.go -->
## sources/sync-backup/syncthing/lib/config/ldaptransport.go

Purpose: Encodes LDAP transport mode as text in configuration.

Important APIs/types/functions: `LDAPTransport` supports `plain`, `tls`, and `starttls`; methods are `String`, `MarshalText`, and `UnmarshalText`.

Control flow and state: Unknown text defaults to `LDAPTransportPlain`; unknown enum values stringify as `unknown`.

Dependencies and integration: Used by `LDAPConfiguration.Transport` and LDAP authentication setup outside this subset.

Risks and test signals: Defaulting unknown values to plain transport may be compatibility-friendly but less secure than failing closed. No direct tests here; configuration default tests cover struct initialization.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/ldaptransport.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/metrics.go -->
## sources/sync-backup/syncthing/lib/config/metrics.go

Purpose: Exposes static configuration information as Prometheus metrics.

Important APIs/types/functions: `RegisterInfoMetrics` registers collector funcs for `folderInfoMetric` and `folderDeviceMetric`. Descriptors emit `syncthing_config_folder_info` labels for folder ID/label/type/path/paused and `syncthing_config_device_info` labels for device ID/name/introducer/paused/untrusted.

Control flow and state: On collection, the metrics read current wrapper snapshots via `FolderList` and `DeviceList`, emitting gauge value `1` for each folder/device. Registration uses `prometheus.DefaultRegisterer.MustRegister`.

Dependencies and integration: Depends on Prometheus client and the `Wrapper` interface. It integrates config state with monitoring without persisting anything.

Risks and test signals: Label cardinality is proportional to configured folders/devices and includes folder paths/device names, which may expose sensitive metadata. `MustRegister` panics on duplicate registration. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/migrations.go -->
## sources/sync-backup/syncthing/lib/config/migrations.go

Purpose: Maintains ordered in-place migrations from older Syncthing config versions to `CurrentVersion`.

Important APIs/types/functions: `migrationSet`, `migration`, global `migrations`, and `migrationsMut`. `migrationSet.apply` sorts by target version, then `migration.apply` runs conversion when `cfg.Version` is below the target and updates the version. Specific migrations handle reconnect interval changes, max concurrent writes defaults, pending-device cleanup, junction defaults, notifications, crash reporting, watcher delays, versioning fields, filesystem type, marker upgrades, symlink cleanup, minimum disk free conversion, NAT/relay/listen address migration, discovery URLs, folder type migration, and old TCP address schema.

Control flow and state: Migrations mutate the passed `Configuration`. Some migrations are pure field rewrites; others touch filesystem state (`migrateToConfigV23` marker replacement and `migrateToConfigV21` symlink cleanup). Nil migration entries still advance version because external database migrations may key off config version.

Dependencies and integration: Called by `Configuration.prepare` under a mutex after defaults and option preparation. Uses `fs`, `netutil`, `upgrade`, environment variable `STNOUPGRADE`, URL/path helpers, logging, and build/runtime state. Fixtures `v5.xml`, `v22.xml`, `example.xml`, and targeted issue files exercise the chain.

Risks and test signals: Migration order and idempotence are high risk because every load of an old config depends on it. Filesystem-touching migrations must avoid data loss. Tests cover crash-reporting migration, reconnect interval migration, v14 listen/relay behavior, historical fixture migration, versioning parameter moves, and address trimming/order behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/migrations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/migrations_test.go -->
## sources/sync-backup/syncthing/lib/config/migrations_test.go

Purpose: Focused tests for selected migration behavior.

Important APIs/types/functions: `TestMigrateCrashReporting` applies the global migration set to version 28 configs. `TestMigrateReconnectInterval` applies version 52 migration behavior from version 51 inputs.

Control flow and state: Both tests lock `migrationsMut`, apply migrations in-place, and compare final option fields. Crash reporting becomes enabled if global discovery is enabled or usage reporting is accepted; reconnect interval is reduced to the minimum of the existing interval and the old QUIC interval formula.

Dependencies and integration: Exercises `migrations.apply` and option fields without loading XML fixtures.

Risks and test signals: These tests protect user-visible notification/reporting behavior and connection retry cadence changes across upgrades.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/migrations_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/mocks/mocked_wrapper.go -->
## sources/sync-backup/syncthing/lib/config/mocks/mocked_wrapper.go

Purpose: Generated counterfeiter fake for the `config.Wrapper` interface, used by tests in packages that need configurable wrapper behavior.

Important APIs/types/functions: Type `mocks.Wrapper` implements every method from `config.Wrapper`: config accessors, mutation methods, folder/device lookup/list methods, ignored state, lifecycle `Serve`, subscription methods, and `suture.Service`. For each method it provides a stub field, mutex-protected call recording, fixed return values, per-call returns, call-count accessors, args-for-call helpers where applicable, and `Invocations`.

Control flow and state: Each fake method locks its method mutex, records arguments, captures the current stub/return configuration, records the invocation under a shared invocation mutex, unlocks, then either calls the stub, returns a per-call value, or returns the default configured value. The final compile-time assertion ensures it satisfies `config.Wrapper`.

Dependencies and integration: Imports `context`, `sync`, `config`, and `protocol`. Regenerated from the `go:generate` directive in `wrapper.go`.

Risks and test signals: Because it is generated, manual edits are risky and will be overwritten. The fake’s locking supports concurrent tests, but returned slices/maps are whatever the test configures and are not deep-copied by the mock itself.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/mocks/mocked_wrapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/observed.go -->
## sources/sync-backup/syncthing/lib/config/observed.go

Purpose: Defines persisted observations of remote devices and folders that were ignored or pending historically.

Important APIs/types/functions: `ObservedFolder` stores time, folder ID, and label. `ObservedDevice` stores time, device ID, name, and address.

Control flow and state: Pure data structures with JSON/XML tags. They are persisted under device ignored folders and root ignored devices.

Dependencies and integration: Depends on `time.Time` and `protocol.DeviceID`. Used by `DeviceConfiguration.IgnoredFolders`, `Configuration.IgnoredDevices`, and deprecated pending fields.

Risks and test signals: Stale observed entries must be pruned when the device/folder is configured or shared. Tests `TestIgnoredDevices`, `TestIgnoredFolders`, and `TestIssue4219` validate that behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/observed.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/optionsconfiguration.go -->
## sources/sync-backup/syncthing/lib/config/optionsconfiguration.go

Purpose: Defines global Syncthing options and helper methods for defaults, normalization, derived network settings, concurrency limits, upgrade/reporting flags, and connection priorities.

Important APIs/types/functions: `OptionsConfiguration` includes listen/discovery/STUN settings, local/global announce flags, bandwidth limits, NAT/relay settings, usage/crash reporting, upgrades, temp/cache/progress settings, LAN-local nets, low priority, folder concurrency, request limits, feature flags, audit fields, connection limits, and connection priority fields. Methods include `Copy`, `prepare`, `RequiresRestartOnly`, `IsStunDisabled`, `ListenAddresses`, `StunServers`, `GlobalDiscoveryServers`, `MaxFolderConcurrency`, `MaxConcurrentIncomingRequestKiB`, `AutoUpgradeEnabled`, `FeatureFlag`, and `LowestConnectionLimit`.

Control flow and state: `prepare` fills nil slices, unique-trims listen and discovery servers, clamps reconnect interval to at least five seconds, removes the auth notification once GUI user/password is set, clamps negative connection limits to zero, keeps WAN priorities above LAN priorities, and generates a usage-reporting unique ID when needed. Derived address methods expand `"default"` placeholders into package defaults; STUN resolution performs DNS SRV lookup and appends shuffled fallback servers.

Dependencies and integration: Uses `runtime.GOMAXPROCS`, DNS, `protocol.MaxBlockSize`, `rand`, `stringutil`, and `structutil`. Connection services consume listen addresses, discovery, relays, bandwidth, LAN limit flags, connection limits, and priorities.

Risks and test signals: Network defaults and derived values affect reachability. DNS lookup in `StunServers` can vary at runtime. Tests cover overridden option values, max folder concurrency, migration interactions, and address/default behavior through fixtures.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/optionsconfiguration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/pullorder.go -->
## sources/sync-backup/syncthing/lib/config/pullorder.go

Purpose: Defines folder pull order configuration text values.

Important APIs/types/functions: `PullOrder` enum supports random, alphabetic, smallest-first, largest-first, oldest-first, and newest-first. It implements `String`, `MarshalText`, and `UnmarshalText`.

Control flow and state: Unknown text defaults to random. Unknown enum values stringify as `unknown`.

Dependencies and integration: Used by `FolderConfiguration.Order` to control file pull scheduling.

Risks and test signals: Invalid config silently becomes random. `TestPullOrder` loads all supported values plus an unknown value from `pullorder.xml`, then verifies XML round-trip preservation of supported values.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/pullorder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/size.go -->
## sources/sync-backup/syncthing/lib/config/size.go

Purpose: Represents user-configurable sizes and percentages, and checks free-space thresholds.

Important APIs/types/functions: `Size` has `Value` and `Unit`; functions/methods include `ParseSize`, `BaseValue`, `Percentage`, `String`, `ParseDefault`, `CheckFreeSpace`, internal `checkAvailableSpace`, and `formatSI`.

Control flow and state: Parsing trims whitespace, accepts decimal/comma numeric characters, then treats the remaining suffix as the unit. `BaseValue` multiplies by SI prefix k/m/g/t, and `Percentage` checks for `%` anywhere in the unit. Free-space checks compare either free percentage or absolute free bytes; `checkAvailableSpace` first reserves the requested bytes before checking the minimum.

Dependencies and integration: Uses `fs.Usage`. `FolderConfiguration.MinDiskFree`, `OptionsConfiguration.MinHomeDiskFree`, and folder free-space checks depend on it.

Risks and test signals: Negative values fail parse because `-` is not accepted in the numeric prefix. Prefix-plus-percent strings are accepted even if nonsensical. `size_test.go` covers parsing, defaults, SI formatting, and available-space checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/size.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/size_test.go -->
## sources/sync-backup/syncthing/lib/config/size_test.go

Purpose: Tests `Size` default parsing, size parsing, formatting, and free-space validation.

Important APIs/types/functions: `TestSizeDefaults`, `TestParseSize`, `TestFormatSI`, and `TestCheckAvailableSize`.

Control flow and state: Defaults are applied via `structutil.SetDefaults`. Parse cases cover upper/lower SI prefixes, fractions, unsupported negative numbers, arbitrary unit suffixes, percentages, empty strings, and plain numbers. Free-space cases check absolute and percentage thresholds after a simulated required allocation.

Dependencies and integration: Uses `fs.Usage` and `structutil`.

Risks and test signals: These tests document intentionally permissive units and intentionally rejected negatives, protecting disk safety behavior in folder and home free-space checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/size_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/deviceaddressesdynamic.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/deviceaddressesdynamic.xml

Purpose: XML fixture for dynamic/empty device address normalization.

Important data: Version 10 config with three devices: one with an empty `<address>`, one with no address elements, and one with explicit `dynamic`.

Control flow and state: When loaded, `DeviceConfiguration.prepare` converts empty or missing addresses to `[]string{"dynamic"}` and `Configuration.ensureMyDevice` can add the local device if absent.

Dependencies and integration: Used by `TestDeviceAddressesDynamic`.

Risks and test signals: Protects backward compatibility for legacy configs where empty address entries meant dynamic discovery.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/deviceaddressesdynamic.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/deviceaddressesstatic.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/deviceaddressesstatic.xml

Purpose: XML fixture for migration of legacy static device addresses.

Important data: Version 3 config with IPv4, IPv6, and host:port address forms lacking the modern `tcp://` scheme.

Control flow and state: Loading applies migrations that wrap non-dynamic legacy addresses with TCP URLs while preserving explicit ports and IPv6 bracket forms.

Dependencies and integration: Used by `TestDeviceAddressesStatic`.

Risks and test signals: Ensures old address syntax still reaches the current dialer/listener URI format.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/deviceaddressesstatic.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/devicecompression.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/devicecompression.xml

Purpose: XML fixture for legacy and current device compression text values.

Important data: Version 5 config with devices using `compression="true"`, `compression="metadata"`, and `compression="false"`.

Control flow and state: `Compression.UnmarshalText` maps true/metadata to metadata and false to never during XML load.

Dependencies and integration: Used by `TestDeviceCompression`.

Risks and test signals: Protects compatibility with pre-enum boolean compression settings.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/devicecompression.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/dupdevices.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/dupdevices.xml

Purpose: XML fixture for duplicate device and duplicate folder-device pruning.

Important data: Version 12 config repeats a device at the root and repeats that device inside folder `f2`.

Control flow and state: `prepareDeviceList` removes duplicate root devices and `ensureNoDuplicateFolderDevices` removes duplicate folder shares before sorting.

Dependencies and integration: Used by `TestDuplicateDevices`.

Risks and test signals: Confirms duplicate device entries are repaired silently while duplicate folders remain fatal.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/dupdevices.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/dupfolders.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/dupfolders.xml

Purpose: XML fixture for rejecting duplicate folder IDs.

Important data: Version 15 config declares folder `f1` twice.

Control flow and state: `prepareFolders` detects the duplicate folder ID and returns an error containing `errFolderIDDuplicate`.

Dependencies and integration: Used by `TestDuplicateFolders`.

Risks and test signals: Duplicate folders are treated as dangerous because the GUI cannot safely resolve them; the test protects fail-fast behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/dupfolders.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/example.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/example.xml

Purpose: Representative legacy config fixture used for migration, copy, and save/load tests.

Important data: Version 10 config with a default folder, three devices, GUI settings, and old options such as UDP discovery servers, old local announce port/group, UPnP fields, old listen address syntax, read-only flag, and puller count.

Control flow and state: Loading migrates addresses, discovery, local announce settings, NAT fields, folder type, puller settings, defaults, and current version. Save/load tests persist the prepared config back to XML and reload it.

Dependencies and integration: Used by `TestCopy`, `TestNewSaveLoad`, the skipped device-removal share test, and historical migration coverage.

Risks and test signals: Provides broad compatibility coverage for realistic old configuration state and deep-copy isolation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/example.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/ignoreddevices.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/ignoreddevices.xml

Purpose: XML fixture for root-level ignored remote device pruning.

Important data: Version 15 config includes two configured devices and two `remoteIgnoredDevice` entries, one of which matches a configured device.

Control flow and state: `prepareIgnoredDevices` removes ignored-device entries that are already present in `Devices` and keeps only unknown ignored devices.

Dependencies and integration: Used by `TestIgnoredDevices` and `TestGetDevice`.

Risks and test signals: Ensures manual device addition overrides prior ignored state.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/ignoreddevices.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/ignoredfolders.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/ignoredfolders.xml

Purpose: XML fixture for per-device ignored folder pruning.

Important data: Version 28 config includes devices with ignored folders and a configured folder shared with one of those devices.

Control flow and state: Device preparation removes ignored-folder entries for folders now shared with that device and removes ignored folders for unavailable devices.

Dependencies and integration: Used by `TestIgnoredFolders`.

Risks and test signals: Ensures accepting or configuring a folder clears stale ignored state for the relevant device while preserving unrelated ignored folders.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/ignoredfolders.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/issue-1262.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/issue-1262.xml

Purpose: Regression fixture for Windows drive-root folder path handling.

Important data: Version 7 config has folder path `e:` with read-only legacy flag.

Control flow and state: On Windows, filesystem initialization should resolve the path to `e:\` after config load.

Dependencies and integration: Used by `TestIssue1262`, skipped on non-Windows platforms.

Risks and test signals: Protects platform-specific path semantics during migration/preparation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/issue-1262.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/issue-1750.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/issue-1750.xml

Purpose: Regression fixture for preserving trimmed option values through migration.

Important data: Version 9 config has listen addresses and global announce servers padded with whitespace.

Control flow and state: `OptionsConfiguration.prepare` unique-trims options before migrations run, preserving the exact intended address strings.

Dependencies and integration: Used by `TestIssue1750`.

Risks and test signals: Protects migration ordering; if migrations ran before option preparation, old schemas could be incorrectly rewritten.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/issue-1750.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/largeinterval.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/largeinterval.xml

Purpose: XML fixture for clamping invalid folder rescan intervals.

Important data: Version 10 config has one overly large `rescanIntervalS` and one negative interval.

Control flow and state: `FolderConfiguration.prepare` clamps values above `MaxRescanIntervalS` down to the maximum and negative values to zero.

Dependencies and integration: Used by `TestLargeRescanInterval`.

Risks and test signals: Prevents pathological scan intervals from persisting into scheduler behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/largeinterval.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/nolistenaddress.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/nolistenaddress.xml

Purpose: XML fixture for preserving an explicit empty listen address.

Important data: Version 1 config with `<listenAddress></listenAddress>`.

Control flow and state: Loading keeps `RawListenAddresses` as `[]string{""}` rather than replacing it with default listen addresses.

Dependencies and integration: Used by `TestNoListenAddresses`.

Risks and test signals: Protects historical behavior for users who intentionally disabled listening through an empty entry.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/nolistenaddress.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/nopath.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/nopath.xml

Purpose: XML fixture for rejecting folders without a path.

Important data: Version 15 config with folder `f1` and no `path` attribute.

Control flow and state: `prepareFolders` returns an error wrapping `errFolderPathEmpty`.

Dependencies and integration: Used by `TestEmptyFolderPaths`.

Risks and test signals: Prevents accidental normalization of an empty path into current directory or filesystem root.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/nopath.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/overridenvalues.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/overridenvalues.xml

Purpose: Current-version XML fixture covering many non-default option and default values.

Important data: Version 52 config sets custom listen/discovery/local announce, bandwidth, relay/NAT, usage reporting, upgrade, temp/cache, home disk free, release/crash URLs, STUN, notification IDs, feature flags, audit, connection priorities, and folder/device defaults.

Control flow and state: Loading should preserve explicit current-version values, generate `URUniqueID` when usage reporting is accepted and missing, and apply default-folder path from the `<defaults>` section.

Dependencies and integration: Used by `TestOverriddenValues`.

Risks and test signals: Broad regression fixture for avoiding unintended default overwrites in current configs. It also documents deprecated/ignored XML fields that may still appear.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/overridenvalues.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/pullorder.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/pullorder.xml

Purpose: XML fixture for pull-order enum parsing and round-trip behavior.

Important data: Version 10 config with folders using default, explicit supported pull orders, and an unknown `whatever` value.

Control flow and state: `PullOrder.UnmarshalText` maps supported strings and falls back to random for unknown/empty values; writing emits canonical strings.

Dependencies and integration: Used by `TestPullOrder`.

Risks and test signals: Protects scheduling option compatibility and serialization stability.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/pullorder.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/untrustedintroducer.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/untrustedintroducer.xml

Purpose: Security regression fixture for untrusted device preparation.

Important data: Version 37 config has an untrusted device marked as introducer and auto-accepting, with one folder shared without an encryption password and another shared with a password.

Control flow and state: `DeviceConfiguration.prepare` clears introducer and auto-accept flags for untrusted devices. `ensureNoUntrustedTrustingSharing` removes trusted shares to untrusted devices unless an encryption password is set or the folder is receive-encrypted.

Dependencies and integration: Used by `TestUntrustedIntroducer`.

Risks and test signals: Protects against accidentally trusting untrusted devices or allowing unencrypted folder sharing with them.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/untrustedintroducer.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/v22.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/v22.xml

Purpose: Historical fixture for config version 22 migration.

Important data: Contains a read-only folder using current-ish filesystem type fields, fsync legacy element, two devices with TCP URLs, and expected folder/device values.

Control flow and state: Loading migrates through later versions to `CurrentVersion`, preserving folder/device semantics while applying newer defaults such as junction handling, max concurrent writes, xattr defaults, and block indexing.

Dependencies and integration: Used by `TestDeviceConfig` when iterating available historical version fixtures.

Risks and test signals: Ensures mid-era configs still migrate to the same expected structure as older fixtures.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/v22.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/v5.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/v5.xml

Purpose: Historical fixture for config version 5 migration.

Important data: Contains a legacy read-only folder, device shares, devices with boolean compression and scheme-less addresses.

Control flow and state: Loading applies older migrations for disk-free defaults, address scheme conversion, folder type conversion, watcher/default fields, and current version upgrades.

Dependencies and integration: Used by `TestDeviceConfig`.

Risks and test signals: Protects long-range upgrade compatibility from early config formats.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/v5.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/versioningconfig.xml -->
## sources/sync-backup/syncthing/lib/config/testdata/versioningconfig.xml

Purpose: XML fixture for versioning parameter parsing.

Important data: Version 22 config with folder `test`, versioning type `simple`, and two `<param>` entries.

Control flow and state: `VersioningConfiguration.UnmarshalXML` decodes internal param slices into a map; config preparation/migration preserves the parameters.

Dependencies and integration: Used by `TestVersioningConfig`.

Risks and test signals: Protects XML map encoding/decoding for versioner configuration.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/testdata/versioningconfig.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/versioningconfiguration.go -->
## sources/sync-backup/syncthing/lib/config/versioningconfiguration.go

Purpose: Defines folder versioning configuration and custom XML/JSON handling for map-like parameters.

Important APIs/types/functions: `VersioningConfiguration` stores type, params map, cleanup interval, filesystem path, and filesystem type. Internal XML types are `internalVersioningConfiguration` and `internalParam`. Methods include `Reset`, `Copy`, `UnmarshalJSON`, `UnmarshalXML`, `MarshalXML`, `toInternal`, and `fromInternal`.

Control flow and state: JSON unmarshal applies defaults before decoding. XML unmarshal decodes to an internal slice representation, then builds `Params`. XML marshal converts the map to sorted `param` elements so output is deterministic.

Dependencies and integration: Uses `structutil`, `FilesystemType`, sorting, and XML/JSON packages. Consumed by `FolderConfiguration.Versioning` and migrations that move legacy params into `FSPath`/`FSType`.

Risks and test signals: Param-map ordering must be deterministic for stable config writes. Tests cover XML serialization and fixture parsing of versioning params.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/versioningconfiguration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/wrapper.go -->
## sources/sync-backup/syncthing/lib/config/wrapper.go

Purpose: Provides the concurrency-safe service wrapper around `Configuration`, including queued modifications, verifier/committer notification, delayed persistence, accessors, and restart-required tracking.

Important APIs/types/functions: Interfaces `Committer`, `Verifier`, `Waiter`, `Wrapper`, and `ModifyFunction`; concrete `wrapper`, `modifyEntry`, and `modifyResult`; constructors `Wrap` and `Load`; service method `Serve`; mutation methods `Modify`, `RemoveFolder`, `RemoveDevice`; accessors for raw config, GUI, LDAP, options, defaults, folders, devices, ignored state; subscription methods; `Save`; and `RequiresRestart`.

Control flow and state: `Modify` enqueues a function into a bounded channel and waits for immediate validation result. `Serve` serializes queued modifications, applies the function to a deep copy, compares with current config, prepares/verifies/replaces under lock, schedules delayed saves at `minSaveInterval`, and waits for all subscriber committers before processing the next modification. Verifiers can reject before state changes; committers run after state replacement and can set `requiresRestart` by returning false. `Save` writes XML atomically and logs `events.ConfigSaved`.

Dependencies and integration: Uses `suture.Service`, `events.Logger`, `osutil.CreateAtomic`, `LineEndingsWriter`, `protocol`, `sliceutil`, logging, mutexes, atomics, and wait groups. Other packages subscribe as committers to react to config changes; API/UI code uses wrapper modification and accessors.

Risks and test signals: Deadlocks are possible if committers call back into wrapper while locks are held, so waiting is done outside locks where needed. Queue overflow returns `errTooManyModifications`. Delayed save means config state can be in memory before disk persistence. Tests cover commit/validation/restart semantics and save/load round trips.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/config/wrapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/connections_test.go -->
## sources/sync-backup/syncthing/lib/connections/connections_test.go

Purpose: Tests connection utility behavior, factory selection, connection status bookkeeping, next-dial cooldown cleanup, and real TCP/QUIC connection establishment.

Important APIs/types/functions: Tests `fixupPort`, `IsAllowedNetwork`, `getDialerFactory`, `getListenerFactory`, `connectionStatusHandler`, `nextDialRegistry.sleepDurationAndCleanup`, and data transfer through `withConnectionPair`. Helpers build TLS certs, suture supervisors, NAT service, listener/dialer factories, registries, and LAN checkers.

Control flow and state: Factory tests parse URIs and verify deprecated, disabled, invalid, and supported schemes. Connection status tests ensure `context.Canceled` does not overwrite meaningful errors. Next-dial tests simulate timestamps and attempt counts to verify registry cleanup. Establishment tests start a listener, wait for a concrete LAN address, dial it, trigger QUIC stream setup with an initial write, then verify data transfer.

Dependencies and integration: Integrates `config`, `registry`, `nat`, `protocol`, `tlsutil`, `suture`, network sockets, and connection factories from files outside this subset. Benchmarks optionally use a local relay.

Risks and test signals: Real network tests can be timing-sensitive, especially QUIC/relay registration. Coverage protects default port fixups, CIDR allow/deny order, deprecated KCP rejection, disabled relay behavior, cooldown pruning, and basic encrypted transport functionality.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/connections_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/debug.go -->
## sources/sync-backup/syncthing/lib/connections/debug.go

Purpose: Provides the package-local logging adapter for connection handling.

Important APIs/types/functions: Declares `l = slogutil.NewAdapter("Connection handling")`.

Control flow and state: Static package initialization only.

Dependencies and integration: Used throughout connection services, dialers, listeners, LAN checking, and limiter code for debug logging.

Risks and test signals: Minimal logic risk; logging category stability affects diagnostics. No direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/deprecated.go -->
## sources/sync-backup/syncthing/lib/connections/deprecated.go

Purpose: Registers deprecated KCP connection schemes as explicitly invalid listener/dialer factories.

Important APIs/types/functions: `invalidListener` and `invalidDialer` embed the normal factory interfaces and implement `Valid(config.Configuration) error`. `init` registers `kcp`, `kcp4`, and `kcp6` in both factory maps with `errDeprecated`.

Control flow and state: Factory lookup for these schemes returns a factory whose `Valid` method always errors, defaulting to `errUnsupported` if no explicit error is configured.

Dependencies and integration: Uses the global `listeners` and `dialers` registries from the connections package and `config.Configuration` for interface compatibility.

Risks and test signals: Keeps deprecated protocols recognizable so users get a deprecation error instead of a generic unsupported error. `TestGetDialer` validates KCP returns `errDeprecated`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/deprecated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/dialqueue.go -->
## sources/sync-backup/syncthing/lib/connections/dialqueue.go

Purpose: Orders pending device dial attempts to prefer likely useful connections while randomizing stale targets.

Important APIs/types/functions: `dialQueueEntry` stores device ID, last-seen time, short-lived flag, and targets. `dialQueue.Sort` sorts and shuffles entries.

Control flow and state: First sort puts non-short-lived, recently seen devices first and orders them by most recent `lastSeen`. Entries older than `recentlySeenCutoff` and short-lived entries are treated as stale; the stale suffix is shuffled to distribute attempts across old/unreliable devices.

Dependencies and integration: Uses `protocol.DeviceID`, `dialTarget` from connection structs, `recentlySeenCutoff` from service constants, and Syncthing `rand.Shuffle`.

Risks and test signals: Ordering affects connection fairness and startup convergence. `dialqueue_test.go` checks recent ordering and randomized stale/short-lived suffix behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/dialqueue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/dialqueue_test.go -->
## sources/sync-backup/syncthing/lib/connections/dialqueue_test.go

Purpose: Tests `dialQueue.Sort` ordering and randomization behavior.

Important APIs/types/functions: `TestDialQueueSort` has subtests `ByLastSeen`, `OldConnections`, and `ShortLivedConnections`; helper `shortDevices` extracts short IDs for comparison.

Control flow and state: Recent devices are expected in strict newest-first order. Old entries are sorted into a stale suffix and shuffled repeatedly, with the test requiring both possible orders to appear enough times. Short-lived recent entries are treated like stale entries for ordering.

Dependencies and integration: Uses shared test device IDs, `time.Now`, and `protocol.ShortID`.

Risks and test signals: Randomized assertions can be flaky if randomness is biased, but repeated loops with broad thresholds make failures meaningful. Protects fairness semantics in the dial scheduler.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/dialqueue_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/lan_test.go -->
## sources/sync-backup/syncthing/lib/connections/lan_test.go

Purpose: Tests LAN host classification with loopback, configured local networks, public addresses, and invalid host strings.

Important APIs/types/functions: `TestIsLANHost` constructs a config wrapper with `Options.AlwaysLocalNets` and calls `lanChecker.isLANHost`.

Control flow and state: The cases verify loopback is LAN, `10.20.30.0/24` is LAN due to config, `192.0.2.1` is not LAN, and malformed host strings return false rather than erroring outward.

Dependencies and integration: Uses `config.Wrap`, `events.NoopLogger`, `protocol.LocalDeviceID`, and `lanChecker` from connection service code.

Risks and test signals: LAN classification controls bandwidth-limit behavior, local address announcement, and connection prioritization. The test guards both configured networks and robust parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/lan_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/limiter.go -->
## sources/sync-backup/syncthing/lib/connections/limiter.go

Purpose: Applies global and per-device read/write bandwidth rate limits to connection streams and updates them on config changes.

Important APIs/types/functions: `limiter` implements `config.Committer`; `newLimiter`, `setLimitsLocked`, `processDevicesConfigurationLocked`, `CommitConfiguration`, `getLimiters`, `newLimitedReaderLocked`, `newLimitedWriterLocked`, per-device limiter accessors, `limitedReader`, `limitedWriter`, `waiterHolder`, and `totalWaiter`.

Control flow and state: Construction subscribes to the config wrapper and initializes global/per-device rate limiters. On config commit, it updates per-device limiters, removes deleted-device limiters, updates global send/recv limiters, and stores whether LAN should be limited. `getLimiters` wraps an `io.ReadWriter` with readers/writers that wait on both per-device and global token buckets. Reads consume after reading; writes split large buffers into adaptive chunks to avoid bursty writes and avoid `WaitN` calls larger than the burst size.

Dependencies and integration: Uses `golang.org/x/time/rate`, `config.Wrapper`, `protocol.DeviceID`, `io`, atomics, locks, and logging. Called by connection setup to wrap streams after LAN classification.

Risks and test signals: Correct lock scope matters because config commits and stream creation can race. Token waits use `context.TODO`, so a blocked limiter wait is not cancelable. LAN exemption depends on `LimitBandwidthInLan`. No direct limiter tests in this subset, but config bandwidth tests and connection tests exercise surrounding behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/connections/limiter.go -->
