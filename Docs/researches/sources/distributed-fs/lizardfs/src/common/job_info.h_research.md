<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/job_info.h -->
# sources/distributed-fs/lizardfs/src/common/job_info.h

## Purpose
Defines a small serializable job descriptor used for protocol/storage paths that need an id and human-readable description. The source was read completely for this report.

## Important APIs, Types, And Functions
`LIZARDFS_DEFINE_SERIALIZABLE_CLASS(JobInfo, uint64_t id, std::string description)` generates constructors/accessors/serialization support according to the project macro contract.

## Control Flow
There is no handwritten runtime flow; serialization macros provide pack/unpack behavior.

## State And Persistence Behavior
Instances persist only where callers serialize them in protocol messages or metadata-like structures.

## Dependencies And Integration Points
Depends on `serialization_macros.h`; integrates with generic serialization helpers.

## Risks And Edge Cases
ABI/schema risk is field order: changing `id` or `description` order changes serialized representation.

## Test Signals
Compile and serialization round-trip tests in consumers are the main signal; no dedicated test file is in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/job_info.h -->
