# sources/distributed-fs/ceph/src/rgw/rgw_http_client_types.h

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This header defines request I/O correlation helpers: `rgw_io_id`, atomic `RGWIOIDProvider`, and abstract `RGWIOProvider`. The state is process-local ids and channel masks used by HTTP completion integration. `rgw_io_id::intersects()` and `operator<()` support lookup/comparison, while `RGWIOProvider` carries user-info hooks for subclasses. Risks include the exact `intersects()` mask semantics and the `id` initialization versus `assign_io()` condition. Tests should cover monotonic ids, ordering, repeated assignment, channel retrieval, and same-id/different-id intersection behavior.
