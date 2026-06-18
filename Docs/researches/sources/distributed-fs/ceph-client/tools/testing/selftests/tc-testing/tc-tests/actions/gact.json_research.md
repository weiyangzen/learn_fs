# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/gact.json

## Purpose
Defines 27 tests for the generic action (`gact`) family, including controls, index boundaries, list/flush/delete/get, batch operations, random/deterministic control parsing, `no_percpu`, and referenced-action flush behavior.

## Important APIs, Types, And Functions
Cases cover `pass`, `pipe`, `reclassify`, `drop`, `continue`, invalid `pump`, duplicate/oversized/max indexes, list/flush, deletion by control/index, replace, get by large index, batches of 32 actions, random deterministic goto-chain controls, invalid goto-chain replace, `no_percpu`, and flush attempts while actions are bound to filters.

## Control Flow
All cases use `nsPlugin`. Commands create or mutate actions, sometimes with setup-created referenced filters, then verify `tc actions list/get` output with regex counts and ref/bind values. Batch cases use shell loops to generate many action clauses.

## State And Persistence
Per-namespace action and filter state persists across setup, command, verify, and teardown. Referenced-action tests intentionally leave a bound action during flush verification to ensure reference protection.

## Dependencies And Integration Points
Depends on `NET_ACT_GACT`, matchall/filter support for reference tests, namespace setup, and tc parser support for random/deterministic action syntax.

## Risks
Regexes assume exact textual wording for ref/bind counts and random control output. Flush behavior for referenced actions is semantically delicate and can change with kernel fixes. Batch quoting is error-prone.

## Test Signals
Pass signals are correct action control rendering, rejected invalid controls/indexes, successful batch add/delete counts, `no_percpu` display, and flush refusing or preserving actions with active filter references as expected.
