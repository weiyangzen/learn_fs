# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/skbedit.json

## Purpose

`skbedit.json` contains 30 tc-testing cases for the `skbedit` action. It validates packet metadata edits for mark, mark mask, priority, queue mapping, packet type, control actions, cookies, index bounds, batch add/delete, and rejection of invalid values.

## Important APIs, Types, and Schema

The manifest uses standard tc-testing fields and requires `nsPlugin`. It drives `$TC actions add|replace|del|flush|list|get action skbedit`. The action grammar under test includes `mark <u32>[/<mask>]`, `prio|priority`, `queue_mapping <u16>`, `ptype host|otherhost`, `inheritdsfield`, control actions, index, and cookie.

## Control Flow

Tests flush `skbedit`, run an add/replace/delete/list/get operation, then assert textual output. Positive cases match normalized mark/mask, priority formatting as `priority :N`, queue mapping, ptype, control action, index, ref, cookie, and batch-created entries. Negative cases expect exit code `255` and assert the invalid value is absent.

## State and Persistence Behavior

State resides in the tc action table. Replace updates an existing mark mask at index 1. Index bounds are explicitly covered with maximum `4294967295` and rejection of `4294967297`. Batch tests create 32 actions with all parameters and cookie, then delete the same 32 indexes. Invalid goto-chain replace preserves an existing action at index 90.

## Dependencies and Integration Points

The tests require `$TC`, `nsPlugin`, and skbedit action support. They are parser/action-table tests, not datapath tests. The batch cases use shell loops in `cmdUnderTest`, so they also depend on `bash` and `seq` availability in the test environment.

## Risks

Output spacing around `skbedit  mark`, priority formatting, and mask normalization is fragile. The tests do not verify packet metadata changes on live packets, only creation and rendering. Batch command construction uses shell quoting and accumulated arguments, which can fail differently if shell behavior changes.

## Test Signals

Coverage includes valid marks, 32-bit mark maximum, out-of-range marks, valid masks including `0xffffffff`, invalid oversized and malformed masks, replace mask, valid and invalid priority, queue mapping and overflow beyond 16-bit, ptype host/otherhost and invalid ptype, controls `pipe`, `reclassify`, `pass`, `drop`, `jump`, and `continue`, cookie, list, max and oversized index, delete, flush, invalid goto-chain preservation, and 32-action batch add/delete.
