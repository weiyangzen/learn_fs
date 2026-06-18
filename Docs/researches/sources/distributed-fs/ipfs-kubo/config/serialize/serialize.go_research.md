# Research: sources/distributed-fs/ipfs-kubo/config/serialize/serialize.go

Purpose: Reads and writes Kubo config files for fsrepo.

Important APIs/types/functions: `ErrNotInitialized`, `ReadConfigFile`, `WriteConfigFile`, `encode`, and `Load`.

Control flow, state, and persistence: `ReadConfigFile` opens and JSON-decodes a config file, mapping missing files to `ErrNotInitialized`. `WriteConfigFile` creates parent directories, opens an atomic file with mode `0600`, writes pretty JSON via `config.Marshal`, and relies on atomicfile close semantics. `Load` reads into `config.Config`.

Dependencies and integration points: Package name is `fsrepo` despite living under `config/serialize`; it is part of repository config persistence. Uses `facebookgo/atomicfile` to avoid partial writes.

Risks and test signals: Decode errors wrap with context but do not include filename. Atomic write close errors depend on deferred close behavior from atomicfile. `serialize_test.go` verifies round-trip and permissions on non-Windows.
