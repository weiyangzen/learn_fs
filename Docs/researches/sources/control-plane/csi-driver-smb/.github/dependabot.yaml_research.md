## sources/control-plane/csi-driver-smb/.github/dependabot.yaml

Purpose: configures Dependabot updates for the SMB CSI repo. It checks Go modules at `/`, GitHub Actions workflows at `/`, and Docker dependencies under `/cmd/smbplugin/`.

Important behavior: all ecosystems run daily and cap open PRs at one. PRs receive dependency, no-release-note, and ok-to-test labels; Docker updates also get `kind/cleanup` and run at 01:00 Asia/Shanghai.

State is GitHub Dependabot service state and generated pull requests. Dependencies are GitHub's `gomod`, `github-actions`, and `docker` ecosystem parsers. Risks include serialized update throughput from the one-PR cap, noisy daily Docker updates, and labels coupling to repository automation. Test signal appears as Dependabot PRs that then run the normal CI matrix.
