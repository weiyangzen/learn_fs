# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/mirred.json

## Purpose

`mirred.json` is a declarative tc-testing manifest for the `mirred` traffic-control action. It validates mirror and redirect behavior for ingress and egress directions, target selection by device or shared block, control-action encoding, index handling, batch add/delete behavior, and loop-prevention statistics for redirect-to-self paths. The file contains 34 test cases.

## Important APIs, Types, and Schema

The file is a JSON array of test objects consumed by the tc-testing runner. Each object uses the standard manifest fields: `id`, `name`, `category`, `plugins.requires`, `setup`, `cmdUnderTest`, `expExitCode`, `verifyCmd`, `matchPattern` or `matchJSON`, `matchCount`, and `teardown`. Several blockid tests also use `dependsOn` to gate execution on `tc action mirred help` advertising `blockid`.

The tc API surface under test is `$TC actions add|replace|del|flush|list|show|get action mirred`. The command grammar exercised includes `ingress` and `egress`, `mirror` and `redirect`, `dev <ifname>`, `blockid <id>`, action `index`, `cookie`, `no_percpu`, and control actions such as `pass`, `pipe`, `continue`, `reclassify`, `drop`, and `jump <chain>`. The later filter-path tests use `$IP link`, `$IP addr`, `$TC qdisc add`, and `$TC filter add ... matchall action mirred`.

## Control Flow

Most cases flush existing `mirred` actions during setup, run a single `$TC actions ...` command, then verify with `list`, `show`, or `get`. Positive text-output tests match strings such as `Egress Mirror to device lo`, `Egress Redirect to device lo`, control action names, index values, `cookie`, and `no_percpu`. Negative parser tests expect exit code `255` and verify that the rejected action is absent.

The block-target tests add `clsact` qdiscs with `ingress_block` or `egress_block` on `$DEV1`, then add or replace `mirred` actions targeting block id 21. These tests verify structured JSON from `$TC -j actions get`, including `kind`, `mirred_action`, `direction`, `to_blockid` or `to_dev`, `control_action.type`, `index`, `ref`, `bind`, and `not_in_hw`.

The final two cases leave pure action management and install filters on `$DUMMY`. They send one ping that is expected to fail and verify action stats in JSON: `packets: 1` and `overlimits: 1`, proving redirect loop protection increments counters.

## State and Persistence Behavior

State lives in kernel tc action tables and qdisc/filter state inside the test network namespace. The manifest is careful to isolate that state with `actions flush action mirred`, `qdisc del`, and action flush teardown. Duplicate index and replace cases intentionally pre-populate state to prove collision or replacement semantics. Batch cases create 32 indexed actions with shell loops and then delete them as a group.

## Dependencies and Integration Points

All tests require `nsPlugin`, so they assume an isolated network namespace and variables such as `$TC`, `$IP`, `$DEV1`, and `$DUMMY`. Device-target tests use loopback `lo`; block tests require kernel/iproute2 support for `blockid`; loop tests require qdisc and matchall filter support. The manifest integrates with tc-testing's text regex matcher and JSON matcher.

## Risks

Text-output assertions are sensitive to iproute2 formatting changes, especially wording around `Mirror`, `Redirect`, `ref`, `no_percpu`, and control names. Blockid assertions are stricter and depend on JSON fields such as `not_in_hw`; offload-capable environments or changed JSON defaults could affect them. The pattern `[Mirror|Redirect] to device lo` is a character-class style regex rather than a true alternation, so it is less precise than intended. The ping tests use a very short timeout (`-W0.01`), which can be sensitive to ping implementation and timing.

## Test Signals

Coverage is broad: valid egress and ingress mirror/redirect, invalid direction/action/device, duplicate index, all common control actions, cookie, 32-bit maximum index, out-of-range index, delete behavior, 32-action batches, `no_percpu`, dev/block mutual exclusion, missing target rejection, dev-to-block and block-to-dev replacement, and redirect loop accounting. Expected failures consistently use `expExitCode: 255` and absence checks, while expected successes assert exactly one or 32 matching actions.
