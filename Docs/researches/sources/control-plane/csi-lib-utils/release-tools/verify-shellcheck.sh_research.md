# sources/control-plane/csi-lib-utils/release-tools/verify-shellcheck.sh

## Purpose

This verifier runs ShellCheck across repository shell scripts, using a host binary only when it matches the required version, otherwise using a pinned Docker image.

## Important Behavior

The script sources `util.sh`, computes the root directory, disables selected ShellCheck rules, finds `*.sh` files excluding generated/vendor/git paths and git-ignored files, and decides between host `shellcheck 0.6.0` and `koalaman/shellcheck-alpine:v0.6.0` by digest. In Docker mode it starts a long-lived container, execs ShellCheck for each script, aggregates failures, and cleans up through `kube::util::trap_add`.

## State, Dependencies, and Integration

It creates a temporary Docker container named `k8s-shellcheck` and removes it at exit. Dependencies are bash, git, ShellCheck or Docker, and `util.sh`. It is one of the core `.prow.sh` checks for release-tools.

## Risks and Test Signals

The fixed container name can collide with stale or parallel runs. Running Docker requires privileges. Aggregating all failures gives complete diagnostics but can produce large logs. Test signal is the failure list and nonzero exit when any script has lint output.
