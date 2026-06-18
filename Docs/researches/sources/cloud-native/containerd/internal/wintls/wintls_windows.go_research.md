# sources/cloud-native/containerd/internal/wintls/wintls_windows.go

## Purpose
Builds a TLS client/server configuration from a certificate and private key in the Windows certificate store.

## Important APIs, Types, And Functions
`WindowsCertResource` owns a `certtostore.WinCertStore` and `windows.CertContext`, with `Close` freeing both. `SetupTLSFromWindowsCertStore` opens the "My" store, finds a certificate by common name, obtains its private key, builds a cert pool and `tls.Certificate`, and returns cleanup resource.

## Control Flow
Each failure path closes/free resources acquired so far. Successful setup filters the leaf out of intermediate chains, attaches leaf raw bytes plus intermediates to TLS certificate, and returns caller-managed cleanup.

## State And Persistence
Opens Windows certificate store handles and certificate contexts. No certificate is persisted or modified.

## Dependencies And Integration Points
Uses `github.com/google/certtostore`, Windows syscalls, and Go crypto/tls/x509. Integrates Windows certificate management with containerd TLS configuration.

## Risks
Context parameter is currently unused. `Close` returns only the last close/free error if both fail. Certificate lookup by common name may be ambiguous depending on store contents.

## Test Signals
No direct tests in this subset; Windows integration/manual tests are needed.
