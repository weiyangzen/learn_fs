<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/fw.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/fw.json

## Purpose
This fixture defines 62 tests for the `fw` classifier, which classifies packets by firewall mark. It validates parser boundaries, action attachment by value and by reference, cookies, handle/mask parsing, parent and protocol requirements, classid/flowid behavior, action reference counts, police actions, deletion selectors, replacement, and class reference behavior after replacement.

## Important APIs, Types, And Functions
The TDC schema drives `tc filter add|del|replace|get|show dev $DEV1 ... fw` plus related `tc action` and `tc class` setup in some cases. The file requires `nsPlugin`. The tested syntax includes `parent ffff:` or `parent 10:`, `handle VALUE[/MASK]`, `prio`, `protocol all|ip|ipv6|arp|802_3`, `fw`, `classid`, `flowid`, and actions `ok`, `continue`, `pipe`, `drop`, `reclassify`, `jump 10`, `goto chain 5`, `gact index N`, `cookie`, and `police rate ... burst ... linklayer atm`.

## Control Flow
Most tests set up ingress and sometimes pre-create referenced gact actions, add a fw filter, verify with `tc filter get` or `show`, then delete ingress. Negative add tests assert nonzero exits and zero matches for invalid prio, invalid action, missing action, invalid handles/masks, missing parent, invalid classid, invalid protocol, and priority/protocol conflicts. Delete tests seed multiple filters, then delete by whole parent, single handle/prio/action forms, prio, chain, or invalid selectors. Replace tests seed a filter and replace action, classid, or action index. One case attempts to delete a class referenced by fw after replacement and expects the class to remain visible.

## State And Persistence Behavior
Fw filter state is keyed by parent, priority, protocol, handle, optional mask, and chain. Handles and masks are normalized to hexadecimal, with 32-bit maximum accepted and larger values rejected. Priority `65535` is accepted while `65536` is rejected. `classid` and `flowid` map to printed classid state, with later duplicate classid/flowid-style arguments taking precedence. Referenced gact actions show increased `ref` and `bind` counts. Police actions persist rate, burst, mtu, action, overhead, linklayer, index, ref, and bind output. Replacement changes existing filter state, and class deletion is prevented while the fw filter still references the class.

## Dependencies And Integration Points
The fixture depends on ingress qdisc support, fw classifier support, gact and police action modules, class/qdisc setup for class reference tests, and iproute2 parser/printer behavior. It integrates with shared tc action reference accounting, class binding semantics, protocol parsing, chain deletion, and parent selector handling. It also exercises action lookup by pre-created `gact index 1` references.

## Risks
The file is broad and output-sensitive. It assumes exact printed forms for `ok` as `gact action pass`, root classid as `root`, large classid truncation to the last 8 hex digits, and police rate formatting such as `1Kbit` and `10Kb`. Several invalid delete forms expect exit `2` while leaving state intact. The typo in names saying `maxixum` is harmless but signals old fixture text. Any changes in ref/bind accounting, class deletion policy, or protocol conflict handling can affect multiple cases.

## Test Signals
Signals include accepted and rejected priority bounds, all common gact actions by value and by reference, cookies and invalid cookies, hex and decimal handle/mask parsing, mandatory parent/handle/action enforcement, classid and flowid precedence, protocol variants and invalid protocol, duplicate priority/protocol rejection, shared action index accounting, police action variants, full and selective deletes, invalid deletes that preserve state, replacement of action/classid/index, class reference protection, and replacement with nil classid. Passing results indicate robust fw classifier parsing and lifecycle behavior across many tc subsystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/fw.json -->
