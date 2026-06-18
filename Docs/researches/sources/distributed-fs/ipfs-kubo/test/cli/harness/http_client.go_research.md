# sources/distributed-fs/ipfs-kubo/test/cli/harness/http_client.go

Purpose: small HTTP testing wrapper for Kubo gateway/API requests with template-expanded paths and buffered responses.

Important APIs/types/functions: `HTTPClient` contains an underlying `*http.Client`, `BaseURL`, optional `Timeout`, and `TemplateData`. `HTTPResponse` exposes body, status, headers, and raw response. Methods include `WithHeader`, `DisableRedirects`, `Do`, `BuildURL`, `Get`, `Post`, `PostStr`, and `Head`.

Control flow: request helpers build URLs by executing a Go `text/template` against `TemplateData`, prepend `BaseURL`, apply request mutators, then call `Do`. `Do` executes the request, closes the body, reads it fully, and returns a structured response.

State and persistence: no persistent state, but `DisableRedirects` mutates the shared `http.Client.CheckRedirect`, so the redirect behavior can affect later requests using the same client.

Dependencies/integration: used by `Node.GatewayClient` and `Node.APIClient`; integrates with Go `net/http` and template rendering.

Risks: the `Timeout` field is unused; global `http.DefaultClient` reuse plus `DisableRedirects` mutation can make parallel tests interdependent. Full body buffering is convenient but unsuitable for large streams except where tests use raw `http.Client` directly. Test signals are status, headers, and body string assertions.
