# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/JobFactoryProducer.java

## Purpose
`JobFactoryProducer` centralizes creation of scheduler `JobFactory` instances from either client job requests or journal entries. In this source slice, it supports only load jobs.

## Important APIs, types, and functions
`create(JobRequest, FileSystemMaster)` returns a `LoadJobFactory` for `LoadJobRequest` or throws `IllegalArgumentException`. `create(Journal.JournalEntry, FileSystemMaster)` returns `JournalLoadJobFactory` when `entry.hasLoadJob()` or throws.

## Control flow
Both factory methods perform type/field discrimination and delegate all actual job construction to concrete factories.

## State and persistence behavior
The class is stateless and non-instantiable. It is part of persistence recovery because journal entries are converted back into job factories.

## Dependencies and integration points
It depends on `JobRequest`, `LoadJobRequest`, `FileSystemMaster`, journal proto entries, and scheduler `JobFactory`. Scheduler/job manager code uses it at submission and recovery boundaries.

## Risks
Adding new job types requires updating both overloads. Unknown journal entries include the entire entry in the exception, which may be verbose. There is no null validation here beyond downstream constructors.

## Test signals
Tests should cover load request creation, load journal creation, unknown request and unknown journal errors, and future job-type registration behavior.
