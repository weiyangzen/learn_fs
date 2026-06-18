<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/errors.go -->
# sources/cloud-native/moby/daemon/internal/quota/errors.go

Purpose: defines the quota-not-supported error used across quota implementations.

Important APIs and types: `ErrQuotaNotSupported` and `errQuotaNotSupported`, which implements Docker `errdefs.ErrNotImplemented`.

Control flow: no control flow beyond `Error` and marker method `NotImplemented`.

State and persistence: none.

Dependencies and integration: returned by unsupported quota builds and by Linux project quota setup when prerequisites are missing.

Risks: message text is generic and may not identify whether filesystem, kernel, namespace, or build tags caused lack of support.

Test signals: indirectly exercised by quota tests when skipped/unsupported.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/errors.go -->
