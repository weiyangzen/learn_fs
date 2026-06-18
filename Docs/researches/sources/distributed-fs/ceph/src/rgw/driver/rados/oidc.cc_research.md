# sources/distributed-fs/ceph/src/rgw/driver/rados/oidc.cc

Purpose: Implements RADOS-backed OIDC provider metadata for RGW, including provider object CRUD, tenant/account listing, account-resource linkage, metadata sync handler, and metadata-key conversion.

Important APIs/types/functions: Provider objects use oid `{tenant}oidc_url.{url_without_prefix}` in `zone.oidc_pool`. Metadata keys use `{tenant}${url}`. `get_oidc_metadata_key()` and `parse_oidc_metadata_key()` translate metadata keys. `read()`, `write()`, `remove()`, `list()`, `list_oidc_urls()`, and `list_account_oidcs()` implement public behavior. `MetadataHandler` exposes metadata type `"oidc"` and calls mdlog completion.

Control flow: `write()` removes URL scheme prefix, writes the provider object, links it to an account OIDC list if `tenant` is an account id, then completes mdlog when supplied. `remove()` deletes the object, unlinks account index if applicable, then completes mdlog. `list()` chooses the account-index path for account tenants; otherwise it scans `zone.oidc_pool` by tenant prefix and decodes each object. Metadata get parses the metadata key, reads the object, and wraps it as `MetadataObject`; metadata put writes nonexclusively and returns `STATUS_APPLIED` on success.

State/persistence: Primary provider state is the encoded `RGWOIDCProviderInfo` object. Account tenants also have a cls_user account-resource list under `account::get_oidcs_obj()`. Metadata sync state is recorded through `RGWSI_MDLog::complete_entry()`.

Dependencies/integration: Depends on account helpers, `oidcs.cc` account-resource helpers, `RGWOIDCProviderInfo`, `url_remove_prefix()`, RGW metadata lister/handler, mdlog service, sysobj, and librados.

Risks: Link/unlink failures to account indexes are non-fatal, so account-optimized listing can miss existing providers or include deleted ones; `list_account_oidcs()` skips stale `-ENOENT` entries. Metadata listing scans all oidc-pool objects with empty prefix and filters oids containing `oidc_url.`, which may be expensive. Metadata key parsing uses the first `$`; URLs containing `$` remain in the url part, but tenants cannot contain this separator safely.

Test signals: CRUD with mdlog completion, account and non-account tenant listing, stale account index entries, URL prefix normalization, metadata key parse/format round trip, corrupt provider decode, and metadata lister filtering.
