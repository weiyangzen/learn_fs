# sources/cloud-native/cri-o/internal/hostport/fake_iptables_test.go

## Purpose
Validates fake iptables restore behavior needed by hostport tests, especially no-flush restore semantics for user-defined versus builtin chains.

## Important APIs, Types, And Functions
- Exercises `newFakeIPTables`, `EnsureChain`, internal `ensureRule`, `writeLine`, `MakeChainLine`, and `Restore`.

## Control Flow
The test creates a fake NAT table with a hostport user chain and a builtin `POSTROUTING` rule, builds a restore payload containing only chain declarations and `COMMIT`, then calls `Restore` with `NoFlushTables`. It asserts the user-defined `KUBE-HOSTPORTS` chain is flushed while builtin `POSTROUTING` keeps its rule.

## State And Persistence
Mutates only fake in-memory table state. No durable persistence.

## Dependencies And Integration Points
Confirms the fake's behavior matches the assumptions of `hostport_iptables.go` tests that rebuild hostport user chains while preserving unrelated builtin chain rules.

## Risks And Edge Cases
The test covers one restore scenario; other parser branches such as `-I`, `-X`, malformed rules, and table filtering are covered indirectly by hostport tests.

## Test Signals
Good targeted signal that fake restore cleanup semantics are sufficient for hostport manager tests.
