# sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/circular_expansion/__init__.py

## Purpose
This pytest module verifies circular variable expansion fails cleanly.

## Important APIs, Types, and Functions
It runs `conf.oldaskconfig()` and checks nonzero exit plus regex-matched stderr.

## Control Flow
The run should abort during preprocessing before configuration interaction.

## State and Persistence
No persistent state beyond captured stderr.

## Dependencies and Integration Points
Depends on `preprocess.c` error messages.

## Risks and Edge Cases
Expected regex must match file/line diagnostics.

## Test Signals
Pass means indirect recursive expansion is caught.
