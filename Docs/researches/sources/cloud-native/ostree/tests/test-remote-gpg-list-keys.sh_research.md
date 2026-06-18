# sources/cloud-native/ostree/tests/test-remote-gpg-list-keys.sh

## Purpose
This test validates formatted key listing for remote-specific and global GPG keyrings, including update URLs, subkeys, expiration, and revocation markers.

## Important APIs, Types, And Functions
It uses `OSTREE_GPG_HOME`, `ostree remote gpg-list-keys`, `remote gpg-import --keyring`, fixture key IDs, `which_gpg`, GPG expiration and revocation commands, and exact expected output blocks.

## Control Flow
The script isolates most tests from global keyrings by setting `OSTREE_GPG_HOME` to an empty directory. It checks that an empty remote keyring lists no keys, that global keys do not appear for a specific remote, imports key1 into remote `R1` and compares exact listing output, checks global no-key and global trusted-key output, then conditionally uses GPG to expire and revoke key1 and verifies the listing marks those statuses.

## State And Persistence
State lives in repo-local remote keyrings, global trusted keyring path referenced by `OSTREE_GPG_HOME`, and temporary exported expired/revoked key files.

## Dependencies And Integration Points
This integrates GPG keyring parsing, output formatting, OpenPGP key metadata, Web Key Directory URL rendering, subkey listing, and status propagation from imported key material.

## Risks
The test is intentionally exact about output and timezone (`TZ=UTC`), so formatting changes are breaking. GPG version differences around revocation import are handled by accepting status 0 or 2 in one helper.

## Test Signals
The TAP plan has five non-GPG and two GPG-dependent results. Exact `assert_files_equal` blocks catch changes in key order, dates, UIDs, update URLs, subkeys, and revoked annotations.
