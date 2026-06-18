# sources/distributed-fs/beegfs-go/rst/remote/internal/job/job.go

## Purpose
Defines BeeRemote job persistence and work-submission behavior. A `Job` wraps the protobuf job, stores regenerated transfer segments, tracks worker results, creates new jobs from requests, and serializes/deserializes jobs for Badger/gob storage.

## Important APIs, Types, And Functions
Exports `Job`, `Job.Get`, `Job.GetSegments`, `Job.InTerminalState`, `Job.InActiveState`, `Job.GenerateSubmission`, `Job.Complete`, `New`, `Job.GobEncode`, `Job.GobDecode`, `Segment`, `Segment.GobEncode`, and `Segment.GobDecode`.

## Control Flow
`New` creates a UUID, normalizes request path to absolute mount-relative form, initializes state `UNASSIGNED`, and accepts builder/sync/mock requests. `GenerateSubmission` calls the RST provider to generate work requests only when segments are absent; it stores cloned segments and later recreates requests from persisted segments for idempotence. `Complete` converts stored worker results into protobuf work records and delegates completion/abort cleanup to the RST provider. Gob encoding marshals the protobuf job separately, gob-encodes segments and work results, and prefixes the job bytes with a two-byte length.

## State And Persistence
Persistent job state includes protobuf job metadata/status, generated segments, and work results. Individual work requests are intentionally not persisted; they are regenerated from job plus segments. Job IDs are UUID strings. Gob serialization is the on-disk contract and must be updated when `Job` fields change.

## Dependencies And Integration Points
Integrates BeeRemote protobuf jobs, flex work requests, common RST provider interfaces, worker result types, worker manager job submissions, UUID generation, protobuf clone/marshal/unmarshal, gob, and timestamp generation.

## Risks And Edge Cases
`Get` returns the underlying protobuf pointer, so callers can mutate job state directly. The two-byte job-data length prefix limits marshaled job size to 65535 bytes; larger jobs would truncate length. `GobDecode` returns nil if segment decode fails, silently ignoring that error before decoding work results. Comments mention duplicate UUID consequences but probability is low. Segment regeneration intentionally does not re-check file size, so resumed submissions preserve original segmentation even if the file changed.

## Test Signals
`job_test.go` covers terminal-state classification. Missing tests include path normalization, accepted/rejected request types, idempotent submission generation, complete/abort delegation, gob round trip, large serialized job failure behavior, and decode error handling.
