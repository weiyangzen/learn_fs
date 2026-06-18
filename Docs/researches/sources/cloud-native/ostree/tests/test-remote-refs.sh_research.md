# sources/cloud-native/ostree/tests/test-remote-refs.sh

## Purpose
This test validates `ostree remote refs` output and `--revision` output against a known remote summary.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo2`, `ostree summary -u`, `ostree refs`, `ostree refs --revision`, `ostree remote add --no-sign-verify`, `ostree remote refs`, and `ostree remote refs --revision`.

## Control Flow
The script creates a fake archive remote, regenerates its summary, captures local remote ref listings and ref-to-revision listings, initializes a client archive repo, adds the HTTP remote, then compares `remote refs origin` with the captured list prefixed by `origin:`. It repeats the comparison for `--revision`.

## State And Persistence
The remote summary and refs are persisted in the fake server repo. The client stores only remote configuration for listing; no pull is required.

## Dependencies And Integration Points
This integrates remote summary fetching/parsing, ref rendering, remote prefix formatting, and revision output ordering.

## Risks
Remote ref listing must match local listing semantics while adding remote prefixes. Ordering or whitespace changes can break exact comparisons.

## Test Signals
Two TAP results cover plain remote refs and revisions. `assert_files_equal` catches any output mismatch.
