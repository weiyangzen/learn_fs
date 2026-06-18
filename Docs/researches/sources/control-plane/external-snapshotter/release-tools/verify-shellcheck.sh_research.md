<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-shellcheck.sh -->
# sources/control-plane/external-snapshotter/release-tools/verify-shellcheck.sh

## Purpose
`verify-shellcheck.sh` lints repository shell scripts with a pinned ShellCheck version, using either a host binary or a pinned Docker image.

## Important APIs, Types, and Functions
Important functions are `join_by`, `create_container`, and `remove_container`. It sources `util.sh`, sets `SHELLCHECK_VERSION=0.6.0`, `SHELLCHECK_IMAGE` with digest, `SHELLCHECK_CONTAINER=k8s-shellcheck`, disables rules `SC1090` and `SC2230`, discovers `*.sh` files excluding `_`, `.git`, and `vendor` paths and git-ignored files, then runs shellcheck on each script.

## Control Flow, State, and Persistence
The script changes to the target root, builds `all_shell_scripts`, detects whether the host ShellCheck exactly matches the pinned version, otherwise starts a long-lived Docker container with the root mounted and registers cleanup through `kube::util::trap_add`. It collects lint output in an array, prints success when empty, or prints all errors and exits false.

## Dependencies and Integration Points
It depends on Bash, Docker when the host ShellCheck version is absent or different, `git check-ignore`, `find`, and the pinned shellcheck image. It integrates with release-tools `make verify` style checks and uses `util.sh` cleanup helpers.

## Risks and Test Signals
Risks include Docker availability, a fixed container name colliding with concurrent runs, old ShellCheck rules missing modern issues, and script discovery excluding only some generated/cache paths. Signals are per-script lint output or the success message stating all shell files pass lint.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-shellcheck.sh -->
