# Research: sources/cloud-native/nydus-snapshotter/pkg/remote/remote.go

This file wraps registry resolver creation and controlled HTTP fallback. `Remote` stores a resolver factory, a `withPlainHTTP` flag, and an `insecure` flag. `New` builds Docker registry resolvers with optional credentials from `auth.PassKeyChain`, TLS skip-verify behavior for insecure registries, an authorizer, a shared HTTP client, and a `WithPlainHTTP` callback driven by the fallback flag.

`RetryWithPlainHTTP` only permits fallback when `insecure` is true and the error string looks like an HTTPS-client-to-HTTP-server mismatch or connection refused. It parses the reference, checks that the error includes the registry host path, logs the downgrade, and sets `withPlainHTTP`. `Resolve` and `Fetcher` create fresh resolver/fetcher instances using the current fallback mode.

State is the mutable fallback flag. Integration points include index/referrer detection, auth, Docker remotes, and registry reference parsing. Risks include mutating `http.DefaultTransport`/`http.DefaultClient`, string-matching unexported Go errors, plain HTTP retry state persisting across later calls on the same `Remote`, and host-string matching assumptions. Tests cover fallback decisions.
