# sources/distributed-fs/ceph/src/osd/osd_op_util.cc

## Purpose

`osd_op_util.cc` implements `OpInfo`, the OSD request classifier. It converts `MOSDOp` flags and contained `OSDOp` opcodes into RMW/capability/cache/promotion flags that later drive authorization, ordering, cache-tier behavior, EC read behavior, and operation scheduling.

## Important APIs and Functions

Accessor methods expose derived properties: `may_read()`, `may_write()`, `may_cache()`, `rwordered()`, `includes_pg_op()`, `need_read_cap()`, `need_write_cap()`, `need_promote()`, `need_skip_handle_cache()`, `need_skip_promote()`, `allows_returnvec()`, `ec_direct_read()`, `ec_sync_read()`, `may_read_data()`, and `may_read_data_for_ec()`. Setter methods OR individual `CEPH_OSD_RMW_FLAG_*` bits. The main APIs are `set_from_op(const MOSDOp *, const OSDMap&)` and `set_from_op(const std::vector<OSDOp>&, const pg_t&, const OSDMap&)`. The stream operator renders class method info.

## Control Flow

`set_from_op(MOSDOp*)` clears existing flags, imports request-level `RWORDERED` and `RETURNVEC`, then delegates to vector classification. The vector classifier loops over each `OSDOp`, marks write/read/cache/PG-op modes using `ceph_osd_op_mode_*` helpers, marks non-stat reads as data reads, and applies cache-tier promotion policy when a tier's base pool requires rollback. For `CEPH_OSD_OP_CALL`, it decodes class and method names from `indata`, opens the class through `ClassHandler`, obtains method flags, maps read/write/promote method flags into RMW bits, records `ClassInfo`, and translates class/method lookup failures into OSD error codes. Watch/notify paths force promotion and watch also forces read-data ordering. Delete/cache/read/writefull special cases set skip-promote or skip-handle-cache bits under narrow conditions.

## State and Persistence Behavior

`OpInfo` state is per request and in-memory: a `uint64_t rmw_flags` bitset and a vector of class method descriptors. It does not persist anything, but its decisions directly affect persistent behavior because promotion, rollback-required tiers, write ordering, and capability checks determine which OSD execution path handles the operation.

## Dependencies and Integration Points

The implementation depends on `OSDMap`, `MOSDOp`, `OSDOp` opcode helpers, `ClassHandler`, Ceph bufferlists, and pool metadata. `OpRequest` embeds `OpInfo`; `OSDCap` consumes class info for class-method authorization; `PrimaryLogPG` uses read/write/cache/promotion and ordering flags to choose locks, cache handling, and operation execution strategy.

## Risks and Test Signals

Classification errors can become security bugs, stale reads, unnecessary promotion, skipped promotion when data is needed, or broken EC behavior. Dynamic class lookup can fail at classification time, so error mapping must remain compatible with client expectations. The explicit allow/deny list for rollback-required tier promotion is fragile when new opcodes are added. Test signals include unit tests for every opcode category, class method flag tests, capability checks for class methods, cache-tier promotion behavior, delete FAILOK handling, watch ping ordering, and EC class read data classification.
