# sources/distributed-fs/eos/mgm/config/QuarkConfigHandler.cc

## Purpose
Implements `eos::mgm::QuarkConfigHandler`, the low-level QuarkDB access layer for MGM configuration hashes, configuration backups, and the configuration changelog. It translates qclient replies into `common::Status`, builds batched writes with `qclient::MultiBuilder`, and exposes synchronous read/list/tail/trim operations plus asynchronous write/changelog append operations.

## Important APIs and Functions
- `QuarkConfigHandler::QuarkConfigHandler` constructs a `qclient::QClient` from `QdbContactDetails` and creates a two-thread Folly IO executor for async continuations.
- `checkConnection` delegates to `QClient::checkConnection`.
- `checkExistence` checks `HLEN eos-config:<name>` and treats a nonzero hash length as existence.
- `listConfigurations` scans `eos-config:*` and `eos-config-backup:*` with `qclient::QScanner` and strips the storage prefixes before returning names.
- `fetchConfiguration` reads `HGETALL eos-config:<name>` and falls back to `HGETALL eos-config-backup:<name>` when the primary hash is missing or empty.
- `writeConfiguration` optionally refuses overwrite, optionally clones the old hash to a backup hash, deletes the target hash, and writes every key/value via a single qclient multi request.
- `appendChangelog` serializes `ConfigChangelogEntry` protobufs into `eos-config-changelog:default` and trims the deque to 500000 entries.
- `tailChangelog` scans the changelog deque backwards and returns serialized entries as strings.
- `trimBackups` deletes at most 200 backup hashes matching `<name>-*`.
- `FormHashKey` and `FormBackupHashKey` centralize QuarkDB key naming.

## Control Flow
Read operations are direct qclient calls followed by qclient parser validation. Write operations first validate overwrite policy with `HLEN` when needed, build an ordered multi-request, submit it through `follyExecute`, and attach a continuation that validates response cardinality and per-HSET integer results. Backup writes prepend `DEL backup` and `HCLONE current backup` before deleting and rewriting the live hash.

## State and Persistence
Persistent state lives in QuarkDB:
- live config hash: `eos-config:<name>`
- backup hash: `eos-config-backup:<name>` or timestamped `eos-config-backup:<name>-YYYYMMDDHHMMSS`
- changelog deque: `eos-config-changelog:default`

The class itself keeps only connection details, a QClient, and an executor. Backup trimming depends on scan order; there is no explicit sort by timestamp before deleting.

## Dependencies and Integration Points
Depends on qclient parsers/scanners/multi execution, Folly futures/executors, EOS `common::Status`, string helpers, logging, `QdbContactDetails`, and `ConfigChangelogEntry` protobufs. It is used by `QuarkDBConfigEngine` and the standalone `eos-config-inspect` utility.

## Risks
- `processWriteConfigurationReply` validates only HSET responses, not the `DEL`/`HCLONE` extra request results.
- `trimBackups` deletes the first scan results after prefix filtering; if scanner order is not chronological, it may remove unexpected backups.
- `fetchConfiguration` falls back to backup when the live hash is empty, so intentionally empty configs are indistinguishable from missing configs.
- `tailChangelog` scans key `eos-config-changelog`, while `appendChangelog` writes `eos-config-changelog:default`; this key mismatch is a compatibility or bug signal worth testing against the deployed deque API.
- Async writes require callers to observe the returned future; otherwise persistence errors surface only through downstream continuations or logs.

## Test Signals
Useful tests include mocked qclient replies for malformed HLEN/HGETALL/multi responses, write-with-backup request ordering, overwrite refusal, changelog key consistency, backup trim ordering, and fallback behavior for missing live configs. Integration tests need a QuarkDB instance with qclient deque/hash support.
