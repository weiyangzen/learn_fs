# sources/distributed-fs/ceph/src/rgw/driver/rados/buckets.h

Purpose: Declares the generic owner-bucket cls_user interface used by user/account ownership code to maintain bucket listings and aggregate storage stats.

Important APIs/types/functions: `add()`, `remove()`, `list()`, `write_stats()`, `read_stats()`, `read_stats_async()`, `reset_stats()`, and `complete_flush_stats()` form a thin RADOS object-class API around a supplied `rgw_raw_obj`.

Control flow: The header makes all operations asynchronous-yield aware through `optional_yield`, except the callback-style `read_stats_async()`. Callers control the owner namespace by choosing the raw object and tenant passed to `list()`.

State/persistence: Functions manipulate cls_user bucket entries and header stats on a single RADOS object. `read_stats()` returns aggregate `RGWStorageStats` and optional sync/update timestamps.

Dependencies/integration: Coupled to librados forward declarations, Ceph time, boost intrusive pointer callbacks, `rgw_sal_fwd.h`, `rgw_bucket`, `RGWBucketEnt`, and `RGWStorageStats`.

Risks: The API does not distinguish user and account ownership; passing the wrong object corrupts the wrong owner list. `write_stats()` assumes the bucket entry exists.

Test signals: API consumers should validate correct owner object selection, pagination marker propagation, stats callback lifetime, and behavior against missing owner objects.
