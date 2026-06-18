# sources/cloud-native/moby/daemon/runtime_unix.go

## Purpose
Configures containerd runtimes for non-Windows daemons, including stock runc runtime entries, custom path runtimes, custom shim-type runtimes, wrapper scripts for runtime arguments, feature discovery, and validation of implicit containerd runtime names.

## Important APIs, Types, And Functions
`shimConfig` stores shim name, options, features, and optional preflight check. `runtimes` stores default and configured runtimes. Key functions are `stockRuntimes`, `defaultV2ShimConfig`, `runtimeScriptsDir`, `initRuntimesDir`, `setupRuntimes`, `wrapRuntime`, `(*runtimes).Get`, `(*runtimes).Features`, and `isPermissibleC8dRuntimeName`.

## Control Flow
`setupRuntimes` rejects attempts to override the reserved stock runtime, installs stock entries, validates default runtime, then processes configured runtimes. Path runtimes become runc-v2 options, optionally via generated shell wrappers when args are present. Type runtimes become direct shim names with generated typed options. `Get` resolves explicit or default runtimes, runs preflight checks, and permits implicit containerd runtime names only if they are well-formed and not path-like.

## State And Persistence
`initRuntimesDir` removes and recreates the runtime script directory. `wrapRuntime` writes executable wrapper scripts named from a hash of their contents so existing scripts referenced by running containers are not modified. Runtime feature discovery runs the runtime binary's `features` command and stores decoded OCI runtime features in memory.

## Dependencies And Integration Points
Integrates with daemon config, containerd runc options, containerd plugin runtime names, shim option generation, atomic file writes, and start code that calls `runtimes.Get`.

## Risks And Edge Cases
Wrapper scripts concatenate binary and args into shell without quoting, so configured paths/args must be trusted daemon config. Feature discovery failures only warn. Blocking path-like implicit runtime names is security-sensitive because containerd can otherwise execute arbitrary host binaries as root. Custom path runtimes without args are not preflight-checked.

## Test Signals
`runtime_unix_test.go` covers invalid config combinations, default runtime validation, explicit versus implicit runtime resolution, shim option generation, preflight checks, wrapper content, and wrapper immutability across reloads.
