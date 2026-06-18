# sources/cloud-native/nydus-snapshotter/pkg/auth/docker_test.go

Purpose: tests Docker config credential lookup with a temporary `DOCKER_CONFIG` directory.

Important APIs and functions: `setupDockerConfig` writes a `config.json` with base64 `auth` entries for Docker Hub and an extra registry, while saving/restoring the old `DOCKER_CONFIG`. `TestDockerCred` instantiates `NewDockerProvider` and calls `GetCredentials`.

Control flow: the test writes config, asserts empty ref and unparsable `foo` fail, checks Docker Hub lookup through the converted host `registry-1.docker.io/foo:bar`, and checks direct lookup for `reg.docker.alibaba-cloud.com/foo:bar`.

State and persistence: modifies process environment and writes a temp Docker config. Cleanup removes the temp directory and restores the original env var.

Dependencies and integration points: exercises Docker CLI config loading and the production `parseReference` host normalization.

Risks and gaps: no test covers credential helpers, partial username/password records, missing config files, token-only auth, or provider renewal. The environment mutation means tests should avoid parallel execution with other Docker-config-dependent tests.

Test signals: confirms base64 auth decoding through Docker configfile and Docker Hub key compatibility.
