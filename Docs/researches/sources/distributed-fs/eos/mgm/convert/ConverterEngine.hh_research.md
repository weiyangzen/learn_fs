# sources/distributed-fs/eos/mgm/convert/ConverterEngine.hh

## Purpose
Declares the converter service API, internal QuarkDB helper, runtime queues, observer integration, and configuration surface for MGM file conversions.

## Important APIs and Types
- `JobInfoT` stores fid, conversion string, and optional callback.
- `JobStatusT` aliases `ConversionJobStatus`; `ObserverT` publishes status changes keyed by conversion string.
- Public API: `Start`, `Stop`, `ScheduleJob`, running/thread-pool/pending/failed counters, pending clear/list, observer access, config apply/set/serialize.
- `QdbHelper` owns QClient and `QHash` for the pending-job hash and exposes iterator/list/add/remove/clear helpers.
- Private thread helpers: `Convert`, `JoinAllConversionJobs`, `PopulatePendingJobs`, `HandlePostJobRun`, and `StoreConfig`.

## Control Flow and State
The constructor wires QDB helper, thread pool defaults, max queue size, and observer manager. The class keeps atomic running/failure/config counters, a concurrent pending queue, a protected running-job map, and an assisted thread.

## Dependencies and Integration Points
Depends on EOS logging, observer manager, global OFS, conversion job, namespace metadata, QuarkDB qclient/QHash, thread pool, and callbacks. Exposes `GetThreadPoolInfo` for operational inspection.

## Risks
- `NumPendingJobs` lacks `const` and exposes the in-memory queue only.
- `GetPendingJobs` returns durable QDB jobs, while `NumPendingJobs` returns memory queue size; callers may confuse the two.
- Constructor uses `std::thread::hardware_concurrency()` directly; if it returns 0, thread pool behavior depends on `ThreadPool` handling.
- The header exposes `QdbHelper::PendingJobsIterator`, coupling tests/callers to qclient iterator details.

## Test Signals
Header-level tests should validate construction with fake `QdbContactDetails`, config serialization defaults, public counter semantics, and QdbHelper hash behavior against a test QuarkDB or mock wrapper.
