## sources/cloud-native/moby/integration-cli/fixtures/auth/docker-credential-shell-test

Purpose: shell credential-helper fixture implementing the Docker credential helper protocol commands `store`, `get`, `erase`, and `list` for auth integration tests.

Control flow branches on `$1`. `store` reads JSON from stdin, extracts `ServerURL`, `Username`, and `Secret` with `jq`, hashes the server with `sha1sum`, writes credentials under `$TEMP/$hash`, and updates a JSON server-to-username list. `get` hashes stdin and returns the stored payload or exits with `credentials not found in native keychain`. `erase` deletes the credential file and removes the server from the list. `list` returns `{}` or the saved list.

State persists in temporary files under `$TEMP`, especially `shell_test_list.json` and hashed credential files. Dependencies are bash, `jq`, `sha1sum`, `awk`, and `$TEMP`. Risks include unquoted JSON values, concurrent tests sharing `$TEMP`, and missing list file during erase. Test signals are JSON stdout payloads and nonzero exit on unknown or missing credentials.
