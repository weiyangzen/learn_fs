# sources/distributed-fs/ceph/src/rgw/driver/rados/oidcs.cc

Purpose: Implements account-scoped OIDC provider URL listing helpers using the `cls_user_account_resource` object-class API.

Important APIs/types/functions: `add()` stores a resource named by `url_remove_prefix(info.provider_url)`. `remove()` deletes a resource by provider URL string. `list()` pages resources and returns provider URL names.

Control flow: Operations resolve the supplied account OIDC object to `rgw_rados_ref`, build cls_user account-resource add/remove/list operations, and operate with optional yield. Listing treats missing objects as empty, returns cls errors, and appends resource names to `provider_urls`.

State/persistence: Account OIDC indexes live on the `account::get_oidcs_obj()` object. Unlike group resources, no custom metadata payload is encoded; the resource name is the URL.

Dependencies/integration: Depends on librados, cls_user client, `RGWOIDCProviderInfo`, `url_remove_prefix()`, and RGW account OIDC object helpers. `oidc.cc` calls these functions during provider write/remove/list.

Risks: `remove()` expects the same normalized URL form that `add()` stored; callers passing a provider URL with scheme can fail to remove the entry. Listing does not clear `next_marker` when not truncated in this file, so callers should rely on cls output or ensure empty marker semantics.

Test signals: Add/remove/list with normalized and unnormalized URLs, missing object listing, pagination markers, limit enforcement, and stale-index behavior with `oidc.cc`.
