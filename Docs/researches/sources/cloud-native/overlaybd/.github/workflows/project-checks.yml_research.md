<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/project-checks.yml -->
# sources/cloud-native/overlaybd/.github/workflows/project-checks.yml

Purpose: Repository hygiene workflow for DCO, short subject, dangling whitespace, and license/header validation.

APIs and control flow: Runs on pushes to `main` and all pull requests. It checks out the repository under a GOPATH-style path, installs `git-validation` and `ltag`, computes the commit range from PR commits API or push event JSON, then runs `git-validation` and `ltag`.

State and persistence: Only uses the Actions workspace and environment variables such as `GOPATH`, `GITHUB_COMMIT_URL`, and `GITHUB_EVENT_PATH`.

Dependencies and integration: Depends on Go 1.19, `jq`, `curl`, `git-validation`, `containerd/ltag`, and the local `script/validate/template`.

Risks and test signals: Empty `REPO_ACCESS_TOKEN` relies on unauthenticated API access for PR commit lookup. Validation passes when commit metadata and headers meet containerd project rules.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/project-checks.yml -->
