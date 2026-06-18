<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/vlan.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/vlan.json

## Purpose
This fixture contains 36 `actions/vlan` TDC tests for the `tc` VLAN action. It validates the action parser and persisted action state for `pop`, `push`, and `modify`, plus replacement, deletion, flush, cookies, `no_percpu`, and batched action add/delete behavior. The cases cover valid behavior and boundary rejection for VLAN IDs, 802.1p priorities, action indices, protocols, opcodes, and goto-chain control.

## Important APIs, Types, And Functions
The JSON is consumed by the tc-testing harness and uses the standard TDC case fields: setup, command under test, expected exit code, verification command, regex match pattern, and teardown. The fixture requires `nsPlugin`. The primary command surface is `tc actions add|replace|del|flush|list|get action vlan`. Tested VLAN action forms include `vlan pop`, `vlan push id N [protocol 802.1Q|802.1AD] [priority N]`, and `vlan modify protocol ... id ... priority ...`. Control opcodes include `pipe`, `pass`, `drop`, `reclassify`, `continue`, `jump 10`, `trap`, and invalid `foo`.

## Control Flow
Most single-action tests flush all VLAN actions during setup, run an add or replace command, verify by `actions list` or `actions get action vlan index N`, and flush during teardown. Negative tests verify that invalid commands do not create matching action state. Replacement tests set up an action at the target index, replace one attribute such as ID, protocol, priority, or cookie, and verify the updated dump. Batch tests use shell loops to build 32 action specs and call `$TC actions add` or `$TC actions del` once with the accumulated arguments; verification counts index lines in the action dump.

## State And Persistence Behavior
The durable state under test is the kernel action table for VLAN actions, addressed by explicit or implicit action indices. Valid `pop` and `push` actions must persist with printed operation, control opcode, index, reference count, and optional cookie. The fixture tests maximum accepted index `4294967295` and rejection above that value. `push` defaults to protocol `802.1Q` and priority `0` when omitted. VLAN ID `4094` and priority `7` are accepted; out-of-range ID `5678` and priority `10` are rejected. Batch add/delete cases verify that multiple indexed action objects can be created and removed in a single command line.

## Dependencies And Integration Points
The file depends on the TDC harness, `nsPlugin`, iproute2 `tc` action parsing and output formatting, and the kernel VLAN action implementation. Batch cases depend on `/bin/bash`, `seq`, command substitution, and shell quoting inside `cmdUnderTest`. The fixture also relies on action dump counters and text such as `ref`, `bind`, protocol spelling, and cookie display. It integrates with shared gact-style control semantics through VLAN action opcodes and with tc action indexing infrastructure.

## Risks
Several match patterns intentionally assert printed defaults, such as protocol `802.1Q`, priority `0`, and `pipe`; these can fail if output formatting changes without semantic regression. Two `modify` cases have expected exit code `0` but `matchCount` `0`, indicating they may be documenting a parser acceptance path where the printed result does not match the optimistic pattern, or an historical expected output mismatch. Batch commands are sensitive to shell quoting and environment variables. `goto chain` rejection tests assume a specific invalid-chain policy and that the old action remains untouched.

## Test Signals
The fixture provides positive signals for every supported pop opcode, push defaults, explicit `802.1Q` and `802.1AD`, maximum VLAN ID and priority, modify mode, replacements, cookies, flush, delete, batch add/delete for push and pop, and `no_percpu`. Negative signals cover invalid opcode, invalid action mode, invalid protocol token, out-of-range ID/priority/index, and invalid goto chain replacement. Together these tests exercise both local parser validation and persistent action table lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/vlan.json -->
