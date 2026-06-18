<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/envvars.go -->
# sources/cloud-native/moby/client/envvars.go

Purpose: centralizes Docker-compatible environment variable names used by client options.

Important APIs/constants: `EnvOverrideHost` (`DOCKER_HOST`), `EnvOverrideAPIVersion` (`DOCKER_API_VERSION`), `EnvOverrideCertPath` (`DOCKER_CERT_PATH`), and `EnvTLSVerify` (`DOCKER_TLS_VERIFY`), with package comments explaining behavior.

Control flow and dependencies: no imports or runtime control flow. Constants are consumed by `FromEnv`, `WithHostFromEnv`, `WithAPIVersionFromEnv`, and TLS env setup.

State and integration behavior: no persistence. Integration point is compatibility with Docker CLI and daemon environment conventions.

Risks and test signals: changing names is a breaking compatibility issue. `client_options_test.go` and `client_test.go` indirectly protect these constants through env-based setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/envvars.go -->
