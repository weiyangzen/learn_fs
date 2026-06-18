# sources/distributed-fs/ceph/src/rgw/driver/rados/config/zone.cc

Purpose: Implements RADOS storage for zone parameters, default zone id per realm, zone name lookup, zone writer operations, and zone name listing.

Important APIs/types/functions: Zone info oids are `zone_info.<id>`, name oids are `zone_names.<name>`, and default-zone oids are `<rgw_default_zone_info_oid>.<realm_id>`. `RadosZoneWriter` implements versioned write/rename/remove. Public methods include `write_default_zone_id()`, `read_default_zone_id()`, `delete_default_zone_id()`, `create_zone()`, `read_zone_by_id()`, `read_zone_by_name()`, `read_default_zone()`, and `list_zone_names()`.

Control flow: Create validates id/name, writes info, writes name index, and rolls back info on name failure. Writer `write()` rejects direct id/name changes. Rename creates the new name exclusively, updates the info object, removes the new name on update failure, then best-effort removes the old name. Reads by name/default resolve id first, then read info with objv for writer creation.

State/persistence: Zone metadata spans info, name index, and realm-scoped default id objects in `impl->zone_pool`. Writer instances carry the version tracker from the info read/create.

Dependencies/integration: Uses `RGWZoneParams`, `RGWNameToId`, `RGWDefaultSystemMetaObjInfo`, SAL `ZoneWriter`, `ConfigImpl`, and Ceph config default oid settings.

Risks: `default_zone_oid()` formats `conf->rgw_default_zone_info_oid` directly; unlike zonegroup/realm, it does not call `name_or_default()`, so empty config would produce `.realm`. Multi-object update rollback is best effort and can leave stale name indexes.

Test signals: Validate default oid construction, create rollback, rename conflict/rollback, writer immutability, default-zone lookup by realm, and list prefix filtering.
