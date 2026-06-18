# sources/cloud-native/buildkit/client/llb/meta.go

Purpose: implements state metadata options and accessors for environment, working directory, user, args, platform, extra hosts, ulimits, cgroup parent, Linux resources, network, security, and environment list behavior.

Important APIs/types/functions: state options include `AddEnv`, `AddEnvf`, `Dir`, `Dirf`, `User`, `Reset`, `Hostname`, `Network`, `Security`, plus internal `args`, `shlexf`, `platform`, `extraHost`, `ulimit`, and `cgroupParent`. Getter factories retrieve typed values from state chains. `LinuxResources` is a public resource-limit struct. `EnvList` is a persistent linked environment list with add/replace/default/delete/get/keys/to-array behavior.

Control flow: state options wrap previous state with a lazy value function. Relative `Dir` resolves against previous directory at lookup time and normalizes through `path.Join`. Environment additions build an `EnvList` chain; `makeValues` walks from newest to oldest, records first non-deleted value, reverses keys to preserve final order, and memoizes using `sync.Once`.

State and persistence: metadata lives in immutable `State` value chains and is evaluated lazily with constraints. `EnvList` memoizes computed maps/slices in memory. No external persistence.

Dependencies/integration points: used heavily by `exec.go`, `fileop.go`, `state.go`, image config application, platform tests, and shlex parsing. Network/security values are solver protobuf enums.

Risks/test signals: `shlexf` ignores split errors, which can silently produce nil args and later exec validation errors. `Dir` closure mutates captured `value` when resolving relative paths, making repeated/concurrent lookups subtle. `EnvList.Delete` returns a value not pointer, so call sites need care. Tests cover relative working directory normalization through `meta_test.go`.
