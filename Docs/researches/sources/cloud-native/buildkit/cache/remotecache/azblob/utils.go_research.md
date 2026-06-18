# sources/cloud-native/buildkit/cache/remotecache/azblob/utils.go

## Purpose

`azblob/utils.go` contains shared Azure Blob remote cache configuration, credential/client creation, object key generation, and blob existence checks. It is used by both Azure exporter and importer.

## Important APIs, Types, and Functions

- Attribute constants define supported cache attrs: `secret_access_key`, `account_name`, `account_url`, `prefix`, `manifests_prefix`, `blobs_prefix`, `name`, and `container`.
- `IOConcurrency` and `IOChunkSize` tune Azure stream upload behavior.
- `Config` stores account URL/name, container, prefixes, names, and secret access key.
- `getConfig` merges attrs with environment variables and defaults.
- `createContainerClient` creates an Azure client using shared key credentials or default Azure credentials, verifies the container, and creates it if absent.
- `manifestKey` and `blobKey` build Azure object keys.
- `blobExists` checks blob properties and maps BlobNotFound to `false`.

## Control Flow

`getConfig` requires `account_url` or `BUILDKIT_AZURE_STORAGE_ACCOUNT_URL`, parses it, derives account name from attrs/env/host, chooses a container from attrs/env/default, applies optional prefix, defaults manifest and blob prefixes, and splits `name` by semicolon with `buildkit` as default. `createContainerClient` chooses shared-key auth when a secret key is supplied, otherwise uses `DefaultAzureCredential`. It checks container properties with a 60-second timeout and creates a missing container with a five-minute timeout. `blobExists` checks properties with a 60-second timeout.

## State and Persistence Behavior

This file has no local persistence. It determines where remote persistent state lives by constructing keys with `filepath.Join(prefix, manifestsPrefix, name)` and `filepath.Join(prefix, blobsPrefix, digest.String())`. It can create the configured Azure container as a side effect.

## Dependencies and Integration Points

The file uses Azure identity and storage SDKs, OCI digests, URL parsing, environment variables, filepath key joining, and pkg/errors. Exporter/importer code relies on it for consistent config and key paths.

## Risks and Edge Cases

- `filepath.Join` uses OS path separators; on Windows this could create backslash-separated blob names unless normalized elsewhere.
- `name` splitting does not filter empty names, so `name=a;;b` can produce an empty manifest key segment.
- Account name derivation assumes the first hostname segment is the Azure storage account.
- Default credentials can involve multiple environment/managed identity flows and may fail later than config parsing.
- Container creation on importer setup may be surprising for read-only import use.

## Test Signals

No direct tests are present in this subset. Exporter/importer behavior depends on these helpers, so unit tests for attr/env precedence, key generation, timeout behavior, and Windows path normalization would be valuable.
