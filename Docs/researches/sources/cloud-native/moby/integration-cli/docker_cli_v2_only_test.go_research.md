## sources/cloud-native/moby/integration-cli/docker_cli_v2_only_test.go

Purpose: registry regression test ensuring daemon operations do not contact Docker registry v1 endpoints. `makefile` creates temporary Dockerfiles; `TestV2Only` uses a mock registry with `/v2/` and `/v1/.*` handlers.

Control flow registers `/v2/` to return 404 and `/v1/.*` to fail the test immediately, starts the daemon with the mock registry as insecure, creates a Dockerfile referencing the registry, then attempts build, run, login, tag, push, and pull. Errors from those operations are intentionally ignored because the signal is whether the v1 handler is touched.

State is the mock registry handler set, temporary build directory, daemon registry configuration, image tags, and login attempt. Dependencies include `internal/testutil/registry`, `net/http`, temp files, and `DockerRegistrySuite`. Risks are that ignored command errors can hide other behavior, but any v1 request remains a hard failure. Test signal is absence of the fatal v1 endpoint hit.
