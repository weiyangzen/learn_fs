<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/bpf.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/bpf.json

## Purpose
This compact fixture contains 7 tests for the `bpf` classifier. It validates classic BPF bytecode input, eBPF object-file loading, replacement, deletion, and listing under an ingress qdisc. The goal is to catch parser, verifier, loader, dump, and lifecycle regressions around `tc filter ... bpf`.

## Important APIs, Types, And Functions
The fixture uses TDC fields with `nsPlugin` and the `tc filter` API. Commands attach filters to `$DEV1` ingress under `parent ffff:` with `handle 1`, `protocol ip`, and `prio 100`. Classic BPF cases use `bpf bytecode '4,40 0 0 12,...'`; eBPF cases use `bpf object-file $EBPFDIR/action-ebpf section action-ok` or `section action-ko`. Verification uses `tc filter get ... bpf` and regexes for bytecode strings, object section names, 16-character program tags, and optional `jited` markers.

## Control Flow
Each case installs ingress qdisc state, runs the add/replace/delete/show command, verifies the resulting classifier state, then deletes the qdisc. Positive add cases assert one persisted filter. Invalid bytecode and invalid eBPF section tests expect nonzero exits and zero matches. Replacement seeds a valid cBPF filter, replaces bytecode with a different EtherType comparison, and verifies that the new bytecode is the visible state. Delete seeds a filter, deletes by handle/prio/protocol/classifier, and verifies absence. The list test seeds multiple BPF filters and counts dump entries.

## State And Persistence Behavior
Filter state is persisted under the ingress qdisc, keyed by handle, protocol, priority, and chain. Successful cBPF bytecode is dumped back exactly enough for regex comparison. Successful eBPF object loading persists a program reference whose dump includes object and section identity plus a verifier-generated tag. Invalid cBPF opcodes and invalid eBPF sections must not leave a visible filter. Replacement overwrites filter bytecode; deletion removes it from the classifier table.

## Dependencies And Integration Points
The file depends on tc-testing, `nsPlugin`, ingress qdisc support, classic BPF validation, eBPF object loading, `$EBPFDIR/action-ebpf`, kernel BPF verifier behavior, optional JIT status, and iproute2 BPF dump formatting. It integrates with kernel classifier infrastructure through the same `parent ffff:` and priority/handle model as other filter fixtures.

## Risks
The eBPF tests depend on a compiled object existing in `$EBPFDIR` with sections named `action-ok` and `action-ko`. Kernel verifier or JIT differences can alter exit codes or dump details, though the regex allows optional `jited`. Classic bytecode strings are compared literally, so printer formatting changes can break tests. Invalid bytecode expects exit `2`, while invalid object-file section expects exit `1`; those exact values can be fragile across iproute2 and kernel versions.

## Test Signals
The strongest signals are successful cBPF add, rejection of invalid cBPF instruction class, successful eBPF object/section load with a tag, rejection of invalid eBPF section, cBPF replacement, deletion, and multi-filter listing. Passing results indicate that both cBPF and eBPF paths are accepted, persisted, dumped, and removed correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/bpf.json -->
