# sources/cloud-native/ostree/tests/test-signed-pull.sh

## Purpose
This test validates commit signature verification during pulls using the signapi dummy and ed25519 backends, including remote configuration parsing, missing key failures, inline key options, re-pulling missing commit metadata, and invalid sign-verify arguments.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1`, `ostree remote add` with `--set` and `--sign-verify=...`, `ostree config set/unset`, `ostree commit --sign` or `--sign-from-file`, `ostree summary -u`, `ostree pull --depth=0`, `repo_init`, and helper `test_signed_pull`.

## Control Flow
`repo_init` recreates the client repo with GPG verification disabled and summary sign verification disabled. `test_signed_pull` creates a signed remote commit, temporarily removes its remote `.commitmeta` file to ensure pull fails without signature metadata, restores it, pulls successfully, deletes the local `.commitmeta`, and pulls again to ensure signatures for stored commits are refetched. The dummy section checks failures with no keys, wrong keys, bad key file, correct config key, inline remote option, explicit sign type, missing configured keys, unknown sign type, and invalid remote-add sign-verify syntax. If ed25519 support exists, it signs from a secret file and verifies using config key, config file with wrong keys plus correct key, file-only correct key, and inline key option.

## State And Persistence
State includes remote and local commit metadata object files, remote config keys such as `sign-verify` and `verification-dummy-key`, temporary ed25519 key files, refs, summaries, and pulled objects.

## Dependencies And Integration Points
This integrates signapi pull verification, remote option parser, commit metadata fetching, summary refresh, dummy backend gating, and optional ed25519 support.

## Risks
Pull must not accept signed commits without trusted keys or without commit metadata. Re-pulling metadata for already stored commits is easy to miss because object content is already present. Inline option parsing must reject unknown systems and malformed key references.

## Test Signals
The TAP plan has twenty results with ed25519 skips when unavailable. Expected failure messages include missing keys, unknown sign type, invalid key reference, and no-signature pull failure.
