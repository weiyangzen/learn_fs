# sources/cloud-native/containerd/core/diff/apply/apply_other.go

Purpose: non-Linux implementation of diff application.

Important function: build-tagged `apply` applies tar streams either directly into a bind mount source when bind mounts are unsupported and there is a single bind mount, or via `mount.WithTempMount` otherwise.

Control flow and state: on direct bind path, it adds `archive.WithNoSameOwner` when not root, applies to `mounts[0].Source`, and ignores sync because Windows sync semantics are TODO. Generic path temp-mounts and applies normally.

Dependencies and integration: core mount and archive packages plus `os.Getuid`.

Risks: `os.Getuid` availability/meaning varies by non-Linux platform. Sync is explicitly unimplemented. The direct bind path depends on `mount.HasBindMounts` platform constant.

Test signals: no direct tests. Platform build and integration tests must validate behavior.
