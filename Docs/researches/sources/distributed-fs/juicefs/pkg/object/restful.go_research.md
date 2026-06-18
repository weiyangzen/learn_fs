# sources/distributed-fs/juicefs/pkg/object/restful.go

Purpose: supplies the package-wide HTTP client and a generic signed REST object-storage implementation used by REST-like backends such as UFile.

Important APIs and types: global `resolver` and `httpClient`, `splitIPsByVersion`, `dialParallel`, `dialRandom`, `GetHttpClient`, `cleanup`, `RestfulStorage`, `request`, `parseError`, `getRange`, `checkGetStatus`, and CRUD methods. `RestfulStorage` holds endpoint, credentials, sign name, and signer callback.

Control flow and state: `init` creates an `http.Client` with cached DNS, custom `DialContext`, IPv6 primary dialing with IPv4 fallback after 300 ms, long total timeout, transport buffers, and disabled compression. `RestfulStorage.request` builds a request, sets date and optional headers/content length, invokes signer, then uses the shared client. Object methods map HTTP status codes to object behavior; copy downloads the whole source and reuploads it; listing is unsupported.

Persistence and integration: persistent state is remote HTTP object storage. Shared `httpClient` is also used by many provider SDK configurations. The `ObjectStorage` assertion documents the generic adapter contract.

Risks and test signals: `Get` leaks response bodies on parse-error paths because `parseError` reads but does not close unless callers clean up. Copy is memory-bound. `dialParallel` behavior is tested in `restful_test.go`, including empty primary/fallback cases.
