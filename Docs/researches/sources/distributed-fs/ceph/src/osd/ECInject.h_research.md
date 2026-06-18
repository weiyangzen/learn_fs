# sources/distributed-fs/ceph/src/osd/ECInject.h

Purpose: `ECInject.h` declares the EC fault-injection interface used by test and backend code. It exposes configuration, clearing, and runtime predicate functions without exposing the static state held in `ECInject.cc`.

Important APIs and types: the public namespace contains `read_error`, `write_error`, `parity_read`, `clear_read_error`, `clear_write_error`, `clear_parity_read`, and predicate functions for read types 0/1, write types 0/1/2/3, and parity reads. The declarations use `ghobject_t` when shard identity matters and `hobject_t` when shard-independent matching is intended.

Control flow: callers configure an injection with object, type, activation delay, and duration, then backend paths call the matching `test_*` function at the behavior point. Clear APIs remove configured state by object/type.

State and persistence: the header defines no state. Its contract implies implementation-side process-local mutable state with countdown semantics. No on-disk or PG-log persistence is involved.

Dependencies and integration: includes `common/hobject.h` and `osd_types.h`, making it part of the OSD EC backend support surface. Admin/test paths can configure injections, while EC read/write paths consume the predicates.

Risks: the API uses integer `type` values rather than strongly typed enums, so call sites must preserve the implicit type table. Header comments are absent here, so users need the `.cc` implementation or external documentation to know type meanings.

Test signals: compile-time coverage is minimal; behavioral coverage must come from tests that call each declaration through the backend paths and verify the injected effects, not just return strings.
