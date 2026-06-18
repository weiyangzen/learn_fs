# sources/distributed-fs/ceph/src/osd/ECInject.cc

Purpose: `ECInject.cc` implements fault-injection controls for EC read, write, and parity-read paths. It lets tests force medium errors, missing shards, dropped writes, simulated OSD-down events, aborts, and parity read behavior for targeted objects or wildcard objects.

Important APIs and functions: `read_error`, `write_error`, and `parity_read` configure injections. `clear_read_error`, `clear_write_error`, and `clear_parity_read` remove them. `test_read_error0/1`, `test_write_error0/1/2/3`, and `test_parity_read` are called by backend paths to decide whether to alter behavior. `test_error` is the shared countdown/duration evaluator.

Control flow: configuration normalizes wildcard object names by setting hash zero and, for some write error types, collapses the shard to `NO_SHARD`. Test functions look up the exact object first, then a wildcard variant. Each match decrements the `when` counter until active, then decrements `duration` and erases exhausted injections. Type-0 write injection is multi-stage: it records the client `reqid`, injects a one-shot dropped shard write, and later fails the retried request.

State and persistence: all injection state is process-local static data protected by a `ceph::recursive_mutex`: maps of object to `(when, duration)`, a type-0 shard map, a retry `reqid` set, and a parity-read set. Nothing is persisted; state disappears on process restart.

Dependencies and integration: it depends on `ghobject_t`, `hobject_t`, `osd_reqid_t`, `shard_id_t`, and Ceph mutex utilities. EC read/write/recovery code calls the test functions to simulate failure modes.

Risks: static global state can leak between tests if not cleared. Wildcard handling mutates object names and hashes, so inconsistent normalization can miss injections. Type-0 write injection has coupled state across maps/sets; partial cleanup would make later writes behave unexpectedly.

Test signals: unit or integration tests should cover countdown semantics, wildcard matching, automatic removal after duration, type-0 retry failure, type-1 chaining into type-2 down injection, and clear functions reporting remaining injections.
