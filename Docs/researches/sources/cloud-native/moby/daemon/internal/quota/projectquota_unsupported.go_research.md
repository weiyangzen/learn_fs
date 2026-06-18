<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/projectquota_unsupported.go -->
# sources/cloud-native/moby/daemon/internal/quota/projectquota_unsupported.go

Purpose: provides quota stubs for unsupported builds/platforms.

Important APIs and types: `NewControl`, `SetQuota`, and `GetQuota`.

Control flow: all functions return `ErrQuotaNotSupported`.

State and persistence: none.

Dependencies and integration: compiled when not Linux, when cgo is disabled, or when disk quota is excluded.

Risks: methods on a nil `*Control` can still return not-supported without dereferencing state, but callers should not assume quota support after `NewControl` fails.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/projectquota_unsupported.go -->
