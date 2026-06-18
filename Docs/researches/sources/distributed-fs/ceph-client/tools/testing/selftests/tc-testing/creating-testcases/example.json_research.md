# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/creating-testcases/example.json

## Purpose
Documents simple tc-testing JSON case structure using three non-network examples. It is an authoring reference rather than a kernel feature test suite.

## Important APIs, Types, And Functions
Each object demonstrates fields `id`, `name`, `category`, `setup`, `cmdUnderTest`, `expExitCode`, `verifyCmd`, `matchPattern`, `matchCount`, and `teardown`.

## Control Flow
The examples show runner ordering: setup commands create a temporary directory or file, command under test runs, verify command output is matched against regex/count expectations, and teardown removes state. One case shows no meaningful verify beyond `/bin/true`, and one shows empty setup/teardown arrays.

## State And Persistence
Temporary state is under `mytest` and is removed in teardown. No kernel state is required.

## Dependencies And Integration Points
Serves as documentation for the tc-testing runner schema consumed by the real test JSON files.

## Risks
Because this file is illustrative, running it in a shared directory could conflict with an existing `mytest` path. It does not demonstrate plugins or JSON matching.

## Test Signals
When run, the examples pass if `touch`, `ls`, `grep`, `ip`, and teardown behave as expected.
