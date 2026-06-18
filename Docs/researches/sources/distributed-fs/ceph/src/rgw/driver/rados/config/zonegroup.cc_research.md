# sources/distributed-fs/ceph/src/rgw/driver/rados/config/zonegroup.cc

Purpose: Implements RADOS storage for zonegroup metadata, default zonegroup id per realm, zonegroup name lookup, writer operations, and name listing.

Important APIs/types/functions: Zonegroup info oids are `zonegroup_info.<id>`, names are `zonegroups_names.<name>`, and default objects are `<default.zonegroup or configured prefix>.<realm_id>`. `RadosZoneGroupWriter` provides versioned write/rename/remove. Public methods include default-id CRUD, create/read by id/name/default, and `list_zonegroup_names()`.

Control flow: Create validates id/name, writes info, writes name index, and removes info on name failure. Rename creates the new name index first, updates info with `MustExist`, rolls back new name on failure, then best-effort removes old name. Remove deletes info with objv then best-effort deletes name.

State/persistence: State lives in `impl->zonegroup_pool` across info object, name index, and realm-scoped default object. Writer objects remember id/name and objv to guard subsequent mutations.

Dependencies/integration: Uses `RGWZoneGroup`, `RGWNameToId`, `RGWDefaultSystemMetaObjInfo`, SAL `ZoneGroupWriter`, `ConfigImpl`, and config option `rgw_default_zonegroup_info_oid`.

Risks: Multi-object operations can leave stale name/default indexes. Rename mutates caller state before old-name cleanup. Listing scans all pool objects and filters by prefix, so sparse pools may require repeated calls.

Test signals: Exercise create exclusive conflicts, rollback on name write failure, rename to existing name, remove cleanup, default zonegroup per realm, and paginated listing.
