## sources/cloud-native/buildkit/snapshot/localmounter_windows.go

Purpose: Windows implementation of local mounting for single containerd mount entries and bind emulation.

Important APIs/types/functions: `Mount` enforces exactly one mount, returns writable bind/rbind sources directly, emulates read-only binds via `bindfilter.ApplyFileBinding`, and otherwise calls `mountWithRetries`. `mountWithRetries` retries transient "file being used by another process" errors with backoff. `Unmount` removes bindfilter bindings or calls `mount.Unmount`, then removes target and release.

Control flow: mutex protects idempotence. Non-bind mounts get up to two retries for known Windows race symptoms. Unmount treats invalid parameter/not found from bindfilter as already unmounted.

State and persistence: temp directory target plus Windows bindfilter/mount state.

Dependencies and integration points: depends on go-winio bindfilter, containerd mount, and Windows error constants. Used for Windows snapshot local access.

Risks and test signals: only one mount is supported; multi-layer Windows snapshots must encode parent layers in mount options. Returning writable bind source before setting `target` means the temp directory created just before may be leaked. No Windows-specific test in subset.
