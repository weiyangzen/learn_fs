# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/nydusd_test.go

Purpose: tests config generation, Unix-socket readiness polling, mount command behavior, and unmount paths for `Nydusd`.

Important APIs and flow: `TestMakeConfig` asserts default localfs config and missing backend config errors. Readiness tests create Unix listeners/HTTP handlers that return `RUNNING` or invalid/non-running responses. Mount tests use fake `nydusd` scripts and PATH-injected `umount` scripts to validate successful readiness and binary failure. `TestUmount` covers missing mount path, successful command invocation, command failure, and non-silent output path.

State and persistence: uses temp config files, Unix sockets, temporary executable scripts, and environment PATH overrides.

Dependencies and integration: exercises real HTTP-over-Unix behavior without real `nydusd`. It verifies integration contracts around daemon state JSON and command invocation.

Risks and test signals: good coverage for wrapper mechanics. It does not verify actual FUSE mount behavior, cache behavior, or timeout duration except through controlled fake process/socket timing.
