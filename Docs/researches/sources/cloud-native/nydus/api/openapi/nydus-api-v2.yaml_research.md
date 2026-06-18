# sources/cloud-native/nydus/api/openapi/nydus-api-v2.yaml

## Purpose
This OpenAPI document sketches v2 service and management APIs under `https://localhost/v2`, focusing on daemon info/config and blob cache management.

## Important APIs, Types, and Functions
Endpoints include `/daemon` GET/PUT and `/blobs` GET/PUT/DELETE. Schemas present in the file include `DaemonInfo`, `DaemonConf`, and `ErrorMsg`; the paths reference additional schemas such as `BlobObjectList`, `BlobObjectConf`, `BlobObjectParam`, and `BlobId`.

## Control Flow
Clients can query/configure daemon state and manage blob cache objects through list/create/delete actions. Success is represented by JSON for reads and `204` for mutations.

## State and Persistence
The v2 API controls daemon runtime configuration and blob cache object state. The underlying blob cache may persist cached files/configs, but this file only defines the HTTP contract.

## Dependencies and Integration Points
The document aligns conceptually with `ApiRequest` v2 variants in `api/src/http.rs`: `GetDaemonInfoV2`, `CreateBlobObject`, `GetBlobObject`, `DeleteBlobObject`, and `DeleteBlobFile`.

## Risks and Edge Cases
The `/blobs` `delete` block appears malformed: it contains two `operationId`, `requestBody`, and `responses` mappings under the same HTTP method, so YAML parsing keeps only one set or OpenAPI validation fails depending on tooling. Referenced blob schemas are not defined in `components.schemas` in the visible file. The server URL uses HTTPS while v1 uses HTTP; implementation compatibility should be checked.

## Test Signals
OpenAPI validation should be run after changes. Tests should assert route registration and schema presence for all referenced v2 blob operations.
