# sources/cloud-native/ostree/src/libostree/ostree-tls-cert-interaction.c

## Purpose
Implements the private `OstreeTlsCertInteraction` `GTlsInteraction` subclass used to lazily load a client certificate/key pair and install it on a `GTlsConnection` when the peer requests a certificate.

## Important APIs, Types, And Functions
The instance stores `cert_path`, `key_path`, and cached `GTlsCertificate *cert`. `request_certificate` is the key virtual method: it calls `g_tls_certificate_new_from_files` the first time, stores the result, and sets it on the connection. `_ostree_tls_cert_interaction_new` allocates the object and duplicates the path strings.

## Control Flow
Creation records the two paths. During TLS negotiation, GIO invokes `request_certificate`; the method loads and caches the certificate if needed, returns `G_TLS_INTERACTION_FAILED` on load failure, otherwise sets the certificate and returns `G_TLS_INTERACTION_HANDLED`.

## State And Persistence Behavior
State is in-memory only. The loaded `GTlsCertificate` is cached across repeated requests for the lifetime of the interaction. The code reads cert/key files but does not write or persist anything.

## Dependencies And Integration Points
Depends on GIO TLS APIs and the private header. It plugs into libostree HTTP/TLS clients that need client certificate authentication.

## Risks
The implementation as shown does not define a finalize method to free `cert_path`, `key_path`, or unref `cert`, so repeated construction can leak memory. It does not reload changed certificate files after the first successful request. Errors from invalid key/cert pairs propagate through the TLS interaction result.

## Test Signals
Tests should exercise valid cert/key loading, invalid file handling, repeated certificate requests using the cached certificate, and object destruction under leak checks.
