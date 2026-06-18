# sources/distributed-fs/ceph-client/tools/testing/selftests/splice/default_file_splice_read.c

## Purpose
Minimal helper that invokes a huge `splice()` from stdin to stdout to test default file splice-read behavior.

## Important APIs, types, and functions
`main()` calls `splice(0, 0, 1, 0, 1 << 30, 0)` and returns zero.

## Control flow
No argument parsing; it simply tries to splice up to 1 GiB from fd 0 to fd 1.

## State and persistence
No persistent state.

## Dependencies and integration points
Called by `default_file_splice_read.sh` with stdin redirected from `/dev/null`.

## Risks
Return value is ignored; the paired script detects leaked output by counting stdout bytes.

## Test signals
Expected behavior with `/dev/null` is zero bytes emitted.
