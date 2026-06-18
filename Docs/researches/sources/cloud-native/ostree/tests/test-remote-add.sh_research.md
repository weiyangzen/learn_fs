# sources/cloud-native/ostree/tests/test-remote-add.sh

## Purpose
This shell test validates the `ostree remote` management CLI for adding, listing, showing URLs, deleting, inheriting parent repo remotes, duplicate handling, and forced replacement.

## Important APIs, Types, And Functions
It uses `setup_test_repository`, `$OSTREE remote add`, `remote show-url`, `remote list`, `remote list --show-urls`, `remote delete`, `--if-not-exists`, `--if-exists`, `--force`, `ostree config set core.parent`, and assertions from `libtest.sh`.

## Control Flow
The script sets up a bare test repo, adds a normal remote and a no-sign-verify remote, verifies duplicate addition fails, checks idempotent add with `--if-not-exists`, lists names without URLs and then with URLs, configures a parent repository with its own remote and verifies inherited listing, deletes existing and nonexistent remotes with and without `--if-exists`, confirms removed remotes cannot be shown, checks remaining names, rejects incompatible `--if-not-exists --force`, and finally overwrites a remote URL with `--force`.

## State And Persistence
State lives in `repo/config` and parent repo config. Deletion removes remote stanzas and `show-url` visibility. The test does not pull objects, so object storage is not central.

## Dependencies And Integration Points
This integrates the CLI remote parser, repository config writing, parent repository lookup, and remote list rendering. It depends on `$OSTREE` being preconfigured by the harness to target the test repo.

## Risks
Remote management can accidentally expose URLs in default listings, ignore parent remotes, fail to delete associated configuration, or allow conflicting flags. Forced replacement must update the URL without creating duplicate stanzas.

## Test Signals
The TAP plan has sixteen results, with regex checks on list output and stderr checks for failure paths.
