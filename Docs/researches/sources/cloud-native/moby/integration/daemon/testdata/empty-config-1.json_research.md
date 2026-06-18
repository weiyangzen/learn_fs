# sources/cloud-native/moby/integration/daemon/testdata/empty-config-1.json

Purpose: daemon config validation fixture representing a completely empty config file.

Important content: the file contains no JSON tokens. It is consumed by `TestDaemonConfigValidation` with `dockerd --validate --config-file`.

Control flow: the daemon validation test passes this file path and expects output containing `configuration OK`, proving the daemon treats an empty config file as valid/no-op configuration.

State and persistence: no state is stored beyond the file's empty content. Its meaning is the absence of directives.

Dependencies and integration: depends on daemon config loading accepting zero-byte config files. It integrates with the daemon binary validation path rather than the client API.

Risks: if config parsing policy changes to require valid JSON, this fixture would become invalid. The test relies on path resolution through integration testdata.

Test signals: protects compatibility for deployments where an empty daemon config file exists.
