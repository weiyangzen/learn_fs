# sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/create-read.c

## Purpose
Small helper verifying that a newly created efivarfs variable opened read/write returns EOF before data has been committed, and that closing succeeds.

## Important APIs, Types, And Functions
Uses `open(path, O_RDWR | O_CREAT, 0600)`, `read()`, `close()`, and standard error reporting.

## Control Flow
The program expects one path argument, opens/creates it, reads four bytes, fails if the read returns anything other than 0, closes, and exits success.

## State And Persistence
It creates a variable path supplied by the shell test. The parent script checks the file is gone afterward.

## Dependencies And Integration Points
Called by `efivarfs.sh` in `test_create_read()`. Requires root and efivarfs path semantics.

## Risks
The helper does not unlink/cleanup on failure; caller handles final checks. It tests only the immediate read behavior, not later writes.

## Test Signals
Success is read returning EOF on a new variable. Any open failure or nonzero read is a failure.
