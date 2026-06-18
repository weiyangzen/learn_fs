# sources/cloud-native/moby/integration/daemon/testdata/malformed-config.json

Purpose: daemon config validation fixture for malformed JSON.

Important content: the file contains only `{`, an incomplete JSON object.

Control flow: `TestDaemonConfigValidation` passes this file to `dockerd --validate --config-file` and expects failure output, exercising JSON syntax error handling.

State and persistence: no daemon state should be written because parsing fails before configuration is accepted.

Dependencies and integration: depends on the daemon's JSON decoder and validation command path.

Risks: low. The exact user-facing error text may change, but the test only checks a broad failure phrase.

Test signals: ensures malformed config files are rejected during daemon validation instead of being ignored or treated as empty config.
