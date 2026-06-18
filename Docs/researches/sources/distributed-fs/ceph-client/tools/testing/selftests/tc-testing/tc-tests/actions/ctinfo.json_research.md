# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/ctinfo.json

## Purpose
Defines 12 tests for the `ctinfo` action parser and lifecycle.

## Important APIs, Types, And Functions
Cases cover default settings, DSCP masks/stats, `cpmark` with zone, drop control, replace changing zone/control, valid and invalid delete, list, flush, duplicate index, invalid index over 32 bits, and invalid `goto_chain` control.

## Control Flow
All cases require `nsPlugin`, run a `tc action add/replace/delete/list/flush action ctinfo` command, compare expected exit code, and verify textual `tc` output for zone, action control, index, ref count, dscp/cpmark fields, and counts.

## State And Persistence
Per-namespace tc action state persists within a case and is reset by teardown.

## Dependencies And Integration Points
Depends on `NET_ACT_CTINFO`, conntrack mark/DSCP support, namespace setup, and tc action output formatting.

## Risks
DSCP/cpmark mask rendering and invalid goto-chain fallback behavior are parser/output sensitive. Some expected failures still verify preexisting state, so setup correctness is important.

## Test Signals
Signals include correct ctinfo field rendering, replace updating state, delete/flush reducing counts, duplicate/invalid indexes rejected, and invalid goto-chain leaving or showing expected pass behavior.
