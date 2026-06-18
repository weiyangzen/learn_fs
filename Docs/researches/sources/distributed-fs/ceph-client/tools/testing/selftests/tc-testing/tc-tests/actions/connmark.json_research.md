# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/connmark.json

## Purpose
Defines 15 tc tests for the `connmark` action parser and action-table lifecycle.

## Important APIs, Types, And Functions
Cases cover default creation, controls `pass`, `drop`, `pipe`, `reclassify`, `continue`, and `jump`, zone argument handling, unsupported/invalid arguments, replace, cookie, invalid `goto chain`, delete valid index, and delete invalid index. All require `nsPlugin`.

## Control Flow
Each case sets up isolated namespace state, runs `tc actions add/replace/del action connmark ...`, verifies with `tc actions get/list`, and matches textual output for zone, control action, index, ref count, and cookie. Negative cases expect no matching installed action or nonzero exit codes.

## State And Persistence
State is per-network-namespace tc action state plus conntrack-related action metadata. Teardown removes actions and namespace state.

## Dependencies And Integration Points
Depends on `NET_ACT_CONNMARK`, conntrack mark support, namespace setup, and iproute2 `tc`.

## Risks
Zone max/invalid handling and default control rendering are parser-sensitive. Regex checks rely on stable `tc` text output. Some tests use the same index values across cases and rely on isolation/teardown.

## Test Signals
Pass signals include correct zone display, action controls, ref counts, cookie preservation, and rejection of invalid zone/unsupported argument/goto-chain cases.
