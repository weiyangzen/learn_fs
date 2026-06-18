# sources/cloud-native/ostree/src/libostree/ostree-tls-cert-interaction-private.h

## Purpose
Private declaration for an OSTree-specific `GTlsInteraction` subclass that supplies a client certificate and key to a TLS connection on demand.

## Important APIs, Types, And Functions
The header defines `OSTREE_TYPE_TLS_CERT_INTERACTION`, cast/check macros, opaque `OstreeTlsCertInteraction` and class typedefs, an autoptr cleanup function, `_ostree_tls_cert_interaction_get_type`, and `_ostree_tls_cert_interaction_new(cert_path, key_path)`.

## Control Flow
Callers create the interaction with certificate and key paths, attach it to TLS-enabled GIO/Soup networking machinery, and the implementation responds when a certificate is requested by the TLS connection.

## State And Persistence Behavior
The header only describes an object that stores certificate/key paths and, in the implementation, lazily caches a `GTlsCertificate`. It does not write persistent state.

## Dependencies And Integration Points
It depends on `otutil.h` and GIO TLS types. The file is private, intended for internal libostree networking code that needs mTLS support without exposing this helper as public API.

## Risks
Because the type is private, ABI risks are low, but macro correctness matters. Credential path lifetime and certificate loading errors are implementation-sensitive.

## Test Signals
Compile tests should ensure the private type is available where needed. Behavioral tests should verify client certificate selection succeeds with valid cert/key files and fails cleanly with invalid paths.
