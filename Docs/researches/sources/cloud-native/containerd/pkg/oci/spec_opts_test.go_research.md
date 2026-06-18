# sources/cloud-native/containerd/pkg/oci/spec_opts_test.go

Purpose: broad platform-neutral tests for the main `SpecOpts` library.

Important APIs/types/functions: defines fake content/image helpers, then tests env replacement, default spec platform selection, process cwd, env appending, mounts, spec-from-file, memory/swap/pids/blockio/cpu options, TTY size, user namespace mappings, image config args, `/dev/shm` size, mount removal, parent cgroup devices, Windows device/resource options, and helper equality checks.

Control flow: tests construct minimal specs or fake images, apply one or more options, and inspect targeted fields. Image config tests serialize OCI image configs into fake content blobs so production `WithImageConfigArgs` paths run.

State/persistence: temporary files for spec JSON and in-memory fake content store.

Dependencies/integration: runtime-spec, image-spec, content store interfaces, and testify/Go testing.

Risks: many tests validate field mutation but not runtime execution. Some Linux-specific effects are skipped or no-op depending on spec platform fields.

Test signals: strongest regression suite for option order, env merging, resource initialization, image command semantics, `/dev/shm` option replacement, and cross-platform no-op behavior.
