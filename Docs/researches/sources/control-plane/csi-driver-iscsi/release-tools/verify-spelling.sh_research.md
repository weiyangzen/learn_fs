# sources/control-plane/csi-driver-iscsi/release-tools/verify-spelling.sh

Purpose: checks spelling across tracked repository files using `misspell`.

Important APIs and types: `TOOL_VERSION=v0.3.4`, optional root argument, temp install directory, and cleanup trap.

Control flow: strict shell mode, install misspell into a temp directory with `go install` if absent, run `git ls-files -z | grep -z -v vendor | xargs -0 misspell --`, prefix errors, and exit nonzero when the error log is non-empty.

State and persistence: temp directory only; no repo writes.

Dependencies and integration: used by release-tools and NFS Prow scripts. Depends on Go, git, grep with null-data support, and misspell.

Risks: excludes paths containing `vendor` by grep substring, which may be broader than intended. Tool version is old and installed dynamically.

Test signals: printed `error:` lines and nonzero exit.
