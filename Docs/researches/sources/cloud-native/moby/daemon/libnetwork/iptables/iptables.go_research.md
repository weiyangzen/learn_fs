# sources/cloud-native/moby/daemon/libnetwork/iptables/iptables.go

## Purpose
Provides Linux iptables/ip6tables programming helpers for libnetwork. It abstracts tables, chains, actions, policy management, idempotent rule operations, firewalld passthrough, rootless namespace execution, and xtables lock waiting.

## Important APIs, Types, And Functions
- Types: `Action`, `Policy`, `Table`, `IPVersion`, `IPTable`, `ChainInfo`, `ChainError`, and `Rule`.
- `GetIptable` constructs an IPTable for IPv4 or IPv6.
- `NewChain`, `RemoveExistingChain`, `ChainInfo.Remove`, `Prerouting`, `Output`, and `Link` manage chains and common linking rules.
- `ProgramRule`, `Exists`, `ExistsNative`, `Raw`, `raw`, `RawCombinedOutput`, and `RawCombinedOutputNative` implement idempotent command execution.
- `FlushChain`, `SetDefaultPolicy`, `HasPolicy`, `AddReturnRule`, `EnsureJumpRule`, and `DeleteJumpRule` manage common chain state.
- `Rule` wraps a rule with idempotent `Append`, `Insert`, `Delete`, `Exists`, `WithChain`, and `String`.

## Control Flow
Initialization is lazy through `initOnce`, detecting firewalld and iptables binaries. `Raw` prefers firewalld passthrough when running, falling back to native iptables for missing D-Bus service-file errors. Native execution prepends `--wait`, optionally wraps the command with `nsenter` into a detached rootless namespace, runs combined output, filters xtables-lock warnings, and logs slow operations.

## State And Persistence
Global binary paths and firewalld state are cached. The main effects are kernel iptables/nftables rule mutations. `Rule` values are immutable-ish wrappers around command arguments.

## Dependencies And Integration Points
Uses `os/exec`, rootless namespace helpers, firewalld functions, and containerd logging. It is a central integration point for bridge networking, port publishing, forwarding, NAT, and cleanup paths.

## Risks
Host binary availability, permissions, firewalld state, namespace selection, and xtables contention all affect behavior. Some remove paths intentionally ignore errors for cleanup idempotency. `Exists` cannot report initialization errors and returns false. `EnsureJumpRule` deletes then inserts, which may briefly remove a jump.

## Test Signals
`iptables_test.go` tests chain creation, link rule pairs, PREROUTING/OUTPUT rules, concurrent programming with `--wait`, cleanup, raw exists checks, `Rule` idempotency, and flushing. Tests require Linux iptables and sometimes isolate with test network namespaces.
