# sources/distributed-fs/ceph/src/rgw/driver/rados/oidc.h

Purpose: Declares the OIDC provider RADOS persistence and metadata sync API.

Important APIs/types/functions: `read()`, `write()`, `remove()`, `list()`, `list_oidc_urls()`, `list_account_oidcs()`, `create_metadata_handler()`, `get_oidc_metadata_key()`, and `parse_oidc_metadata_key()` form the public interface.

Control flow: The API separates direct provider CRUD from account-index listing. Optional mdlog and objv parameters allow the same functions to serve admin paths and metadata sync.

State/persistence: Provider data is stored in zone OIDC pool objects; account provider URL indexes are stored via cls_user helpers; metadata keys use tenant/url conversion.

Dependencies/integration: Forward declares sysobj, mdlog, objv, zone params, provider info, metadata handler, and librados. Includes Ceph time for mtime.

Risks: Callers must pass normalized URLs consistently. Account vs non-account behavior depends on tenant string satisfying account-id validation.

Test signals: API-level tests should cover optional objv/mdlog use, URL listing pagination, account/non-account tenant split, and metadata key conversion.
