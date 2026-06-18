# sources/cloud-native/cri-o/.github/workflows/patch-release.yml

Purpose: scheduled/manual patch release automation.

Important jobs and flow: runs monthly or manually. On canonical main, checks out full history, sets up Go from `go.mod`, and executes `make release` with `GITHUB_TOKEN`.

State and persistence: may create release branches, tags, PRs, or other artifacts through the `scripts/release` target; this YAML only supplies workflow permissions and environment.

Dependencies and integration: depends on setup-go, repository release scripts, and GitHub token permissions for content and PR writes.

Risks: high-impact automation guarded by repo/branch condition but still capable of modifying release state. Correctness depends on `make release`.

Test signals: workflow success and resulting release artifacts/PRs are the observable signals.
