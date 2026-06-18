# sources/distributed-fs/eos/mgm/config/QuarkDBConfigEngine.cc

## Purpose
Implements the QuarkDB-backed `IConfigEngine` used by MGM to load, save, mutate, autosave, list, and display configuration from QuarkDB. It also implements a text changelog adapter and a background backup cleanup thread.

## Important APIs and Functions
- `QuarkDBCfgEngineChangelog::AddEntry` writes textual entries into `eos-config-changelog` and trims the deque.
- `QuarkDBCfgEngineChangelog::Tail` reads recent entries and formats epoch timestamps into local time strings.
- `QuarkDBConfigEngine::LoadConfig` resets local config, pulls a named config from QuarkDB, optionally cleans unused/deprecated entries, applies config, and records the loaded config name.
- `RemoveUnusedNodes` removes global config entries for off nodes without registered filesystems when `EOS_MGM_CONFIG_CLEANUP=1`.
- `SaveConfig` resolves the target name, checks existence if not overwriting, stores into QuarkDB, adds a changelog entry, and updates `mConfigFile`.
- `ListConfigs` delegates to `QuarkConfigHandler`.
- `CleanupThread` trims default config backups to 1000 every 30 minutes.
- `PullFromQuarkDB` replaces `sConfigDefinitions` from QuarkDB under `mMutex` and removes the `timestamp` key.
- `FilterConfig` dumps a named config to a stream.
- `AutoSave` saves only when this MGM is master, autosave is enabled, and a config name is loaded.
- `SetConfigValue` and `DeleteConfigValue` mutate `sConfigDefinitions`, publish changes to peer MGMs for local changes, update changelog, and save.
- `StoreIntoQuarkDB` filters deprecated entries and invokes async `writeConfiguration` with a timestamp backup.

## Control Flow
Loading follows `ResetConfig -> PullFromQuarkDB -> optional cleanup/save -> ApplyConfig`. Saving follows name resolution and optional existence check, then queues an async QuarkDB write and immediately records changelog/local state. Runtime config mutations update the in-memory `sConfigDefinitions` first, then publish/broadcast and persist if the change originated locally.

## State and Persistence
The engine bridges global in-memory `sConfigDefinitions` and QuarkDB hashes. It stores the current config name in `mConfigFile`, owns both a direct QClient for text changelog access and a `QuarkConfigHandler` for structured config operations, and starts an `AssistedThread` for backup cleanup. `StoreIntoQuarkDB` saves timestamped backups using local time format `YYYYMMDDHHMMSS`.

## Dependencies and Integration Points
Integrates with `IConfigEngine`, `XrdMgmOfs` globals, `FsView`, qclient, Folly, `QuarkConfigHandler`, `AssistedThread`, and the shared config map inherited from the base config engine. It uses `PublishConfigChange`/`PublishConfigDeletion` from the base class to fan out live updates.

## Risks
- `SaveConfig` reports success before the async QuarkDB write has completed; failures are logged in `checkWriteConfigurationResult` and may not propagate to the caller.
- `StoreIntoQuarkDB` holds `mMutex` while queuing async work and passes `sConfigDefinitions` by const reference to `writeConfiguration`; the handler currently copies into a multi request synchronously, but this relies on that implementation detail.
- `RemoveUnusedNodes` erases entries while iterating and checks node names by substring, which can remove unexpected entries if node names overlap.
- Cleanup behavior depends on environment variable `EOS_MGM_CONFIG_CLEANUP`; without it, stale node entries are only logged.
- Changelog format differs from protobuf changelog in `QuarkConfigHandler`, and the key naming differs from handler append behavior.

## Test Signals
Tests should exercise load/save with mocked `QuarkConfigHandler`, async write failure visibility, unused-node cleanup with overlapping node names, changelog tail parsing of malformed timestamps, autosave master gating, and config mutation broadcast/save behavior.
