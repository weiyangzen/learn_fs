# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/scale.c

## Purpose

This small verifier fixture registers two scale tests that exercise large generated BPF programs through the shared `bpf_fill_scale` helper. It validates that the verifier accepts stress-sized scheduler-classifier programs and returns the expected values.

## Important APIs, Types, and Functions

The entries are table data with empty `.insns` and `.data`, `.fill_helper = bpf_fill_scale`, `.prog_type = BPF_PROG_TYPE_SCHED_CLS`, `.result = ACCEPT`, and distinct `.retval` values of `1` and `2`. The important API is the harness fill-helper contract: instead of listing instructions inline, the harness calls `bpf_fill_scale` to synthesize the program body.

## Control Flow

The verifier harness discovers each entry, invokes `bpf_fill_scale`, loads the generated classifier program, and checks the result and return value. The source file itself has no local loops or branches; all execution shape is delegated to the fill helper.

## State and Persistence Behavior

No state persists across tests. Generated instruction buffers, verifier states, and return-value checks are harness-owned and per-test.

## Dependencies and Integration Points

The file depends on the BPF verifier selftest data format, `bpf_fill_scale`, scheduler-classifier program loading, and the harness return-value runner. It integrates with verifier scalability coverage, especially instruction/state growth limits.

## Risks and Test Signals

Risks are primarily indirect: if `bpf_fill_scale` changes, these tests change behavior without local edits; if the verifier limit logic changes, failures may be broad. Test signals are successful loads, expected return values, and runtime that stays within verifier complexity limits.
