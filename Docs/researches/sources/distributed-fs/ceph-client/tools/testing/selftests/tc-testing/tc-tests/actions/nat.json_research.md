# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/nat.json

## Purpose

`nat.json` contains 27 tc-testing cases for the `nat` action. It validates ingress and egress address translation syntax, control actions, index bounds, special address keywords, cookies, replace rejection for unsupported goto-chain control, and delete behavior.

## Important APIs, Types, and Schema

The manifest uses standard test keys for tc-testing: `id`, `name`, `category`, `plugins.requires`, `setup`, `cmdUnderTest`, `expExitCode`, `verifyCmd`, `matchPattern`, `matchCount`, and `teardown`. It requires `nsPlugin` and drives `$TC actions add|replace|del|flush|ls|get action nat`.

The command grammar under test is `nat ingress <oldaddr> <newaddr>` and `nat egress <oldaddr> <newaddr>` with optional control action, `index`, and `cookie`. Address operands include explicit IPv4 addresses and aliases `default`, `any`, and `all`, which should render as `0.0.0.0/0`.

## Control Flow

Cases flush `nat` state before setup. Positive add cases execute the command and verify text output via `ls` or `get`. The expected rendering includes direction, normalized source prefix, replacement address, control action, index, ref, and cookie when present. Negative cases expect exit code `255`, then query the would-be index and assert zero matches. Delete cases pre-create an action, delete by index, and assert absence, or attempt deletion of a non-existent index and assert the existing action remains.

## State and Persistence Behavior

State is confined to tc action entries of kind `nat`. Index tests explicitly exercise maximum 32-bit index `4294967295` and rejection of larger values. The invalid goto-chain replace test starts with an existing action at index 90 and then verifies that the invalid replacement does not overwrite the old `drop` action. Special address aliases persist in normalized CIDR form.

## Dependencies and Integration Points

The file depends on `$TC`, iproute2 support for `nat`, and a test namespace. It does not install filters or send packets, so it validates parser and action-table behavior rather than datapath translation. It integrates with tc-testing through regex assertions.

## Risks

The action is older and output has double spaces in patterns such as `action order ...:  nat`, making the tests sensitive to spacing changes. Alias rendering for `default`, `any`, and `all` is assumed to normalize to `0.0.0.0/0`; output changes there could cause false failures. Since no packets are sent, the file does not prove actual NAT rewriting, only command parsing and action representation.

## Test Signals

Coverage includes default `pass`, `pipe`, `continue`, `reclassify`, `jump`, and `drop` for ingress and egress, maximum index, invalid oversized index, invalid IPv4 address, stray argument rejection, special address aliases, cookie output for both directions, invalid goto-chain replace preservation, valid delete, and invalid delete. Successful cases expect exactly one match; rejected parse paths expect no persisted action.
