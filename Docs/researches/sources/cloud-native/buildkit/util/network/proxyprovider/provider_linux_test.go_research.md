## sources/cloud-native/buildkit/util/network/proxyprovider/provider_linux_test.go

Purpose: Linux tests for proxy handler capture, policy conversion, URL redaction, transport behavior, and cert cache.

Important tests: capture successful GET digest; strip Accept-Encoding while preserving compressed response; ignore canceled client context for upstream round trip; ensure `ForceAttemptHTTP2` and cloned HTTP/2 dialing; adjust MITM response close behavior for unknown length; mark POST incomplete; map redirect aliases to final digest; redact credentials and normalize default ports; apply source policy URL conversion; redact credentials in policy errors; reject non-GET conversion and converted attrs; cache and refresh per-host certs.

State/control flow: uses `httptest` servers, a test proxy handler with cloned default transport, synthetic policy evaluators, and generated test CA.

Risks covered: reproducibility capture correctness, credential leakage, HTTP/2 regressions, unsupported policy conversions, cert cache expiry. Gaps: full namespace/veth lifecycle and actual CONNECT tunnel integration are not end-to-end tested here.
