# sources/distributed-fs/ceph/src/osd/osd_op_util.h

## Purpose

`osd_op_util.h` declares the `OpInfo` request-classification type used by OSD request processing. It presents a compact API for deriving read/write/cache/order/promotion/capability information from OSD operation vectors and for exposing object-class method metadata to authorization code.

## Important APIs and Types

`OpInfo::ClassInfo` stores class name, method name, read bit, write bit, and whether the class method is allowed. Private state is `uint64_t rmw_flags` plus `std::vector<ClassInfo> classes`. Public methods include `clear()`, `get_flags()`, all boolean predicates over the flag set, setters for individual categories, the two `set_from_op()` overloads, and `get_classes()`. A free `operator<<` formats `ClassInfo`.

## Control Flow

The header separates declaration from the policy implementation in `osd_op_util.cc`. Callers construct or reuse an `OpInfo`, call `set_from_op()` with a `MOSDOp` or op vector plus PG and `OSDMap`, then consult predicates such as `may_read()`, `may_write()`, or `need_promote()`. `clear()` resets only the flags; successful class classification appends to `classes` in the implementation.

## State and Persistence Behavior

`OpInfo` is transient request metadata. It is not encoded or persisted, but its flags influence persistent side effects by selecting OSD execution, ordering, promotion, and authorization paths. Because `get_classes()` returns a vector by value, consumers get a snapshot of class metadata rather than a mutable reference.

## Dependencies and Integration Points

The header includes `OSDMap` and `MOSDOp`, making the type part of the OSD request layer rather than a generic utility. It is included by `OpRequest.h`; `OpRequest::classes()` exposes `OpInfo` class metadata to capability checks in `OSDCap.cc`. `PrimaryLogPG` depends on `OpInfo` predicates to choose lock and cache behavior.

## Risks and Test Signals

The main API risk is stale `classes` entries if an `OpInfo` instance is reused and `clear()` resets only `rmw_flags`. That behavior should be reviewed against actual lifecycle expectations in `OpRequest`. Other risks are mismatched declarations and implementation when new RMW flags are added. Compile coverage, request classification tests, class authorization tests, and regression tests around reused `OpInfo` objects are useful signals.
