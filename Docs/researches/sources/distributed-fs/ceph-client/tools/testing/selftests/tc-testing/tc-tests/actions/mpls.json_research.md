# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/mpls.json

## Purpose

`mpls.json` defines 53 tc-testing cases for the `mpls` action. It validates parsing and rendering for `dec_ttl`, `pop`, `push`, and `mod` operations, including valid and invalid MPLS label, traffic class, TTL, BOS, protocol, cookie, replace, delete, and flush behavior.

## Important APIs, Types, and Schema

The manifest uses the standard tc-testing object schema: identity and category metadata, `nsPlugin`, setup flushes, command under test, expected exit code, verification command, regex match pattern/count, and teardown. The tc API surface is `$TC actions add|replace|del|flush|list|get action mpls`.

The command grammar under test covers `mpls dec_ttl`, `mpls pop protocol <proto>`, `mpls push [protocol mpls_uc|mpls_mc] label <label> [tc <tc>] [ttl <ttl>] [bos <0|1>]`, and `mpls mod label|tc|ttl|bos`. It also validates tc control opcodes: `pipe`, `pass`, `drop`, `reclassify`, `continue`, `jump 10`, and `trap`.

## Control Flow

Each test begins with an `mpls` action flush and then executes a single tc action command. Verification usually lists all `mpls` actions or gets a specific index and matches iproute2 output for operation name, normalized protocol, normalized numeric fields, control action, index, refcount, and cookie. Replace tests pre-create an action then call `actions replace` and assert the new rendered action. Delete and flush tests pre-populate state and then assert that matching entries disappear.

## State and Persistence Behavior

State is maintained in the kernel action table for `mpls`. Most tests use a clean table per case. Replace cases persist a known action at an index and verify replacement rather than addition. The maximum-value checks rely on parser limits rather than persistent data structures: label maximum `0xfffff` is accepted and rendered as `1048575`; `0x100000` is rejected. TTL bounds are 1 through 255, and TC bounds are 0 through 7.

## Dependencies and Integration Points

The suite requires `nsPlugin`, `$TC`, and kernel/iproute2 support for the `mpls` action. It integrates only through action management commands, not through packet datapath filters. It depends on iproute2 rendering names such as `modify` for `mod`, `protocol mpls_uc`, `protocol mpls_mc`, `protocol ip`, and textual control opcodes.

## Risks

The tests are mostly regex-based and therefore exposed to output-format changes. Protocol aliases are a risk because commands use `ipv4` while expected output may contain `ip`. Some invalid tests assert absence via broad patterns, so a future output change could hide a parser regression. The `a70a` invalid TC test looks for `tc.*4` despite issuing `tc 8`, which may make that absence check weaker than intended.

## Test Signals

The file strongly covers operation-specific parser rules: `dec_ttl` rejects label/tc/ttl/bos parameters; `pop` requires protocol and rejects label/tc/ttl/bos; `push` requires an MPLS label and rejects IPv4 protocol, out-of-range label, TC 8, and TTL 0; `mod` accepts label/TC/TTL/BOS modification but rejects out-of-range label, implicit-null label 3, TTL 0/256, BOS 2, and protocol. It also covers cookie rendering, maximum cookie length, replacing push actions, deleting one action, and flushing all actions.
