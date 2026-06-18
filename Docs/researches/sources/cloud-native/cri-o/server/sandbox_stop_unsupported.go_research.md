# sources/cloud-native/cri-o/server/sandbox_stop_unsupported.go

Purpose: unsupported-platform implementation for pod sandbox stopping.

Important APIs and functions: `stopPodSandbox` returns `"unsupported"`.

Control flow: no stop work is attempted.

State and persistence: none.

Dependencies and integration: build-tag fallback for platforms other than Linux and FreeBSD.

Risks: runtime cannot stop pod sandboxes on unsupported platforms through this implementation.

Test signals: compile-time coverage only.
