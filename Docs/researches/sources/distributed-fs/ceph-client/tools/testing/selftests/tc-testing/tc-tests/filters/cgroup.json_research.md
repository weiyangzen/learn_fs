<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/cgroup.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/cgroup.json

## Purpose
This fixture defines 56 tests for the `cgroup` classifier and its ematch support. It mirrors much of the basic classifier ematch coverage but attaches it to `tc filter ... cgroup`, validating how cgroup filters parse, store, dump, replace, and delete match expressions and action chains. Categories are mostly `filter/cgroup`, with at least one case also tagged `filter/drop`.

## Important APIs, Types, And Functions
The TDC schema fields drive `tc filter add|replace|delete|show dev $DEV1 parent ffff: ... cgroup`. The file requires `nsPlugin`. Tested command arguments include `handle`, `protocol ip`, `prio`, `cgroup match '...'`, and actions `drop`, `pass`, `pipe`, `skbedit mark 7 pipe`, and `gact drop`. The expression APIs are `cmp`, `u32`, and `canid`, with the same layer aliases, widths, masks, offsets, boolean operators, and SFF/EFF CAN ID syntax used by the basic fixture.

## Control Flow
Each test creates an ingress qdisc on `$DEV1`, executes a cgroup filter operation, verifies via `tc filter show dev $DEV1 parent ffff:`, and removes the qdisc. Positive add cases expect one match in dump output. Negative parser cases expect exit `1` and zero matches. Replacement seeds a cgroup filter, replaces its match expression, and verifies the new normalized `cmp` expression. Deletion removes the previously installed filter and verifies that the old expression is no longer present.

## State And Persistence Behavior
The persisted state is a cgroup classifier instance attached to ingress. Output includes protocol, priority, classifier name, chain number, handle, normalized ematch expressions, and attached action state. The fixture checks normalization of `cmp` layers (`link` to `0`, `network` to `1`), `trans` display, boolean operators, `u32` value/mask expansion, negative offsets, `nexthdr+` offsets, and CAN ID display. Invalid ematch syntax or out-of-range value/mask inputs must fail before state is installed.

## Dependencies And Integration Points
The file depends on cgroup classifier support, ematch modules, ingress qdisc support, gact and skbedit actions, tc-testing variable expansion, and namespace isolation. It integrates with common tc classifier mechanics (`parent ffff:`, `protocol`, `prio`, `handle`, `chain`) and with the same ematch parser used by other classifiers. Its show-based verification makes it more dependent on dump formatting than on packet-level behavior.

## Risks
One negative case named as a cgroup test uses `basic match` in `cmdUnderTest`, which likely intentionally checks that an invalid command does not produce cgroup output, but it is a maintenance trap. The fixture has many format-sensitive regexes for normalized masks, CAN ID order, and action output. Because most verification uses `show` rather than `get`, unrelated filters left behind by failed teardown could affect match counts if namespace isolation breaks. Exact parser exit code `1` is assumed across malformed `u32` cases.

## Test Signals
Signals include successful cgroup filters with `cmp` widths and layers, boolean ematch composition, `u32` across widths and offset forms, SFF/EFF CAN ID matches and masks, action attachment, replacement to a different match, and deletion. Negative signals cover over-wide values/masks, missing syntax elements, and non-numeric fields. Passing results demonstrate that cgroup classifier ematches share the expected parser and dump behavior with basic while preserving cgroup-specific classifier state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/cgroup.json -->
