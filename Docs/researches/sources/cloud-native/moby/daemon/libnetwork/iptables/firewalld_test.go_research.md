# sources/cloud-native/moby/daemon/libnetwork/iptables/firewalld_test.go

## Purpose
Integration-tests firewalld-backed iptables behavior on Linux hosts where firewalld is available.

## Important APIs, Types, And Functions
- `skipIfNoFirewalld` detects D-Bus/firewalld availability.
- `TestFirewalldInit` checks initialization.
- `TestReloaded` verifies registered reload callbacks restore rules after flush/removal.
- `TestPassthrough` adds and deletes an INPUT rule through firewalld passthrough.

## Control Flow
Tests skip when system D-Bus or firewalld is absent. Reload test creates a forwarding chain and jump, adds link rules, registers `OnReloaded`, removes rules, calls `reloaded`, and checks rules are recreated.

## State And Persistence
Mutates host/test namespace iptables and firewalld runtime state. Cleanup removes chains/rules where possible.

## Dependencies And Integration Points
Uses D-Bus, `GetIptable`, `ChainInfo.Link`, and package reload machinery. These are closer to integration tests than pure unit tests.

## Risks
Host environment controls whether tests run. Firewalld in a different namespace can make rule visibility tricky. Cleanup failures could leave test rules on development machines.

## Test Signals
Confirms the D-Bus passthrough path can program real rules and that reload callbacks are sufficient to rebuild Docker rules after firewalld reload.
