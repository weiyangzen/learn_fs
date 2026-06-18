<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/errors.go -->
# sources/cloud-native/moby/daemon/internal/runconfig/errors.go

Purpose: centralizes runconfig validation and invalid JSON error types.

Important APIs and types: `validationError` and `invalidJSONError`.

Control flow: `validationError` creates containerd invalid-argument errors. `invalidJSONError` prefixes JSON decode errors, unwraps the original error, and implements `InvalidParameter`.

State and persistence: none.

Dependencies and integration: used by create request decoding and validation so API handlers can classify errors.

Risks: callers comparing exact error strings will see `invalid JSON: ` prefix. Validation errors carry only message text.

Test signals: indirectly covered by runconfig tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/errors.go -->
