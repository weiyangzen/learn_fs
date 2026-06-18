# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/publish.sh

## Purpose
Publish built bcachefs-tools Debian packages to apt.bcachefs.org.

## Workflow
- Loads signing and publish config from `$STATE_DIR/config`.
- Signs `.deb` and `.ddeb` artifacts with `debsigs`.
- Detects distro jobs with status `done`.
- Creates or updates aptly repos named `$distro-$suite`.
- Removes old `bcachefs-*` packages before adding new artifacts.
- Adds source and binary artifacts with `aptly repo add`.
- Creates snapshots and publishes or switches aptly publications.
- Syncs staging to live with `rsync --delay-updates`.
- Exports GPG public key in binary and armored forms.
- Generates nginx fancyindex footer instructions for users.

## Important Notes
- Avoids aptly `-force-overwrite` because it can corrupt shared pool files by overwriting in place.
- Does not use `rsync --delete`, preserving suites not published in the current run.
- Suite is `snapshot` by default or `release` for tagged releases.

## Dependencies
Requires aptly, gpg, debsigs, rsync, and a configured signing subkey.
