# sources/compression/zstd/.github/dependabot.yml

Purpose: Dependabot configuration for GitHub Actions dependency updates.

Important behavior: version 2 config contains one update rule for the `github-actions` ecosystem at repository root, scheduled monthly. That means pinned actions in `.github/workflows` are periodically proposed for updates.

State, dependencies, and integration: no runtime state is persisted in this file. It integrates with GitHub Dependabot and the workflow files that pin action versions or SHAs. Because many workflows use SHA-pinned actions with tag comments, Dependabot can help keep supply-chain pins current while preserving reviewable diffs.

Risks and test signals: monthly cadence reduces noise but can leave action security fixes unapplied for several weeks. Dependabot PRs themselves become test signals because all affected workflows should run on the proposed update branch. The file does not manage Docker images, apt packages, or language dependencies.
