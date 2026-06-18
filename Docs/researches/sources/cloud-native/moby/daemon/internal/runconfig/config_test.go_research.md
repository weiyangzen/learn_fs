<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/config_test.go -->
# sources/cloud-native/moby/daemon/internal/runconfig/config_test.go

Purpose: tests container create request decoding and selected daemon-side validation.

Important APIs and types: `TestDecodeCreateRequest`, `TestDecodeCreateRequestIsolation`, and `TestDecodeCreateRequestPrivileged`.

Control flow: fixture tests decode Unix and Windows API 1.24 JSON and assert image, entrypoint, and memory. Isolation tests marshal minimal requests and assert platform-dependent acceptance of default/process/hyperv/invalid values. Privileged test asserts Windows rejects privileged mode and non-Windows accepts it.

State and persistence: reads fixture JSON files; no persistence.

Dependencies and integration: uses API container types, sysinfo, runtime GOOS checks, containerd errdefs, and gotest assertions.

Risks: tests depend on current platform, so Windows-only rejection paths are not exercised on Linux except through conditional expectations. Fixture coverage is broad but asserts only a few decoded fields.

Test signals: validates backward-compatible request decoding for old fixtures and key platform validation paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/config_test.go -->
