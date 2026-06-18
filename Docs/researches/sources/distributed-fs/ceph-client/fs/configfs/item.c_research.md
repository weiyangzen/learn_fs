# sources/distributed-fs/ceph-client/fs/configfs/item.c

Purpose: implements generic `config_item` and `config_group` lifetime, naming, initialization, reference counting, cleanup, and child lookup helpers.

Important APIs/functions: `config_item_set_name()` formats item names into `ci_namebuf` when short or dynamically allocates long names. `config_item_init_type_name()` and `config_group_init_type_name()` combine naming, type assignment, and kref/list initialization. `config_item_get()`, `config_item_get_unless_zero()`, and `config_item_put()` manage krefs. `config_item_cleanup()` frees dynamic names, calls optional `ct_item_ops->release()`, and drops group/parent references. `config_group_init()` initializes child/default lists. `config_group_find_item()` searches children by name under the caller-held subsystem mutex.

Control flow: clients allocate items/groups, initialize them here, configfs links them into parent groups in `dir.c`, and cleanup runs automatically when the final reference is dropped. Group lookup returns a referenced child.

State and persistence: state is embedded in client-owned `config_item`/`config_group` objects. Names persist until cleanup or rename through `config_item_set_name()`.

Dependencies/integration: public configfs API users depend on these exports. `dir.c` relies on `ci_parent`, `ci_group`, `ci_entry`, `cg_children`, and default group lists initialized here.

Risks: release callbacks are responsible for freeing client objects at the correct time. Long-name allocation failures can leave initialization partially named unless callers check return values. `config_group_find_item()` requires external locking; using it without `su_mutex` risks list races.

Test signals: short and long item names, repeated name changes freeing old allocations, kref final release, group child lookup under concurrent configfs operations, and client release callback ordering.
