# sources/distributed-fs/ceph/src/rgw/rgw_rest_conn.cc

## Purpose

`rgw_rest_conn.cc` implements `RGWRESTConn`, the higher-level connection object that selects remote endpoints, signs requests with zone credentials, retries transient I/O failures, marks endpoints temporarily unconnectable, and exposes convenience APIs for forwarding requests, object transfer, and generic resource GET/POST/PUT/DELETE.

## Important APIs and Functions

The file implements constructors, move operations, endpoint selection (`get_url()`), failure marking (`set_url_unconnectable()`), sys-param population, request forwarding (`forward()`, `forward_iam()`), object upload/download helpers (`put_obj_*`, `get_obj()`, `complete_request()`), generic resource helpers (`get_resource()`, `send_resource()`), and the `RGWRESTReadResource`/`RGWRESTSendResource` wrapper methods.

`get_obj()` is the densest API. It maps replication and conditional-read options into query parameters and headers: `prepend-metadata`, `stat`, `sync-manifest`, `sync-cloudtiered`, `skip-decrypt`, `if-not-replicated-to`, `versionId`, permission-check uid, conditional dates, ETag match, destination zone/PG version, and byte ranges.

## Control Flow

Construction records endpoints and initializes each endpoint status to `real_clock::zero()`. With a driver, it also pulls the local zone system key and zonegroup id. `get_url()` round-robins with an atomic counter and skips endpoints marked failed in the last two seconds. If every endpoint is still marked failed, it returns `-EINVAL`.

`forward()` and `forward_iam()` try up to 20 endpoint I/O retries. They build params, create an `RGWRESTSimpleRequest`, call `forward_request()`, return successful HTTP status values, and only retry on `-EIO`. Object and resource helpers follow the same pattern: pick URL, build params and headers, prepare a streaming request, send, wait, and mark the endpoint unconnectable on `-EIO`.

`RGWRESTReadResource` and `RGWRESTSendResource` wrap a single request object for synchronous and asynchronous resource access. Their `wait()` methods decode JSON responses or expose raw bufferlists depending on template usage.

## State and Persistence Behavior

Connection state includes endpoint list, per-endpoint atomic last-failure timestamps, remote id, system credentials, self zonegroup, optional API name, host style, and atomic selection counter. The two-second failure window is in-memory only. Remote persistence occurs through forwarded object/resource/IAM requests. Local persistence is not changed except for any caller-controlled side effects of remote metadata and object sync.

## Dependencies and Integration Points

The implementation depends on `rgw_zone.h`, SAL driver zone access, `rgw_rest_client.h`, HTTP errno mapping, and object/zone types. It is an integration layer between RGW multisite metadata/object logic and the lower HTTP request classes. `S3RESTConn` in the header overrides parameter population, while the base connection injects RGW system params for admin-style remote RGW APIs.

## Risks and Edge Cases

Endpoint selection returns `-EINVAL` both for no endpoints and all endpoints temporarily failed, which can obscure failure classification. The two-second unconnectable TTL is short and may cause rapid retries against a bad endpoint under persistent failure. Several constructors for resource wrappers call `conn->get_url()` as a string and ignore a possible `get_url()` error path. Move operations copy only selected fields and do not move `api_name` or `host_style`, which is a maintenance risk if moved connections are used.

Object retrieval has many coupled flags; incorrect parameter/header translation can break multisite sync semantics. Range formatting uses signed casts from unsigned fields. Callers own request pointers until `complete_request()`, which deletes them.

## Test Signals

Tests should cover round-robin endpoint selection, endpoint failure expiry, retry-on-`-EIO` only, no-endpoint errors, forwarded IAM service signing, object GET/HEAD parameter/header construction, versioned object paths, range and conditional headers, and async wrapper `wait()` behavior with JSON decode success/failure. Multisite sync integration tests are the strongest signal because they exercise credentials, zonegroup params, and endpoint failover together.
