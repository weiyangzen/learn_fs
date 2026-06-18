# sources/cloud-native/cri-o/.muse/config.toml

Purpose: Muse static-analysis configuration.

Important settings and flow: sets `build = "make"`, ignores the `RESOURCE_LEAK` rule, and excludes `vendor/**` plus `internal/log/log_test.go`.

State and persistence: no state; controls external Muse analysis behavior.

Dependencies and integration: consumed by Muse tooling when run against the repository.

Risks: ignoring resource leaks and a specific log test can hide real issues in those scopes, though likely chosen to suppress false positives.

Test signals: Muse scan results under this configuration.
