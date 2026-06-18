# sources/cloud-native/moby/daemon/libnetwork/iptables/iptables_test.go

## Purpose
Integration-tests Linux iptables helper behavior against actual iptables commands.

## Important APIs, Types, And Functions
- `createNewChain` sets up NAT and filter chains.
- `TestNewChain`, `TestLink`, `TestPrerouting`, `TestOutput`, `TestConcurrencyWithWait`, `TestCleanup`, `TestExistsRaw`, `TestRule`, and `TestFlushChain` cover the helper API.
- `addSomeRules` adds representative DNAT, filter, and masquerade rules.
- `mustDumpChain` inspects chain rules through `iptables -S`.

## Control Flow
Tests create chains, add rules via helper methods, verify existence through `Exists` or `iptables-save`, and clean up. Some tests use `netnsutils.SetupTestOSContext` to isolate rules; firewalld-running cases are skipped where host namespace passthrough cannot modify the test namespace.

## State And Persistence
Mutates iptables state and depends on cleanup. Uses hard-coded test chain names such as `DOCKEREST`, `TESTCHAIN`, and `TESTFLUSHCHAIN`.

## Dependencies And Integration Points
Requires Linux, iptables binaries, suitable privileges, and sometimes network namespace support. Uses `errgroup` for concurrent rule additions.

## Risks
Environment sensitivity is high. Missing privileges or firewalld namespace mismatches can skip or fail tests. Hard-coded chain names can collide if cleanup failed from a previous run.

## Test Signals
Confirms idempotent rule operations, exact reciprocal link rules, `--wait` preventing xtables lock failures under concurrency, cleanup removing chain references, raw existence checks rejecting truncated rules, and flush preserving empty chain definitions.
