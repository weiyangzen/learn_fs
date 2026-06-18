# sources/cloud-native/ostree/tests/test-summary-view.sh

## Purpose
This test verifies human-readable and raw viewing of a pulled summary file.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1`, `ostree commit`, `ostree summary -u`, `ostree pull --mirror`, `OSTREE summary --view`, and `OSTREE summary --raw`.

## Control Flow
The script creates a signed or unsigned fake remote depending on GPGME availability, adds an `other` branch, regenerates the summary, initializes a client repo, adds the remote with GPG verification disabled, and mirror-pulls it. It then runs `ostree summary --view` in the repo and checks branch names and metadata labels, followed by `ostree summary --raw` and checks raw tuple and metadata serialization.

## State And Persistence
The mirror pull persists `repo/summary`, refs, and objects. Output files `summary.txt` and `raw-summary.txt` are temporary assertions.

## Dependencies And Integration Points
This integrates summary generation, mirror pull storing the summary, CLI default repo/context behavior for `OSTREE summary`, and summary rendering code.

## Risks
View output is user-facing and can break tests if labels change. Raw output must retain GVariant structure for consumers and diagnostics.

## Test Signals
Two TAP results cover view and raw view. Assertions check branches `main` and `other`, `ostree.summary.last-modified`, commit timestamp/version labels, and raw tuple strings.
