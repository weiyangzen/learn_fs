<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/cred.json -->
# sources/cloud-native/overlaybd/src/example_config/cred.json

Purpose: Example Docker-style credential file.

APIs and control flow: Contains top-level `auths` keyed by registry host, with explicit `username` and `password` fields. `load_cred_from_file` parses this into `AuthConfig`, and `parse_auths` matches host/path prefixes against requested blob URLs.

State and persistence: Installed to `/opt/overlaybd/cred.json` as sample data unless replaced.

Dependencies and integration: Referenced by default `credentialConfig` examples.

Risks and test signals: Placeholder credentials must not be used in production. Tests should verify both explicit username/password and base64 `auth` variants.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/cred.json -->
