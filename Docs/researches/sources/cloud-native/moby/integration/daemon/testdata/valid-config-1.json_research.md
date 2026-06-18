# sources/cloud-native/moby/integration/daemon/testdata/valid-config-1.json

Purpose: daemon config validation fixture containing a minimal valid setting.

Important content: `{"debug": true}`. It is consumed by `TestDaemonConfigValidation`.

Control flow: the validation test passes this file to `dockerd --validate --config-file` and expects `configuration OK`, proving recognized settings pass validation.

State and persistence: the file represents daemon debug configuration, but in validation mode it should not start or persist daemon runtime state.

Dependencies and integration: depends on daemon config schema recognizing the `debug` directive.

Risks: low, although future config schema changes could rename or deprecate the key.

Test signals: confirms the validation path accepts a simple real daemon option, complementing empty and invalid fixtures.
