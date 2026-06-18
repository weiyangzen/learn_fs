# sources/cloud-native/cri-o/server/sandbox_run_unsupported.go

Purpose: unsupported-platform implementation for sandbox creation and ID mapping lookup.

Important APIs and functions: `runPodSandbox` and `getSandboxIDMappings` both return `"unsupported"` errors.

Control flow: no sandbox work is attempted.

State and persistence: none.

Dependencies and integration: build-tag fallback for platforms other than Linux and FreeBSD.

Risks: CRI runtime service cannot create pod sandboxes on these platforms.

Test signals: compile-time coverage only.
