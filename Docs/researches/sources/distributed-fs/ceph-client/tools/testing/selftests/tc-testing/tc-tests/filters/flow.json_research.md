<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/flow.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/flow.json

## Purpose
This fixture contains 28 tests for the legacy `flow` classifier. It validates map and hash key selection, arithmetic/logical map operations, divisor and baseclass output, optional ematch/action attachment, listing, change, replace, and delete behavior. The tests are mostly positive lifecycle and dump-fidelity cases.

## Important APIs, Types, And Functions
The JSON uses the normal TDC schema with `nsPlugin`. Commands use `tc filter add|change|replace|delete|get|show dev $DEV1 parent ffff: handle 1 prio 1 protocol ip flow`. Tested `flow` arguments include `map key KEY`, operations `and`, `or`, `xor`, `rshift`, and `addend`, `hash keys src`, `divisor 1024`, `baseclass 1:1`, ematch `match 'cmp(...)'`, and `action drop`. Map keys covered include `dst`, `src`, `proto`, `proto-src`, `proto-dst`, `iif`, `priority`, `mark`, `nfct`, `nfct-dst`, `nfct-src`, `nfct-proto-src`, `nfct-proto-dst`, `rt-classid`, `sk-uid`, `sk-gid`, `vlan-tag`, and `rxhash`.

## Control Flow
Each case installs an ingress qdisc, runs a flow filter command, verifies with `tc filter get` or `tc filter show`, and removes the qdisc. Add cases verify normalized output for the chosen key and operation. The multi-operation case combines hash key selection, divisor, baseclass, a `cmp` ematch, and a drop action in one filter. The list case seeds two flow filters and expects two `rxhash` map-key dump entries. Change and replace cases mutate an existing `rxhash` addend, then verify the new value. Delete removes the matching flow filter and verifies absence of the prior replace state.

## State And Persistence Behavior
The persisted state is a flow classifier instance attached to ingress. Map operations are normalized in dumps: for example `and 0xff` becomes `and 0x000000ff`, `or 0xff` becomes `or 0x000000ff`, and `rshift 0x1f` prints as decimal `31`. `addend` remains displayed as a hex addend. `baseclass` is present by default and can be explicitly set to `1:1`. Change and replace modify the existing filter state rather than requiring delete/add.

## Dependencies And Integration Points
The fixture depends on the flow classifier, ingress qdisc, tc-testing namespace setup, ematch support for the combined case, and gact action support. Some keys, especially netfilter connection tracking keys and socket UID/GID keys, depend on parser support even though the tests do not inject packets. The fixture integrates with common filter infrastructure through handle, prio, protocol, parent, and chain output.

## Risks
The flow classifier is older and less commonly used than flower, so kernel or iproute2 support may vary by configuration. Regexes are tightly coupled to textual normalization of integer operations. There are no negative parser tests in this file, so it mainly proves accepted syntax and lifecycle behavior, not rejection boundaries. The delete test verifies absence of a replaced state pattern; if delete matching semantics change, this could miss some unrelated residual state.

## Test Signals
The fixture signals parser support for all listed map keys, logical/arithmetic operations, hash-key mode, combined divisor/baseclass/ematch/action syntax, list counts, change, replace, and delete. A successful run means flow classifier state can be created, queried, updated, dumped, and removed through the standard tc filter lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/flow.json -->
