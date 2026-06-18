## sources/cloud-native/containers-storage/pkg/idtools/idtools_unix.go

Purpose: Unix implementation of directory creation with ownership, access checks, passwd/group lookup with getent fallback, and command execution helpers.

Important APIs/types/functions: `mkdirAs`, `CanAccess`, `accessible`, `LookupUser`, `LookupUID`, `LookupGroup`, `LookupGID`, `getentUser`, `getentGroup`, `callGetent`, and package globals `entOnce/getentCmd`.

Control flow: `mkdirAs` identifies missing path components, requires absolute paths for recursive creation, creates directories, and chowns only required components depending on `chownExisting`. Lookup functions first use moby/sys/user local file lookup, then call `getent` if available, parsing passwd/group output and mapping exit codes to user-facing errors.

State and persistence: creates directories and changes ownership. Caches resolved `getent` path with `sync.Once`. Spawns external `getent` process.

Dependencies and integration points: backs public mkdir/chown helpers in `idtools.go` and user/group lookups in storage setup. Depends on `fileutils.Exists`, `system.Stat`, `moby/sys/user`, and `utils_unix.go` command helpers.

Risks: `callGetent` returns `fmt.Errorf("")` when no getent exists, an unhelpful empty error. `mkdirAs` only records missing ancestors before creation; concurrent filesystem changes can alter chown behavior. Absolute path requirement applies only to recursive creation.

Test signals: `idtools_unix_test.go` covers mkdir ownership behavior and relative path rejection; no selected tests for getent fallback or access checks.
