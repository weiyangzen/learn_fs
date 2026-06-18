# sources/cloud-native/moby/integration/daemon/testdata/invalid-config-1.json

Purpose: daemon config validation fixture containing a syntactically valid but semantically invalid unknown option.

Important content: `{"unknown-option": true}`. It is consumed by `TestDaemonConfigValidation`.

Control flow: the validation test runs the daemon binary with `--validate --config-file` and expects output indicating failure to configure the daemon from the file.

State and persistence: no runtime state should be created; the fixture is for validation rejection.

Dependencies and integration: depends on daemon config schema validation rejecting unknown directives.

Risks: if config validation becomes permissive or adds an option named `unknown-option`, the expected failure would change.

Test signals: protects strict config validation and useful failure output for unsupported daemon settings.
