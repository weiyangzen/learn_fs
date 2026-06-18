# sources/cloud-native/buildkit/client/mergediff_nolinux_test.go

Purpose: non-Linux fallback helpers for merge/diff tests that cannot create FIFOs or character devices.

Important APIs/types/functions: build tag `!linux`; `mkfifo` and `mkchardev` return `fstest.Applier`s that fail with not-implemented errors.

Control flow: applying either helper returns an explicit error instead of attempting unsupported node creation.

State and persistence: no filesystem mutation occurs because appliers fail.

Dependencies/integration points: containerd continuity `fstest`, `pkg/errors`, and platform-agnostic merge/diff tests that can skip or expect unsupported behavior.

Risks/test signals: tests using these helpers must handle the explicit errors on non-Linux. Keeps unsupported behavior visible rather than silently passing.
