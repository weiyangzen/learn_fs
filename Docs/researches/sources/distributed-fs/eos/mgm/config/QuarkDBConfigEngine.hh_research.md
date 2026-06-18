# sources/distributed-fs/eos/mgm/config/QuarkDBConfigEngine.hh

## Purpose
Declares the QuarkDB implementation of the MGM `IConfigEngine` interface and its text changelog adapter. It is the primary header tying QuarkDB storage to the generic MGM configuration engine contract.

## Important APIs and Types
- `QuarkDBCfgEngineChangelog : ICfgEngineChangelog` exposes `AddEntry` and `Tail`.
- `QuarkDBConfigEngine : IConfigEngine` overrides `LoadConfig`, `SaveConfig`, `ListConfigs`, `AutoSave`, `SetConfigValue`, `DeleteConfigValue`, and private `FilterConfig`.
- `FormatBackupTime` is an inline timestamp formatter used for backup names.
- Private helper methods cover QuarkDB store/pull, cleanup thread, unused/deprecated key removal, and config filtering.
- Private members own QDB contact details, QClient, `QuarkConfigHandler`, Folly executor, and cleanup assisted thread.

## Control Flow and State
The header makes `QuarkDBConfigEngine` a stateful engine with persistent connection objects and a background cleanup thread. The default constructor is exposed only under `IN_TEST_HARNESS`, indicating tests can instantiate without QDB wiring for isolated helper coverage.

## Dependencies and Integration Points
Depends on `IConfigEngine`, `QuarkConfigHandler`, qclient `QHash`/`AsyncHandler`/`QClient`, QuarkDB contact details, and EOS assisted threading/status primitives. It inherits base config state such as `sConfigDefinitions` through `IConfigEngine`.

## Risks
- `DeleteConfigValue` comment documents `save_config`, but the signature lacks that parameter, indicating stale API documentation.
- Inline `FormatBackupTime` uses `localtime`, which is not thread-safe and is also used by the implementation in concurrent contexts.
- Header includes several heavy qclient headers, increasing compile coupling.

## Test Signals
Compile tests should cover interface conformance. Unit tests can use `IN_TEST_HARNESS` to validate `FormatBackupTime`, `RemoveUnusedNodes`, config serialization/filtering, and private helper behavior without requiring a full engine bootstrap.
