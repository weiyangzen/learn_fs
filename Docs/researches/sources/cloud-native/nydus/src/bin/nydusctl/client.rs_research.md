# sources/cloud-native/nydus/src/bin/nydusctl/client.rs

## Purpose
`client.rs` is the async Unix-domain HTTP client used by `nydusctl` to communicate with the `nydusd` administration API.

## Important APIs, Types, And Functions
`NydusdClient` stores the API socket path. `new` constructs a client. `build_uri` prefixes request paths with `/api/` and adds simple query strings before converting them to `hyperlocal` Unix-socket URIs. `get`, `put`, `post`, and `delete` create a `hyper_util` Unix client, send the request, collect the response body, parse JSON error payloads when needed, and return either JSON values or unit.

## Control Flow
Command objects call `get` for information and metrics, `put` for daemon configuration, `post` for mount/create operations, and `delete` for unmount/delete operations. Each request creates a fresh client, builds a URI using the stored socket, sends optional JSON body bytes, checks HTTP status, and bails on status codes >= 400.

## State And Persistence
The client keeps only the socket path. It does not persist connections, cookies, or response data. Any daemon state changes are performed by the server endpoints reached through PUT/POST/DELETE.

## Dependencies And Integration Points
It integrates `nydusctl` command implementations with `nydusd` API routes exposed by `nydus_api` and `api_server_glue.rs`. It depends on `hyper`, `hyper_util`, `hyperlocal`, `http_body_util`, `serde_json`, and `anyhow`.

## Risks
Query parameters are concatenated without URL encoding, so special characters in mountpoints or ids can break requests. Error handling assumes error responses are JSON; non-JSON error bodies become deserialize failures. The PUT/POST/DELETE success path ignores response bodies. Creating a new client per request is simple but loses connection reuse.

## Test Signals
Unit tests cover construction and URI building with no query, one query parameter, multiple parameters, an empty query list, and representative API paths. They do not exercise real socket I/O, HTTP errors, non-JSON bodies, or URL encoding.
