
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector_load_bytes.c

## Purpose

`flow_dissector_load_bytes.c` checks helper availability/behavior for `bpf_skb_load_bytes()` in a flow dissector program run through the skb-style test-run path.

## Important APIs, Types, and Functions

The test hand-builds raw BPF instructions, loads them as `BPF_PROG_TYPE_FLOW_DISSECTOR` with `bpf_test_load_program()`, and executes with `bpf_prog_test_run_opts()`. It uses `pkt_v4`, `struct bpf_flow_keys`, and return codes `BPF_DROP`/`BPF_OK`.

## Control Flow and Data Flow

The BPF program tries to copy one byte from offset zero into stack memory. If helper execution succeeds it returns `BPF_DROP`; otherwise it returns `BPF_OK`. The host runs the program with packet input and flow-key output buffer, then asserts the program loaded, test-run succeeded, output size is the flow-key size, and retval is `BPF_OK`.

## State, Dependencies, Integration Points, Risks, and Test Signals

There is no persistent state beyond the loaded program FD. The test depends on flow dissector test-run support and helper restrictions for this program type/context. It integrates with verifier/helper availability and skb-less-vs-skb flow dissector semantics. The main risk is interpreting a helper policy change as a behavior regression; comments and expected retval encode the current contract. Test signals are successful load, successful run, preserved data-out size, and `BPF_OK` rather than helper-success `BPF_DROP`.
