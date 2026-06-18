# sources/cloud-native/moby/daemon/volume/local/local.go

## Purpose
Core implementation of Docker's built-in local volume driver, managing volume directories, metadata files, active mount counts, and live-restore reference state.

## Important APIs, Types, And Functions
`New` initializes a `Root`. `Root` implements `volume.Driver` through `List`, `Name`, `Create`, `Remove`, `Get`, and `Scope`. `localVolume` implements `volume.Volume` and `volume.LiveRestorer` through `Path`, `Mount`, `Unmount`, `Status`, `CreatedAt` in platform files, and `LiveRestoreVolume`. Helpers include `loadOpts`, `saveOpts`, `getAddress`, and `getPassword`.

## Control Flow
Startup creates `<scope>/volumes`, initializes quota control when available, scans child directories, identifies volumes by `_data` or `opts.json`, loads persisted options, restores already-mounted status, and caches volumes. `Create` validates name/options, creates root and `_data` directories with appropriate ownership, applies options, persists them if needed, and caches the volume. `Remove` rejects unknown volume types and active mounts, unmounts, resolves the data path, prevents deletion outside the local volume root, removes data/root paths, and drops cache state. `Mount` mounts once when options require it, increments active count, applies post-mount quota, and returns `_data`; `Unmount` decrements and unmounts only when the count reaches zero.

## State And Persistence
Persistent state is the volume root, `_data`, and `opts.json` written atomically. In-memory state includes the root volume map, quota controller, per-volume options, and `activeMount` count/mounted flags.

## Dependencies And Integration Points
Used as the default driver by `service/default_driver.go`. It depends on idmapped ownership helpers, quota, atomicwriter, mount platform files, errdefs, and Moby name validation.

## Risks
Deletion containment relies on symlink evaluation and prefix checks; path validation must remain strict. Mount count bugs can leave volumes mounted or removable while active. Option persistence compatibility with older nil/empty files matters during daemon upgrades. Password redaction is handled in platform mount errors.

## Test Signals
Local tests cover address/password parsing, create/remove/reload, name validation, option persistence, mount count behavior, tmpfs mounting, quota enforcement, and option validation.
