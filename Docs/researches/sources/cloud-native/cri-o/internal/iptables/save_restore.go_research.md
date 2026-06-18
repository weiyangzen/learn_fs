# sources/cloud-native/cri-o/internal/iptables/save_restore.go

## Purpose
Provides a small helper for formatting iptables-save/restore chain declaration lines.

## Important APIs, Types, And Functions
- `MakeChainLine(chain Chain) string` returns `:<chain> - [0:0]`.

## Control Flow
No branching; formats the supplied chain into an iptables-save-compatible declaration.

## State And Persistence
No state is changed. The returned string is used in restore payload generation.

## Dependencies And Integration Points
Used by hostport iptables code and fake iptables tests to emit chain declarations in restore data. Depends only on `fmt` and local `Chain`.

## Risks And Edge Cases
Assumes zero counters and default policy marker `-`, which is appropriate for user-defined chains. Builtin chain policies may require different formatting in other contexts.

## Test Signals
Used by hostport tests and fake restore tests; no direct standalone test.
