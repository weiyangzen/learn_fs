# sources/distributed-fs/eos/mgm/imaster/IMaster.cc

## Purpose

`IMaster.cc` implements shared helper behavior for the abstract MGM master-state interface declared in `IMaster.hh`. It supplies log buffering, lock/status file management, and namespace cache sizing defaults used by concrete master implementations.

## Important APIs, Types, and Functions

- `IMaster::MasterLog(const char* log)` appends non-empty log messages to `mLog` under `mMutex`.
- `IMaster::CreateStatusFile(const char* path)` creates a status/lock file with mode `S_IRWXU | S_IRGRP | S_IROTH` if it does not exist.
- `IMaster::RemoveStatusFile(const char* path)` unlinks an existing status/lock file.
- `IMaster::FillNsCacheConfig(IConfigEngine*, std::map<std::string, std::string>&)` reads namespace cache size settings and writes QuarkDB namespace constants.

## Control Flow

Status-file helpers first `stat()` the target path. Creation only calls `creat()` when the file is missing; removal only calls `unlink()` when the file exists. Errors are logged through `MasterLog()` using EOS static log formatting and return `false`.

`FillNsCacheConfig()` starts with defaults of 40,000,000 files and 5,000,000 directories. It asks `IConfigEngine` for `ns.cache-size-nfiles` and `ns.cache-size-ndirs`, parses them as unsigned integers, logs critical parse failures, and writes stringified values into the passed map under `constants::sMaxNumCacheFiles` and `constants::sMaxNumCacheDirs`.

## State and Persistence Behavior

`mLog` is the only object-local state changed by this file. Status-file creation/removal affects filesystem state, commonly under `/var/eos` paths defined in the header. Namespace cache config is not persisted directly here; it mutates the caller-provided map that later configures namespace services.

## Dependencies and Integration Points

The file depends on `mgm/config/IConfigEngine.hh` for config reads, `namespace/ns_quarkdb/Constants.hh` for namespace cache keys, POSIX filesystem calls (`stat`, `creat`, `unlink`, `close`), and EOS parse/logging helpers.

Concrete master implementations call these helpers while managing MGM master/slave transitions. The lock-file semantics are paired with XrdMqOfs behavior by convention rather than direct linkage.

## Risks and Edge Cases

- `CreateStatusFile()` treats any `stat()` failure as "file missing"; permission errors or transient filesystem errors will lead to a `creat()` attempt rather than a distinct diagnostic.
- `RemoveStatusFile()` ignores `stat()` errors, so permission or path errors can be silently treated as already removed.
- `CreateStatusFile()` uses `creat()` without `O_CLOEXEC`.
- `FillNsCacheConfig()` dereferences `configEngine` without a null check.
- On parse failures, defaults remain in effect but only a critical log indicates the bad config.

## Test Signals

Tests should cover successful create/remove, permission-denied failure paths, idempotent behavior when files already exist or are already absent, log appending under repeated calls, default namespace cache values, valid config override parsing, and invalid numeric strings preserving defaults.
