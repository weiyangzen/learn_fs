# sources/cloud-native/containerd/.github/workflows/api-release.yml

## Purpose
This workflow publishes GitHub releases for API tags matching `api/v*`.

## Important APIs, Types, And Functions
It sets `GO_VERSION=1.26.4`, defaults to read-only contents permission, checks signed tags, extracts release notes from tag annotation text, uploads the notes as an artifact, and creates a release with `softprops/action-gh-release`.

## Control Flow
On tag push, job `check` checks out the tag, verifies `git tag -v`, derives `stringver`, writes `release-notes.md`, and uploads it. Job `release` needs `check`, requests `contents: write`, downloads the artifact, and creates a non-latest release named `containerd API <version>`.

## State And Persistence
Persistent outputs are a GitHub Release and transient Actions artifacts. No source files are changed.

## Dependencies And Integration Points
It depends on signed annotated tags, `GITHUB_TOKEN`, checkout/upload/download actions, and release action. It separates API releases from full containerd releases.

## Risks
The release body path is `./builds/release-notes.md`, while downloaded artifacts are usually placed under an artifact-name subdirectory; this path should be watched in workflow runs. Signature verification shell precedence is subtle and should be validated. The workflow does not configure SSH allowed signers unlike the main release workflow.

## Test Signals
Dry-run validation is hard because it triggers on tags; evidence comes from successful signed `api/v*` release runs and correct release note body rendering.
