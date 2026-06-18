<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/basic.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/basic.json

## Purpose
This file defines 60 tests for the `basic` classifier under `tc filter`. It focuses on ematch expression parsing and dump fidelity rather than packet forwarding. The fixture validates `cmp`, `u32`, and `canid` ematches, boolean composition with `not`, `and`, and `or`, action attachment, classid/flowid output, list/show behavior, and a set of malformed expression cases that must fail without leaving a filter behind.

## Important APIs, Types, And Functions
The JSON fixture uses the common TDC schema and requires `nsPlugin`. Its command surface is `tc filter add|get|show dev $DEV1 parent ffff: ... basic`. Each test installs an ingress qdisc on `$DEV1`, then adds or queries a basic filter under parent `ffff:`. Important filter arguments include `handle`, `protocol ip`, `prio`, `basic match '...'`, optional `classid 1:1`, and action chains such as `action pass`, `action skbedit mark 7 pipe action gact drop`, or `action gact drop`. Ematch APIs covered include `cmp(TYPE at OFFSET layer LAYER mask MASK [trans] OP VALUE)`, `u32(WIDTH VALUE MASK at OFFSET)`, and `canid(sff|eff ID[:MASK] ...)`.

## Control Flow
Every case creates ingress state in setup and deletes it during teardown. Add cases run one `tc filter add` command, then query the filter with `tc filter get` for a precise handle/prio/protocol or `tc filter show` for aggregate list cases. Positive tests assert a single match against normalized output. Negative parser tests expect exit code `1` and zero matches. The two list-oriented cases seed multiple filters in setup, then add or show additional filters and verify that dump counts match the expected number of basic classifier entries or ematch appearances.

## State And Persistence Behavior
The persisted state is a filter attached to the ingress qdisc. Handles are printed in hexadecimal, priorities are normalized as `pref`, and layer aliases are printed numerically: link as `0`, network as `1`, and transport as `2`. `cmp` tests ensure that parser choices survive dump output, including width, offset, layer, mask, comparison operator, and `trans`. `u32` tests exercise normalization of smaller widths into 32-bit value/mask display, negative offsets, and `nexthdr+` offsets. `canid` tests verify canonical uppercase hex display, mask truncation for SFF, and deterministic output ordering when SFF and EFF are mixed.

## Dependencies And Integration Points
The fixture depends on the ingress qdisc, basic classifier, ematch parser modules for `cmp`, `u32`, and `canid`, action modules such as gact and skbedit, and iproute2 output formatting. It also depends on TDC variable expansion for `$TC` and `$DEV1`. It integrates with shared classifier infrastructure through `parent ffff:`, `handle`, `protocol`, `prio`, and action chain syntax.

## Risks
The test suite is strongly coupled to printed normalization. For example, masks such as `0x00ff` may print as `0xff`, aliases print as numeric layers, and SFF CAN IDs are masked down before display. These are useful regression signals but can fail on harmless printer refactors. The negative `u32` cases mostly expect exit `1`, so changes in iproute2 parser error codes could require test updates. Because the tests attach to ingress qdisc state, teardown failures can cascade into later cases unless the harness isolates namespaces reliably.

## Test Signals
Positive signals cover `cmp` across link/network/transport layers, `trans`, u8/u16/u32 widths, single and multiple actions, boolean ematch composition, `u32` offsets including negative and `nexthdr+`, SFF/EFF CAN ID lists and masks, and list/show output. Negative signals cover over-wide `u32` values and masks, missing offsets, missing `at`, missing values, and non-numeric values or masks. A passing run shows that the basic classifier can parse, store, normalize, and dump a broad ematch surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/basic.json -->
