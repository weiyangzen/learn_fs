# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/simple.json

## Purpose

`simple.json` defines 9 tc-testing cases for the `simple` action. It validates simple string payload storage through `sdata`, change and replace behavior, duplicate index rejection, listing, deletion, flushing, and cleanup after failed batched action operations.

## Important APIs, Types, and Schema

The file follows the standard tc-testing manifest schema and uses `$TC actions add|change|replace|delete|flush|list action simple`. The primary command grammar is `simple sdata <string> [index <u32>]`, with optional invalid `goto chain` and `cookie` in the replace rejection case.

## Control Flow

Tests flush or pre-create simple actions, execute a tc action command, and verify with `actions list action simple`. Positive assertions match rendered strings such as `Simple <A triumph>` and index/ref output. Negative assertions check that duplicate add and invalid goto-chain replace do not create or overwrite the target action. The last two tests exercise batch cleanup behavior by arranging a failed batch setup and then verifying only the expected action remains.

## State and Persistence Behavior

The action table stores an indexed simple action and its string payload. `change` mutates an existing action at index 60. Delete and flush remove persisted entries. The invalid replace test verifies an existing `hello` action at index 90 remains after a rejected `goto chain` replacement.

## Dependencies and Integration Points

The manifest depends on `nsPlugin`, `$TC`, and the kernel simple action. It is integrated only through action management commands and regex matching. It provides a small sanity suite for action lifecycle behavior that is simpler than parser-heavy action types.

## Risks

The action's output format is concise, so regexes are sensitive to `Simple <...>` formatting and capitalization. The file does not test packets or action execution, only storage and management. Batch-cleanup tests depend on setup semantics in the tc-testing runner, so their meaning is partly outside the JSON object itself.

## Test Signals

Signals include successful add, successful change, duplicate index rejection, listing three preloaded actions, delete, flush, invalid goto-chain replace preserving old state, and cleanup validation for failed batch add/change scenarios.
