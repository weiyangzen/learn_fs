# sources/cloud-native/containerd/internal/wintls/wintls_other.go

## Purpose
Provides non-Windows stubs for Windows certificate-store TLS setup.

## Important APIs, Types, And Functions
`CertResource` aliases `io.Closer`. `NoopCertResource` implements `Close`. `SetupTLSFromWindowsCertStore` returns nil TLS config, nil cert pool, a noop resource, and nil error.

## Control Flow
Non-Windows callers can invoke the API without build failures, but receive no TLS material.

## State And Persistence
No state.

## Dependencies And Integration Points
Uses context, crypto/tls, crypto/x509, and io for API compatibility.

## Risks
Returning nil error with nil TLS config requires callers to interpret platform behavior correctly. It is a no-op, not an unsupported error.

## Test Signals
No direct tests. Compile coverage is the main signal.
