# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/bootstrap/walker_test.go

Purpose: broad unit/regression coverage for the lifecycle bootstrap walker.

Important APIs/types: local `recorder`, `dispatchCall`, `mustTime`, and `compileEvDriven` support tests of `Walk`.

Control flow: tests compile active snapshots, feed in-memory entries through `EntryCallback`, and assert dispatch calls/checkpoints. They cover normal due dispatch, multi-action shape-specific dispatch, not-yet-due skip, date action before/after rule date, directory skip, disabled mode skip, pending bootstrap inactivity, failure halt and checkpoint behavior, resume, MPU init destination-key matching, and MPU/noncurrent shape separation.

State and persistence behavior: checkpoint expectations are central: completed walks set `Completed` and last scanned path; failed dispatch leaves the checkpoint at the last successfully processed path.

Dependencies and integration points: exercises engine compilation/prior state, lifecycle action kinds, `EvaluateAction`, and bootstrap dispatcher contract with a fake.

Risks: uses in-memory list ordering rather than filer ordering, so pagination and version expansion risks are covered in dailyrun filer-list tests instead. Some tests use artificial entries that would not all appear together in production, intentionally to isolate action gates.

Test signals: strong signal for prior regressions around multi-action rules, date actions lacking a dedicated scheduler, and MPU/noncurrent dispatch crossing.
