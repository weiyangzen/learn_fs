# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/test-symmetric-id-float.sh

## Purpose
This thin OVPN selftest wrapper runs the symmetric peer-id plus floating transport variant. It exists so kselftest can expose the mode as a separate `TEST_PROGS` entry while sharing the common implementation.

## Important APIs and data
The only behavior is setting `OVPN_SYMMETRIC_ID="1"` and `OVPN_FLOAT="1"` before sourcing `test.sh`. The script then executes `source test.sh` or `source test-close-socket.sh`, so all functions, traps, and KTAP reporting come from the sourced file.

## Control flow
Bash evaluates the variable assignment, sources the target test script in the same shell, and the sourced script immediately runs its staged test plan. There are no local functions or local cleanup handlers in this wrapper.

## State and persistence
State is inherited from the sourced test. The assignment changes environment-visible shell variables that affect peer setup, key algorithm choice, MTU, transport mode, or fixture selection.

## Dependencies and integration points
It depends on the target sourced script, `common.sh`, `ovpn-cli`, fixture files, and the same root/networking requirements as the base test. It selects symmetric peer IDs, runs float checks, and compares against `*-symm-float.json` fixtures.

## Risks and edge cases
Because the script uses `source`, any syntax error or early exit in the target script terminates this wrapper. The variable must be set before sourcing; moving it afterward would silently run the default scenario.

## Test signals
The test signals are exactly those of the sourced base script: KTAP plan/pass/fail lines, command wrapper failures, traffic checks, key/peer lifecycle checks, and notification fixture diffs.
