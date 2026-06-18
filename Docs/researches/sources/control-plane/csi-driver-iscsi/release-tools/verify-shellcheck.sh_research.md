# sources/control-plane/csi-driver-iscsi/release-tools/verify-shellcheck.sh

Purpose: runs ShellCheck over shell scripts in a repository, using an exact host ShellCheck version or a pinned Docker image.

Important APIs and types: configurable `ROOT` argument, `SHELLCHECK_VERSION=0.6.0`, pinned `SHELLCHECK_IMAGE`, disabled checks `SC1090` and `SC2230`, and helper functions `join_by`, `create_container`, and `remove_container`.

Control flow: sources `util.sh`, discovers `*.sh` files excluding hidden output, `.git`, vendor, and git-ignored files, detects host shellcheck version, otherwise starts a long-lived Docker container mounted at the repo root, runs shellcheck for every script, collects failures, and exits nonzero with all lint output if any fail.

State and persistence: may create and remove a Docker container named `k8s-shellcheck`. No repo files are modified.

Dependencies and integration: used by release-tools `.prow.sh`; depends on bash, git, find, Docker, ShellCheck, and `util.sh` trap handling.

Risks: pinned ShellCheck 0.6.0 is old. Docker is required when the exact host version is absent. Files without `.sh` extension are not linted even if executable shell.

Test signals: ShellCheck output and Prow verifier status.
