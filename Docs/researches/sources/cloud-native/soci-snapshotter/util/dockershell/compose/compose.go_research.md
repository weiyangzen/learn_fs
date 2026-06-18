# sources/cloud-native/soci-snapshotter/util/dockershell/compose/compose.go

Purpose: this file provides Docker Compose-based test environments and returns per-service container exec handles.

Important APIs and types: `Supported` checks Docker and `docker compose`. `Compose` holds service-name to `*exec.Exec` map plus cleanup functions. Options support build args and stdio redirection. `Build` only builds images. `Up` starts services from YAML without an explicit build step. `New` builds then starts services. `Get`, `List`, and `Cleanup` manage the resulting environment.

Control flow: functions write provided Compose YAML to a temporary context, call Docker Compose commands with that file, parse `docker compose ps --services`, resolve each service's container ID with `ps -q`, and wrap it with `dexec.New`. Cleanups tear down compose projects and remove temporary contexts. `Build` registers repeated `down --rmi all` cleanup functions before removing the context.

State and persistence: creates temporary directories under the system temp path and Docker containers/images/volumes/networks managed by Compose. Cleanup errors are joined and returned.

Dependencies and integration points: integrates `os/exec`, Docker Compose CLI, local `dockershell/exec`, and xid-generated unique temp names. Used by integration tests that need multi-container fixtures.

Risks: if a command fails before returning a `Compose`, accumulated cleanups are not automatically run, so callers may leak temp directories or compose resources on setup failure. `Build` appends three identical image-removal cleanups, likely to handle dependency ordering but unusual. Compose project naming is implicit from temp directory, and stdio handling differs between full stdio and stderr-only commands.

Test signals: no direct tests in this subset. Validation requires Docker-enabled integration tests.
