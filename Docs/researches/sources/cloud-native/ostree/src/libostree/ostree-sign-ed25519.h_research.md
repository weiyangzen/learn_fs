# sources/cloud-native/ostree/src/libostree/ostree-sign-ed25519.h

Purpose: declaration header for the Ed25519 final `OstreeSign` backend.

Important APIs/types/functions: defines `OSTREE_TYPE_SIGN_ED25519`, declares `OstreeSignEd25519`, and exposes backend method implementations for signing data, verifying data, engine name, metadata key/format, key clearing, secret/public key setting, public-key addition, and public-key loading.

Control flow: `ostree-sign.c` registers this type conditionally and invokes methods through the generic interface. Direct users should normally use `ostree_sign_get_by_name(OSTREE_SIGN_NAME_ED25519)` and generic APIs.

State/persistence: state is implementation-private. Detached metadata stores arrays of Ed25519 signatures under backend metadata key/type macros.

Dependencies/integration: depends on `ostree-sign.h`, GLib/GObject, and compile-time Ed25519 support flags in the implementation.

Risks: backend symbols are callable directly, but that ties callers to compile-time availability and backend-specific key formats.

Test signals: shell tests for signed Ed25519 commits/deltas and composefs signed validation exercise the declarations through generic API/CLI paths.
