# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/sample.json

## Purpose

`sample.json` contains 29 tc-testing cases for the `sample` action. It validates mandatory `rate` and `group` parsing, optional truncation, control actions, index and field bounds, cookies, replacement of existing actions, invalid goto-chain preservation, and delete behavior.

## Important APIs, Types, and Schema

The manifest uses standard tc-testing JSON fields and requires `nsPlugin`. It drives `$TC actions add|replace|del|list|get action sample`. The action grammar under test is `sample rate <u32> group <u32> [trunc <u32>] [control] [index <u32>] [cookie <hex>]`. Controls include default `pipe`, `continue`, `drop`, `reclassify`, `pipe`, and `jump <chain>`.

## Control Flow

Each test flushes sample actions in setup. Positive add cases verify rendered text such as `sample rate 1/<rate> group <group>`, optional `trunc_size`, control action, index, refcount, and cookie. Mandatory-argument and range failures expect exit code `255` and verify absence. Replacement cases pre-create an index, replace one field, and assert the new value. Delete cases check both successful deletion and failed deletion of a missing index.

## State and Persistence Behavior

State is held in the tc sample action table. Tests verify 32-bit maximum values for `rate`, `group`, `trunc`, and index, and reject values above that range. The invalid goto-chain replace test preserves a previous action at index 90, proving rejected replacement does not corrupt existing state.

## Dependencies and Integration Points

The file depends on `$TC`, `nsPlugin`, and kernel/iproute2 support for `sample`. It does not require psample userspace listeners and does not validate sampled packet delivery; it validates action creation, representation, replacement, and deletion.

## Risks

Because no traffic is generated, runtime sampling behavior and psample netlink emission are outside coverage. Regexes are tied to the textual `rate 1/N`, `trunc_size`, and default `pipe` rendering. There are two tests with the same name and command for missing `group`, which is harmless but redundant.

## Test Signals

Signals include positive coverage for all common controls, invalid `rate 0`, invalid unknown control, missing mandatory arguments, maximum and out-of-range values for rate/group/trunc/index, cookies, replace rate/group/trunc/control at a stable index, invalid goto-chain replace preserving old state, valid delete, and invalid delete preserving existing state.
