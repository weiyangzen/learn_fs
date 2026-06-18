# sources/cloud-native/containers-storage/pkg/mount/mountinfo.go

Purpose: re-exports mountinfo parsing and mounted checks through the local `mount` package.

Important APIs, types, and functions: type alias `Info`, variable alias `Mounted`, and `GetMounts`.

Control flow: `GetMounts` delegates to `mountinfo.GetMounts(nil)`.

State and persistence: reads mount table information from the platform mountinfo implementation; no mutation.

Dependencies and integration points: depends on `github.com/moby/sys/mountinfo`. Used by high-level mount checks, recursive unmount, and tests.

Risks and edge cases: returned mount data reflects the current namespace and can change concurrently. Filter is nil, so all mounts are returned.

Test signals: `mount_unix_test.go` checks that `/` appears in mounts and that mounted targets are detected.
