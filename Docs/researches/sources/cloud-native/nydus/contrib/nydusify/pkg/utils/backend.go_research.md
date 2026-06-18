<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/backend.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/backend.go

## Purpose

This file builds and rewrites registry backend configuration used when nydusify and nydusd access external image blobs through registries and optional proxies.

## Important APIs, Types, and Functions

`RegistryBackendConfig` models registry scheme, host, repository path, auth, skip-verify, and proxy settings. `BackendProxyConfig` models proxy URL, cache directory, fallback, ping URL, and timeouts. `NewRegistryBackendConfig` derives a runtime config from a parsed image reference and Docker credential store. `BuildRuntimeExternalBackendConfig` injects runtime registry/proxy settings into an existing external backend JSON file.

## Control Flow

`NewRegistryBackendConfig` chooses `HTTP_PROXY`, falling back to `HTTPS_PROXY`, fills host/repo from `distribution/reference`, and loads Docker auth for the host. `BuildRuntimeExternalBackendConfig` reads an external backend file, unmarshals caller-provided registry JSON, applies environment overrides for proxy URL/cache dir, replaces `Backends[0].Config`, marshals, and overwrites the same file.

## State and Persistence Behavior

The first function only reads Docker config and environment. The second rewrites `externalBackendConfigPath` in place. It assumes at least one backend entry exists in the external backend JSON.

## Dependencies and Integration Points

It integrates with Docker CLI config loading, image references, and `snapshotter/external/backend.Backend`. `viewer.handleExternalBackendConfig` calls the rewrite path for model artifacts with external backend configs.

## Risks and Test Signals

Risks include panic on empty `Backends`, loss of existing backend config fields, proxy fallback always forced true during rewrite, and auth only populated when username/password fields are present. Tests cover proxy env selection, Docker auth, missing files, and normal rewrite but not empty backend arrays or invalid JSON variants.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/backend.go -->
