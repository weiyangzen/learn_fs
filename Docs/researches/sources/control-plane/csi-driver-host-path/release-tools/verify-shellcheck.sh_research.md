## sources/control-plane/csi-driver-host-path/release-tools/verify-shellcheck.sh

Purpose: runs shellcheck over shell scripts in a repo, using either a matching host binary or a pinned Docker image.

Control flow sources `util.sh`, finds non-ignored `*.sh` files outside excluded directories, detects shellcheck 0.6.0, otherwise starts a long-lived Docker container mounted at the root, runs shellcheck with disabled rules 1090 and 2230 for each script, collects all lint outputs, and fails if any exist. Cleanup removes the container through a composed trap.

State is a Docker container named `k8s-shellcheck` when host shellcheck is unavailable. Dependencies are bash, git check-ignore, Docker, shellcheck image, and util trap helper. Risks include fixed container name collisions, old shellcheck version, dependency on Docker in CI, and excluding only `*.sh` files while some executable shell snippets may lack extension. Test signal is aggregate lint output.
