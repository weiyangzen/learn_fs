# sources/distributed-fs/ipfs-kubo/core/commands/sysdiag.go

Purpose: implements system diagnostic output used for support/debugging.

Important APIs/types/functions: `sysDiagCmd` emits `getInfo(nd)`; helper functions populate runtime, environment, disk, memory, and network maps.

Control flow: command obtains node, builds a `map[string]any`, sequentially calls `runtimeInfo`, `envVarInfo`, `diskSpaceInfo`, `memInfo`, and `netInfo`, then adds Kubo version and commit.

State and persistence behavior: read-only. It reads environment variables, repo root path, disk usage, memory info, network interface addresses, and node online status.

Dependencies and integration points: uses `config.PathRoot`, `go-sysinfo` disk/memory helpers, `manet.InterfaceMultiaddrs`, runtime package, and Kubo version constants.

Risks: diagnostics may expose environment paths and interface addresses. Any helper error aborts the whole command. Memory field names are terse (`swap`, `virt`) and depend on go-sysinfo semantics.

Test signals: no direct tests in this file.
