# sources/distributed-fs/ceph/src/rgw/driver/rados/oidcs.h

Purpose: Declares account OIDC provider URL index helper APIs.

Important APIs/types/functions: `add()`, `remove()`, and `list()` manage provider URL resources on a supplied `rgw_raw_obj`, with exclusive/limit support for add and marker/max pagination for list.

Control flow: Callers choose the account index object and pass optional-yield context. Returned `provider_urls` and `next_marker` drive higher-level provider reads.

State/persistence: The API manipulates cls_user account-resource entries; resource names are provider URLs.

Dependencies/integration: Uses librados forward declarations, SAL forward types, `RGWOIDCProviderInfo`, and `DoutPrefixProvider`.

Risks: URL normalization is not encoded in the type system; add/remove/list callers must agree on whether scheme prefixes are stripped.

Test signals: Compile consumer paths, pagination propagation, exclusive add conflicts, limit behavior, and URL normalization through the higher-level OIDC API.
