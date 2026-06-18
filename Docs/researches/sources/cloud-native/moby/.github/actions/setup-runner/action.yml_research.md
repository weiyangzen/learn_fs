<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/actions/setup-runner/action.yml -->
# sources/cloud-native/moby/.github/actions/setup-runner/action.yml

## Purpose
Provides a composite GitHub Action that prepares Linux runners for Moby tests by loading required kernel modules, reloading overlay with `redirect_dir=off`, enabling Docker daemon experimental/live-restore/IPv6 configuration, running a best-effort kernel config check, and printing `docker info`.

## Important APIs, Types, And Functions
- Composite `runs.steps` invoke bash scripts directly.
- `modprobe ip_vs`, `ipv6`, `ip6table_filter`, and overlay reload set kernel module state.
- `jq` merges Docker daemon settings into `/etc/docker/daemon.json`.
- `sudo service docker restart` applies daemon configuration.
- `./contrib/check-config.sh || true` reports kernel support without failing.

## Control Flow
Workflows call this action before building or running tests. The action first adjusts kernel modules, then daemon JSON, restarts Docker, runs config diagnostics, and prints final Docker state.

## State And Persistence
It mutates runner-global kernel module state and `/etc/docker/daemon.json` for the remainder of the job. It does not persist beyond the ephemeral GitHub runner.

## Dependencies And Integration Points
Used by Linux unit, integration, validation, and reusable test workflows. Depends on privileged `sudo`, Docker service availability, `jq`, and repository checkout for `contrib/check-config.sh`.

## Risks And Edge Cases
Reloading overlay can fail if the module is in use. The daemon config merge assumes valid JSON and service management via `service`. Since `check-config.sh` is non-fatal, missing kernel features may only surface later as test failures.

## Test Signals
Successful action execution and `docker info` output are readiness signals. Later integration tests validate whether the runner setup was sufficient.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/actions/setup-runner/action.yml -->
