## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/index.go

Purpose: shared existing-index push policy flags and helper.

Important APIs/types/functions: `ExistingIndexFlag`, policy constants `warn`, `skip`, `allow`, `SupportedExistingIndexOptions`, `ExistingIndexFlags`, and generic `SupportedArg`.

Control flow: no command execution; push command validates and switches behavior based on the chosen policy.

State and persistence: none directly.

Dependencies and integration: used by `soci push` to handle remote referrer conflicts before uploading.

Risks and test signals: validation is opt-in by callers; unsupported values are not rejected by flag parsing itself. No direct tests here.
