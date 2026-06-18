# sources/distributed-fs/ceph/src/rgw/driver/rados/group.cc

Purpose: Implements RADOS-backed IAM/group metadata for RGW, including primary group info objects, case-insensitive account/name indexes, per-group user resource objects, account group-list linkage, and the RGW metadata handler.

Important APIs/types/functions: Group info keys are `info.<group_id>`, name keys are `name.<account_id>$<lower_name>`, and per-group user-list keys are `users.<group_id>`. `NameObj` is the redirect equivalent. `read()`, `read_by_name()`, `write()`, and `remove()` are the main CRUD APIs. `create_metadata_handler()` returns the `"group"` metadata handler.

Control flow: Reads decode and verify `RGWGroupInfo.id`. Writes compare `old_info`, read old name object for removal, check new name uniqueness, write the primary group object, then best-effort remove old name/account-list entry and write new name/account-list entry. Removes delete the primary object first, then best-effort delete name, per-group users object, and account group-list entry. Metadata put mirrors account handling by reading old state and calling `write()` nonexclusively.

State/persistence: Group metadata lives in `zone.group_pool`; account linkage uses `account::get_groups_obj()` and `groups::add/remove()` in the account pool/account object. Name matching is lower-cased, giving case-insensitive names per account.

Dependencies/integration: Depends on `RGWSI_SysObj`, librados, account resource object helpers, `groups.cc` cls_user account-resource helpers, RGW metadata sync, `RGWGroupInfo`, and boost lowercase conversion.

Risks: Account linkage and name redirects are not atomic with primary group writes. Failures linking/unlinking account lists are logged but non-fatal, so list-by-account may diverge from group objects. The remove error message says "account obj" for a group object, which may confuse logs.

Test signals: Create/update/remove with name changes, case-insensitive name conflicts, account group list consistency, metadata sync put/remove, missing secondary object cleanup, and corrupt decode/id mismatch handling.
