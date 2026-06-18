# sources/distributed-fs/ceph-client/include/trace/events/objagg.h

Purpose: Defines tracepoints for object aggregation lifecycle and tree operations. It is used to diagnose creation, destruction, reference handling, parent assignment, and root management in the `objagg` helper.

Important APIs/types/functions: Events include `objagg_create`, `objagg_destroy`, `objagg_obj_create`, `objagg_obj_destroy`, `objagg_obj_get`, `objagg_obj_put`, `objagg_obj_parent_assign`, `objagg_obj_parent_unassign`, `objagg_obj_root_create`, and `objagg_obj_root_destroy`. Fields capture object aggregator pointers, object pointers, roots, deltas, nesting counts, user counts, and parent/root relation data.

Control flow: Objagg core emits lifecycle events when an aggregator is allocated, objects are created or destroyed, references are taken or dropped, and candidate parent/root relationships are changed. Trace output reconstructs aggregation tree evolution.

State and persistence: No state is stored by the header. It observes in-memory aggregation nodes and reference counts; persistence is owned by subsystem users such as switchdev resource aggregation.

Dependencies and integration points: Depends on tracepoints and objagg structs from including C files. It integrates with networking/switching code that deduplicates hardware resource programming.

Risks and test signals: Risks include pointer reuse confusing traces, reference-count imbalance, parent/root assignment races, and missing tracepoints around failed allocation paths. Test objagg selftests, create/destroy churn, nested aggregation, refcount underflow cases, and switchdev resource programming failures.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/objagg.h` completely for this pass (228 lines, 4691 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/objagg.h_research.md`.
