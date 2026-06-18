# sources/distributed-fs/ceph-client/tools/testing/selftests/splice/default_file_splice_read.sh

## Purpose
Checks that splicing from `/dev/null` through the default file splice path does not leak data.

## Important APIs, types, and functions
Runs `./default_file_splice_read </dev/null | wc -c` and compares the count to zero.

## Control flow
If byte count is `0`, exits success. Otherwise prints a leak message and exits failure.

## State and persistence
No persistent state.

## Dependencies and integration points
Depends on the helper binary and standard `wc`.

## Risks
Assumes current directory contains the built helper.

## Test signals
Exit 0 means no leaked output; failure prints `default_file_splice_read broken: leaked <n>`.
