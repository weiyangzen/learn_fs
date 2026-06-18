# sources/cloud-native/ostree/src/libostree/ostree-sign.h

Purpose: public header for the SignAPI abstraction, allowing callers to use named signing engines without depending on backend implementation details.

Important APIs/types/functions: defines `OSTREE_TYPE_SIGN`, engine name constants, and `G_DECLARE_INTERFACE(OstreeSign, ...)`. The interface declares vfuncs for engine name, data sign/verify, metadata key/format, key clearing, secret/public key setting, public-key addition, and public-key loading. Public wrappers include data signing/verification, metadata introspection, commit signing/verification, key management, engine enumeration/lookup, summary signing, and key blob-reader creation.

Control flow: consumers instantiate an engine by name, configure keys, then call data/commit/summary sign or verify. Verification can return a success message identifying the key used. `ostree_sign_read_pk/sk` lets CLIs parse backend-appropriate key encodings.

State/persistence: the interface itself does not define storage, but backend instances hold keys and generic operations persist signatures in repository metadata. Constants name stable engine selectors.

Dependencies/integration: depends on GLib/GObject, `ostree-blob-reader.h`, refs/remotes/types, and repository types. Used by `ostree-repo.h` static delta and signature APIs and by CLI/admin paths.

Risks: backend availability is compile-time dependent. Callers must understand backend-specific key variant formats even though the API is generic. Repo verify flags can skip all SignAPI verification.

Test signals: backend-specific signed commit tests, summary signature tests, delta signature tests, and Rust binding sign modules exercise the interface. ABI/layout tests should catch accidental public header changes.
