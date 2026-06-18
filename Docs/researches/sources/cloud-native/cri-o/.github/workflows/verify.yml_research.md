# sources/cloud-native/cri-o/.github/workflows/verify.yml

Purpose: PR and branch verification workflow for linting, formatting, documentation, dependency, typo, and generated-file checks.

Important jobs and flow: triggered on manual, tags, main/release/update-nixpkgs branches, and PRs. Jobs run golangci-lint, markdownlint, shellcheck, shfmt, trailing-space grep, docs validation, vendor verification, log capitalization, config-template validation, dependency verification, typos, mdtoc, and prettier dry-run. Concurrency cancels older runs per ref.

State and persistence: mostly read-only; some jobs generate files locally and then use tree-status checks to require committed output.

Dependencies and integration: uses Makefile verify targets, setup-go, markdownlint action, shellcheck problem matchers, typos, and prettier action.

Risks: many style gates can fail due to tool version drift, although versions are mostly pinned in Makefile or action references. Markdown lint excludes README, vendor, docs, and `.github`.

Test signals: clean workflow indicates source formatting, generated docs/config, vendor state, dependency policy, and spelling are acceptable.
