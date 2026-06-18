# sources/cloud-native/buildkit/client/llb/exec.go

Purpose: core implementation of LLB exec operations and their public run/mount/secret/SSH/CDI/cache/network/security option APIs.

Important APIs/types/functions: `ExecOp` implements `Vertex`; `mount` stores target/source/output and mount options; `NewExecOp` creates the root mount; `AddMount`, `GetMount`, `Validate`, `Marshal`, `Inputs`, and `getMountIndexFn` manage graph behavior. Public option APIs include `Shlex`, `Args`, `AddMount`, `Readonly`, `SourcePath`, `AsPersistentCacheDir`, `Tmpfs`, `AddSecret`, `SecretAsEnv`, `AddSSHSocket`, `AddCDIDevice`, `WithProxy`, `ReadonlyRootFS`, `ValidExitCodes`, network/security constants, cache-sharing constants, ulimit names, and content-cache options.

Control flow: `State.Run` builds `ExecInfo`, creates `ExecOp`, adds requested mounts, secrets, SSH, and CDI devices. `Validate` requires args and working directory and validates mount sources. `Marshal` sorts mounts by target for deterministic output, gathers environment/cwd/user/hostname/cgroup/extra hosts/ulimits/valid exits/network/security/platform from state metadata, applies default PATH behavior based on cap negotiation, adds capability requirements for every used feature, deduplicates equal protobuf inputs, assigns output indexes only to writable non-cache non-tmpfs mounts, appends secret/SSH mounts, serializes deterministically, and caches by constraints pointer.

State and persistence: state is immutable at the public `State` layer but `ExecOp` mutates internal mount slices, constraint capability metadata, SSH target defaults, validation flag, and marshal cache. Persistent cache mounts are represented by `cacheID` and sharing mode but actual persistence is managed by BuildKit daemon workers.

Dependencies/integration points: `solver/pb` exec/mount/metadata capabilities, `system.DefaultPathEnv`, state metadata from `meta.go`, constraints from `state.go`, `MarshalCache`, BuildKit secret/SSH/CDI execution support, and solver-side mount semantics.

Risks/test signals: deterministic sorting is critical because mount order affects output indexes; mutating constraints and SSH targets during marshal makes concurrency/cache behavior sensitive. Background cache keyed by constraints pointer can miss equivalent constraints or reuse after mutation. Tmpfs and no-output mounts intentionally cannot be used as parent outputs. Tests in `exec_test.go` cover tmpfs errors, mount index stability with sorted tmpfs, Linux resource metadata/cache behavior, resource merging, and marshal determinism.
