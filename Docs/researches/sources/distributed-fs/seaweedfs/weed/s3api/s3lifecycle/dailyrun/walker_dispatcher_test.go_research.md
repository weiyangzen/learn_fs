# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_dispatcher_test.go

Purpose: unit tests for `WalkerDispatcher` request construction, outcome classification, limiter behavior, and guard errors.

Important APIs/types: `walkerStubClient`, `sampleAction`, and multiple `TestWalkerDispatcher_*` cases.

Control flow: fake client captures last request and returns scripted outcome/error/nil response. Tests call `Delete` with bootstrap entries and compiled actions.

State and persistence behavior: none. Tests validate error returns that upstream walker uses to halt/resume.

Dependencies and integration points: uses lifecycle proto outcomes, bootstrap entries, engine compiled actions, testify, and `rate.Limiter`.

Risks: no test asserts metric labels directly. Limiter timing test depends on wall-clock delay and may be sensitive on slow/loaded CI, though it uses a modest threshold.

Test signals: strong guard for the MPU anti-pattern of dispatching `DestKey` instead of `.uploads/<id>`, and for treating unresolved server outcomes as walker-stopping errors.
