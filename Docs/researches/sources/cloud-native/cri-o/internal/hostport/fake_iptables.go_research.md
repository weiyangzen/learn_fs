# sources/cloud-native/cri-o/internal/hostport/fake_iptables.go

## Purpose
Implements an in-memory `internal/iptables.Interface` used by hostport tests to simulate iptables chain/rule operations, save/restore output, protocol selection, and builtin-chain behavior.

## Important APIs, Types, And Functions
- `fakeIPTables`, `fakeTable`, and `fakeChain` model tables, chains, and rule lists.
- `newFakeIPTables`, `EnsureChain`, `FlushChain`, `DeleteChain`, `ChainExists`, `EnsureRule`, `DeleteRule`, `SaveInto`, `Restore`, `RestoreAll`, `Protocol`, `IsIPv6`, `Present`, and `HasRandomFully` satisfy the iptables interface.
- Helpers `normalizeRule`, `findRule`, `saveChain`, `restore`, and `isBuiltinChain` implement test semantics close to real iptables.

## Control Flow
Chain and rule operations lazily create missing chains as needed. Rules are normalized before insertion to mimic iptables behavior for `--to-destination`, quoted comments, and IP CIDR suffixes. `SaveInto` writes iptables-save style table, chain, and `-A` rule lines. `restore` parses iptables-restore data table-by-table, creates chain lines, appends or prepends rules, deletes chains, flushes non-builtin user chains unless they are being deleted, and honors table filtering.

## State And Persistence
All state lives in maps and slices inside `fakeIPTables`. There is no disk persistence. Restore operations mutate the in-memory tables in a way tests can later inspect through `SaveInto` or direct map access.

## Dependencies And Integration Points
Implements CRI-O's vendored Kubernetes iptables abstraction for hostport unit tests. Uses Kubernetes set utilities and IP family helpers for normalization.

## Risks And Edge Cases
The fake is not a complete iptables parser. It splits restore lines simplistically, supports only the operations needed by tests, and normalizes comments/IP addresses in ways tailored to assertions. Divergence from real iptables can hide production bugs or create false failures when command formatting changes.

## Test Signals
`fake_iptables_test.go`, `hostport_iptables_test.go`, and `meta_hostport_manager_test.go` exercise save/restore, chain cleanup, IPv4/IPv6 rule generation, and legacy cleanup behavior through this fake.
