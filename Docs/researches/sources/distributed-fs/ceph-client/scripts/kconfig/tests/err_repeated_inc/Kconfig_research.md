# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_repeated_inc/Kconfig

## Purpose
This fixture starts a repeated include scenario by sourcing `Kconfig.inc1`.

## Important APIs, Types, and Functions
The file contains one source statement.

## Control Flow
The scanner should detect repeated inclusion through included fixture files and fail.

## State and Persistence
No persistent state.

## Dependencies and Integration Points
Targets source include tracking.

## Risks and Edge Cases
The repeated include details are in files outside this work item; this file is the test entry.

## Test Signals
The paired test expects nonzero exit and matching stderr.
