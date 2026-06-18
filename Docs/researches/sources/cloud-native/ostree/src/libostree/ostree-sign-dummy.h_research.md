# sources/cloud-native/ostree/src/libostree/ostree-sign-dummy.h

Purpose: declaration header for the dummy `OstreeSign` final type and its interface method implementations.

Important APIs/types/functions: defines `OSTREE_TYPE_SIGN_DUMMY`, declares `OstreeSignDummy`, and declares name, sign, verify, metadata key/format, secret-key, public-key, and add-public-key functions.

Control flow: the generic signing registry instantiates this type by GType and invokes these functions through `OstreeSignInterface`.

State/persistence: no persistent state is declared in the header; instance state is private to the implementation. Metadata key/format imply detached storage shape `ostree.sign.dummy: aay`.

Dependencies/integration: depends on `ostree-sign.h` and GObject type macros. Included by `ostree-sign.c`.

Risks: backend symbols are visible even though the backend is test-only. The header declares `ostree_sign_dummy_add_pk`, but the implementation maps the interface to `set_pk` rather than defining a separate function, so direct callers of that symbol would fail linkage.

Test signals: dummy signing shell tests and generic sign API tests are the main linkage/behavior signals.
