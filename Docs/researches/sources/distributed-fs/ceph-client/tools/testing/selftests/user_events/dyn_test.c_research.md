<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/dyn_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/dyn_test.c

## Purpose
Checks that user_events dynamic_events parser and direct ABI parser accept and reject the same event field syntax and enforce format matching.

## Important APIs, Types, and Functions
parse_dyn, parse_abi, parse, check_match, TEST_PARSE/TEST_NPARSE, TEST_MATCH/TEST_NMATCH.

## Control Flow
Writes dynamic event definitions to /sys/kernel/tracing/dynamic_events and registers equivalent ABI definitions, deletes temporary events, then verifies accepted scalar, array, loc, struct-size, and name/type matching cases.

## State and Persistence
Creates __test_event under tracefs and deletes it after parse/match checks; uses one fixture enable word.

## Dependencies and Integration Points
Requires tracefs/user_events_data/dynamic_events and root via user_events_selftests.h.

## Risks and Edge Cases
Parser equivalence is sensitive to kernel grammar changes; cleanup waits for event deletion but can be affected by busy refs.

## Test Signals
Pass means ABI and dynamic parser results agree and same-name format matching rejects incompatible definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/dyn_test.c -->
