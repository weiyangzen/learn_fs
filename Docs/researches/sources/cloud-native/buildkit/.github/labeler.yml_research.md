# sources/cloud-native/buildkit/.github/labeler.yml

## Purpose
Defines path-based pull request labels for BuildKit areas. Labels cover project metadata, CI, testing, API, storage/cache, client, LLB, buildctl/buildkitd, CDI, dependencies, docs, Dockerfile frontend, examples, executor/exporter/frontend/hack/session/solver/source/sourcepolicy/util/worker, and Windows-specific changes.

## APIs, Flow, And State
The file is consumed by `actions/labeler`. Each top-level key is a label and each value is a matcher using `changed-files`, `any-glob-to-any-file`, `all-globs-to-all-files`, or `all` clauses. Matching occurs during PR workflow execution and persists only through GitHub labels.

## Dependencies And Integration
Tied to `.github/workflows/labeler.yml`. It mirrors the repository’s directory structure, so ownership and CI routing depend on these glob boundaries. `area/project` explicitly excludes workflow changes so `.github/workflows/**` maps to `area/ci`.

## Risks And Test Signals
Glob drift is the main risk: moved files may stop labeling, and broad globs can over-label PRs. Negated patterns in `all` blocks require careful validation because a small syntax mistake can change label scope. Test signal is labeler workflow output on PRs and synthetic PRs that touch representative paths.
