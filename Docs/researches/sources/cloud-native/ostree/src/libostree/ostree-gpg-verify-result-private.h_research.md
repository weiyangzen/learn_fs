# sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result-private.h

## Purpose
This private header exposes the real `OstreeGpgVerifyResult` instance layout to GPG verifier/result implementation files.

## Important APIs, Types, And Functions
`struct OstreeGpgVerifyResult` contains a GObject parent, `gpgme_ctx_t context`, and `gpgme_verify_result_t details`.

## Control Flow, State, And Persistence
The stored GPGME context owns key lookup state and is tied to the temporary GPG home created by the verifier. The `details` pointer holds verification result data refcounted from GPGME.

## Dependencies And Integration Points
It includes `ostree-gpg-verify-result.h` and `otutil.h`, which supplies GPGME-related cleanup macros/utilities. It is consumed by `ostree-gpg-verifier.c` and `ostree-gpg-verify-result.c`.

## Risks And Test Signals
The context and details lifetimes must remain aligned: freeing the temporary home too early breaks key detail lookup, while failing to release GPGME refs leaks resources. Tests should cover result finalization, repeated attribute queries after verification, and error cleanup.
