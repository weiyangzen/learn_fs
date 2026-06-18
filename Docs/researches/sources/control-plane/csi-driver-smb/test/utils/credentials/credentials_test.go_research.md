# sources/control-plane/csi-driver-smb/test/utils/credentials/credentials_test.go

## Purpose
This test file verifies Azure credential file generation for both Azure public cloud and Azure China cloud, using both direct environment variables and Prow-style TOML credentials.

## Important APIs, Types, And Functions
Tests are `TestCreateAzureCredentialFileOnAzureChinaCloud` and `TestCreateAzureCredentialFileOnAzurePublicCloud`. Helpers are `withAzureCredentials` and `withEnvironmentVariables`. `fakeAzureCredentials` provides TOML input.

## Control Flow
Each top-level test runs two subtests. The Prow-style path clears direct env vars, writes fake TOML to a temp file, sets `AZURE_CREDENTIALS`, calls `CreateAzureCredentialFile`, then asserts returned fields and JSON file contents. The direct env path sets all env vars and performs the same assertions.

## State, Persistence, And Dependencies
Tests mutate process environment and write `/tmp/azure.json`. They remove both the temp TOML and credential JSON with defers. Dependencies include `testify/assert` and `text/template` for expected JSON.

## Integration Points
The tests cover `credentials.go` and implicitly `testutil.IsRunningInAzureProw` through `AZURE_CREDENTIALS`.

## Risks And Test Signals
Environment variables are not restored with `t.Setenv`, so test ordering or parallelism could leak state. The fixed `/tmp/azure.json` path prevents safe parallel execution. Signals are field equality and `assert.JSONEq` on generated file content.
