<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/Makefile -->
# sources/cloud-native/containers-storage/Makefile

- Purpose: Central build/test/lint/docs automation for containers/storage.
- Important targets: Local binary and cross builds, unit and integration tests, validation, lint, docs/manpage generation, vendor maintenance, and tool installation.
- Control flow and state: Make variables control storage driver, transient mode, build tags, install paths, and test environment. Targets invoke Go commands, helper scripts, and docs tools.
- Dependencies and integration: Integrates with Cirrus scripts, docs Makefile, Go module tooling, and integration test suite.
- Risks: Environment-sensitive variables such as storage driver and rootless setup can change behavior; make target dependencies need to keep generated tools current.
- Test signals: CI executes `local-binary`, `local-cross`, `local-test-integration`, `local-test-unit`, `local-validate`, and `lint`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/Makefile -->
