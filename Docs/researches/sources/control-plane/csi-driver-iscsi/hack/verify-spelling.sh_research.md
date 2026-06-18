## sources/control-plane/csi-driver-iscsi/hack/verify-spelling.sh

Purpose: spelling verifier for tracked repository files.

Control flow resolves repo root, creates a temp directory, installs misspell v0.3.4 if needed, runs `git ls-files | grep -v vendor | xargs misspell`, prints findings prefixed with `error:`, and exits nonzero when findings exist. State is temp install/log directory.

Dependencies are bash, Go install, git, xargs, and misspell. Risks include filenames with spaces, old misspell path, broad vendor-only exclusion, and no custom domain word list unlike the GitHub codespell workflow. Test signal is `verify-all.sh`.
