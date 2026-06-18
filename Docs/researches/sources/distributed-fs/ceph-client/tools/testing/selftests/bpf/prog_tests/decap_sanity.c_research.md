# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/decap_sanity.c

## Purpose
Runs a namespace-level decapsulation sanity test for the generated `decap_sanity` BPF program, using IPv6 loopback and a fixed UDP test port.

## Important APIs, types, and functions
Uses `decap_sanity.skel.h`, network helpers, `ip netns` setup, socket APIs, and BPF program attach/test-run paths inside the generated skeleton.

## Control flow and state
The test creates a named netns, configures IPv6 loopback address `face::1`, loads/attaches the skeleton, sends or tests UDP traffic to port 7777 as defined by the BPF object, validates BSS status, and deletes the namespace. Runtime state is namespace config, sockets, and skeleton state.

## Dependencies and integration points
Depends on `ip` tooling, namespace privileges, IPv6 loopback support, and generated decapsulation BPF program. Integrated as `test_decap_sanity()`.

## Risks and test signals
Environmental namespace setup is the main risk. Signals are successful skeleton load/attach, UDP trigger completion, and BPF status/counters showing expected decapsulation behavior.
