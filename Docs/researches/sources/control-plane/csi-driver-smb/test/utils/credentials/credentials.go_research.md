# sources/control-plane/csi-driver-smb/test/utils/credentials/credentials.go

## Purpose
This package generates a temporary Azure credential JSON file for SMB tests from environment variables or Prow-provided TOML credentials.

## Important APIs, Types, And Functions
Constants define cloud names, default locations, env vars, resource group prefix, and `/tmp/azure.json`. Types are `Config`, `FromProw`, and `Credentials`. Public APIs are `CreateAzureCredentialFile(isAzureChinaCloud bool)` and `DeleteAzureCredentialFile`. Internal functions are `getCredentialsFromAzureCredentials` and `parseAndExecuteTemplate`.

## Control Flow
`CreateAzureCredentialFile` selects public or China env vars, generates a UUID resource group if absent, applies default location, and prefers complete direct env credentials. If incomplete and running in Azure Prow, it reads `AZURE_CREDENTIALS` TOML and converts it to JSON. Otherwise it returns an error listing required env vars. Template execution writes `/tmp/azure.json`.

## State, Persistence, And Dependencies
The main persistent artifact is `/tmp/azure.json`, containing secrets in plain JSON. Dependencies include `go-toml/v2`, `pborman/uuid`, `html/template`, and `testutil` Prow detection.

## Integration Points
Azure helper clients and test setup consume the generated credential file. The file format mirrors Azure File CSI driver credential expectations.

## Risks And Test Signals
Secrets are written to a fixed world-default temp path via `os.Create`, so concurrent tests can collide and file permissions depend on umask. In Azure Prow, `cloud` is based on requested test mode while tenant/client values come from TOML. Signals are returned credential structs, file contents, and cleanup success.
