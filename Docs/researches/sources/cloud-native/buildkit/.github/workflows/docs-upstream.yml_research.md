# sources/cloud-native/buildkit/.github/workflows/docs-upstream.yml

## Purpose
Validates BuildKit docs against Docker’s upstream documentation validation workflow when relevant docs or this workflow change.

## APIs, Flow, And State
On selected pushes and PR paths, the `validate` job calls `docker/docs/.github/workflows/validate-upstream.yml@main` with `module-name: moby/buildkit`. No local steps run in this repo.

## Dependencies And Integration
Depends on the external `docker/docs` reusable workflow and intentionally uses `@main` so validation follows current Docker docs rules. Zizmor unpinned-use warning is explicitly ignored in the comment because freshness is desired.

## Risks And Test Signals
External workflow changes can break BuildKit PRs without local changes. Test signal is upstream docs validation status; persistence is limited to workflow logs.
