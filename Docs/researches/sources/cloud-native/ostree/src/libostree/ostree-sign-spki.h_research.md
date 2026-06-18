# sources/cloud-native/ostree/src/libostree/ostree-sign-spki.h

Purpose: declaration header for the SPKI final `OstreeSign` backend.

Important APIs/types/functions: defines `OSTREE_TYPE_SIGN_SPKI`, declares `OstreeSignSpki`, and exposes backend method implementations for data signing/verification, name, metadata key/format, key clearing, secret/public key setting, public-key addition, and public-key loading.

Control flow: the generic signing registry instantiates this backend conditionally and calls methods through `OstreeSignInterface`; direct callers should prefer generic `OstreeSign` APIs.

State/persistence: state is private to the implementation. Detached metadata produced by this backend uses SPKI metadata key/type macros.

Dependencies/integration: depends on `ostree-sign.h` and OpenSSL-enabled implementation support. Included by the generic signing layer.

Risks: direct use ties callers to optional compile-time support and backend-specific key formats.

Test signals: SPKI signed commit tests and generic signing/summary tests exercise this declaration surface through the public interface.
