# sources/cloud-native/moby/hack/buildkit-ref

## Purpose
Outputs the BuildKit repository and ref used by the current Moby checkout, intended for GitHub Actions environment export.

## Important APIs and Types
Shell function `resolve_github_commit_sha(repo, ref)` uses `gh api` or `curl` plus `jq`. Main variables are `buildkit_pkg`, `buildkit_ref`, and `buildkit_repo`.

## Control Flow, State, and Persistence
The script queries `go list -m` for `github.com/moby/buildkit`, respects module replacement path/version, strips `github.com/`, resolves pseudo-version commit suffixes to full GitHub SHAs, and prints `BUILDKIT_REPO=` and `BUILDKIT_REF=` lines. It writes no files itself.

## Dependencies, Integration Points, Risks, and Test Signals
Requires Go module metadata and GitHub API access for pseudo-version expansion; optionally uses `GH_TOKEN`. Risks include non-GitHub BuildKit replacements, API rate limits, missing `jq`, or pseudo-version parsing assumptions. CI jobs that consume `$GITHUB_ENV` are the integration signal.
