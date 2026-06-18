# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/start.go

## Purpose
This file implements Kubo CLI process startup: tracing, plugin loading, environment construction, interrupt handling, local-vs-remote executor selection, profiling, API address resolution, and remote version negotiation.

## Important APIs, Types, And Functions
Important functions include `loadPlugins`, `BuildDefaultEnv`, `BuildEnv`, `Start`, `checkDebug`, `apiAddrOption`, `makeExecutor`, `tracingWrappedExecutor.Execute`, `getRepoPath`, `startProfiling`, `profileIfEnabled`, `resolveAddr`, and `getRemoteVersion`.

## Control Flow
`Start` initializes tracing, optional profiling, interrupt handler, command aliases (`--version`, `help`), GUI no-arg daemon fallback, stable `os.Args[0]`, then runs the CLI with `BuildEnv` and `makeExecutor`. `makeExecutor` decides local execution, explicit or repo-discovered daemon API use, fallback behavior, TCP/Unix transports, API auth headers, remote version lookup, and multipart compatibility.

## State And Persistence Behavior
It loads plugins from the repo path, may open fsrepo lazily, writes CPU/heap profile files when enabled, mutates global logging/tracing providers, and reads the repo API file.

## Dependencies And Integration Points
It integrates go-ipfs-cmds CLI/HTTP clients, Kubo command tree, fsrepo path detection, plugin loader, tracing/OTel, DNS multiaddr resolver, API authorization, and signal handling.

## Risks And Test Signals
Risks include remote/local fallback surprises, remote version fetch before command execution, Unix socket transport handling, profiler goroutine leak, and global `os.Args` rewriting. Tests cover DNS resolution and coverage-time main execution; broader signals come from CLI integration tests.
