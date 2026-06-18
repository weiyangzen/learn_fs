<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/helpers/azurite.go -->
# sources/cloud-native/buildkit/util/testutil/helpers/azurite.go

Purpose: starts an Azurite blob service for integration tests that need Azure Blob Storage behavior.

Important APIs and types: `AzuriteOpts`, `NewAzuriteServer`, and `waitAzurite`.

Control flow: verifies `azurite-blob` exists, reserves an ephemeral localhost port, starts Azurite with account env vars and temp location, waits up to 15 seconds by issuing blob list requests, registers cleanup in a `MultiCloser`, and returns account-scoped service URL and cleanup function.

State and persistence: creates a temp Azurite data directory and child process; cleanup stops the process through integration helpers.

Dependencies and integration: depends on external `azurite-blob` binary, BuildKit integration sandbox logs/context, HTTP readiness checks, and account credentials.

Risks: port is selected by opening then closing a listener before process start, so another process could theoretically claim it. Missing binary skips via returned error to caller. Readiness accepts any successful HTTP response.

Test signals: helper itself has no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/helpers/azurite.go -->
