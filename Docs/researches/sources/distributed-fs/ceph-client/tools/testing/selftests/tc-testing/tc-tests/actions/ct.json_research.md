# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/ct.json

## Purpose
Defines 22 tests for the tc connection-tracking action, covering parser features, NAT/mark/label options, attachment restrictions, and one packet-driven conntrack/NAT conflict scenario.

## Important APIs, Types, And Functions
Cases cover simple `ct`, cookies, `clear`, zones, `commit`, marks and masks, IPv4/IPv6 NAT addresses and ranges, `force`, labels and label masks, `no_percpu`, DNAT tuple conflict, and attaching `act_ct` to ETS qdisc, ingress, clsact egress, and shared blocks. Verification uses both regex output and `matchJSON` for filter/action binding.

## Control Flow
Most cases run `tc actions add action ct ...` and verify textual state. The DNAT case configures an ingress flower rule with `ct commit nat dst`, sends two TCP packets with scapy, and verifies `/proc/net/nf_conntrack` contains the expected original destination. Attachment cases set up qdisc/block context, run `tc filter add ... action ct`, and verify JSON output or expected failure.

## State And Persistence
State includes per-namespace tc action/filter/qdisc state and conntrack table entries. Teardown must clear qdiscs/actions and namespace state.

## Dependencies And Integration Points
Depends on `NET_ACT_CT`, conntrack, NAT, flower/matchall classifiers, ingress/clsact/shared block support, `nsPlugin`, and for one case `scapyPlugin`.

## Risks
Conntrack table contents can be affected by prior packets if namespace isolation fails. NAT and label output formatting is iproute2-sensitive. JSON match expectations depend on tc's nested schema. Attachment restrictions may change as kernel qdisc/action compatibility evolves.

## Test Signals
Pass signals are correct ct option rendering, successful NAT/mark/label parser behavior, expected failure attaching to ETS, successful binding on ingress/egress/shared block with ref/bind counts, and conntrack entry evidence after scapy traffic.
