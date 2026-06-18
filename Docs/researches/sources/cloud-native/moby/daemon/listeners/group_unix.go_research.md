## sources/cloud-native/moby/daemon/listeners/group_unix.go

Purpose: Resolves the Unix socket group used when creating Docker daemon Unix sockets.

Important API: `lookupGID(name string) (int, error)` first attempts `usergroup.LookupGroup`, then accepts a numeric string via `strconv.Atoi`, otherwise returns `-1` and an error. `defaultSocketGroup` is `docker`.

Control flow and state: This is a pure lookup helper. It allows both group names and numeric GIDs.

Dependencies and integration points: Used by Unix listener initialization before `sockets.NewUnixSocket`. Depends on daemon internal `usergroup` lookup and the host group database.

Risks: If the configured group does not exist and is not numeric, socket creation falls back or fails depending on caller handling. Numeric strings bypass group existence validation.

Test signals: No direct tests in this subset; behavior is indirectly relevant to listener setup.
