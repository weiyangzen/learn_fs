<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/test -->
# sources/cloud-native/buildkit/hack/test

Purpose: main BuildKit test runner wrapper that normalizes environment, tags, packages, integration modes, and helper services before invoking Go tests.

Important APIs, types, and functions: bash script sources `hack/util`, configures fail-fast shell options, interprets environment variables and arguments for test selection, prepares Docker/BuildKit integration settings, and runs `go test` with appropriate tags, package lists, and flags.

Control flow and state: mostly orchestration. It may start or depend on Docker resources, temporary directories, and fixture setup, then exits with the test command status.

Dependencies and integration: central integration point for CI and local testing. Depends on Go, Docker, BuildKit test fixtures, `hack/util`, and package-specific test expectations.

Risks and test signals: broad environment coupling makes failures sensitive to Docker daemon state, privileges, rootless mode, and test tags. The best signal is successful CI and targeted local invocations with representative package/tag combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/test -->
