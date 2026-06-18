# sources/distributed-fs/ceph/src/rgw/rgw_lc.h

Purpose: Declares the lifecycle data model, serialization format, rule expansion structures, lifecycle worker class, and helper APIs used by RGW lifecycle processing.

Important APIs and types: `LCExpiration`, `LCTransition`, `LCFilter`, and `LCRule` model lifecycle rule components. `transition_action` and `lc_op` are execution-ready forms used by `rgw_lc.cc`. `RGWLifecycleConfiguration` owns `rule_map` and `prefix_map`, validates and encodes rules, and converts rules into `lc_op`. `RGWLC` owns lifecycle workers and exposes processor/config APIs. Namespace `rgw::lc` declares shard repair and S3 header helpers.

Control flow: Lifecycle XML or stored attrs decode into `RGWLifecycleConfiguration`, whose decode path rebuilds the prefix map by calling `_add_rule()`. `RGWLC::LCWorker` threads call `RGWLC::process()` repeatedly, and `RGWLC` methods use SAL lifecycle services to list, lock, and mutate lifecycle entries. Header helpers decode bucket lifecycle attrs on demand to compute response metadata.

State and persistence: The classes encode with Ceph `ENCODE_START` versioning, preserving backward compatibility across lifecycle schema changes. `LCExpiration` tracks days, date, and newer-noncurrent versions. `LCFilter` tracks prefix, tags, size bounds, and extension flags such as `ArchiveZone`. `LCRule` carries expiration, noncurrent expiration, multipart expiration, transitions, noncurrent transitions, and delete-marker expiration. `RGWLC` stores daemon-local worker state, lifecycle object names, shutdown flag, and lock cookie.

Dependencies and integration points: Depends on Ceph buffer encoding, librados types, RGW tags, SAL driver/bucket abstractions, RGW common request/debug infrastructure, and lifecycle class types. It is included by S3 XML parsing, lifecycle execution, and operation handlers that install or remove lifecycle configs.

Risks: Several fields are stored as strings and converted with `atoi()` or `stoull()` style parsing, so validation must happen before execution. Versioned encoding makes compatibility important when adding fields. The worker owns raw `obj_names` allocated in `initialize()` and freed in `finalize()`, so lifecycle object lifetime must stay ordered.

Test signals: Serialization compatibility tests should cover all struct versions, especially `LCExpiration` and `LCFilter`. Rule tests should cover id length, empty actions, date/day conflicts, duplicate ids, tag restrictions, size filters, transitions, archive-zone flags, and prefix map reconstruction after decode.
