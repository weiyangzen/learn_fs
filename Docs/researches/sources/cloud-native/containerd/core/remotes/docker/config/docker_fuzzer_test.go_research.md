<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/docker_fuzzer_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/config/docker_fuzzer_test.go

Purpose: fuzz target for `parseHostsFile`.

Important APIs/types/functions: `FuzzParseHostsFile` uses `go-fuzz-headers` to create arbitrary files and TOML bytes under a temp dir, then calls `parseHostsFile`.

Control flow: fuzz input is split between generated filesystem fixtures and bytes passed as the hosts file. Errors are intentionally ignored because the objective is crash/panic resistance.

State and persistence: temporary directories and generated files only.

Dependencies and integration points: protects Docker registry configuration parsing from malformed TOML and file path combinations.

Risks covered: parser robustness, relative path handling, and type assertion paths. It does not assert semantic correctness for accepted configs.

Test signals: fuzz-only coverage complements deterministic `hosts_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/docker_fuzzer_test.go -->
