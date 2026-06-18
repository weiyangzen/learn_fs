# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/sleepable.c

## Purpose

This verifier fixture validates which BPF program/attach types may use `BPF_F_SLEEPABLE`. It accepts sleepable fentry, fexit-style tracing metadata, fmod_ret, iterator, LSM, and uprobe cases, and rejects an unsupported raw tracepoint sleepable program with an exact verifier diagnostic.

## Important APIs, Types, and Functions

Each case is a minimal two-instruction program (`r0 = 0`, `exit`) with metadata fields including `.prog_type`, `.expected_attach_type`, `.kfunc`, `.flags = BPF_F_SLEEPABLE`, `.runs = -1`, `.result`, and optional `.errstr`. Covered attach/program signals include `BPF_PROG_TYPE_TRACING`, `BPF_TRACE_FENTRY`, `BPF_MODIFY_RETURN`, `BPF_TRACE_ITER`, `BPF_PROG_TYPE_LSM`, `BPF_LSM_MAC`, and `BPF_PROG_TYPE_KPROBE`.

## Control Flow

The harness loads each minimal program with a sleepable flag and target symbol/attach type. The verifier performs compatibility checks before runtime execution; most cases accept without being run, while the raw tracepoint case must fail before execution.

## State and Persistence Behavior

There is no file-owned state. The only meaningful state is verifier load context: program type, expected attach type, kernel function/target name, and sleepable flag.

## Dependencies and Integration Points

The fixture depends on tracing/LSM/iterator/uprobe verifier attach rules and on kfunc/test symbol availability such as `bpf_fentry_test1` and `task`. It integrates with BPF verifier regression coverage for sleepable-program policy.

## Risks and Test Signals

Risks include attach-type rule drift, renamed test symbols, and error-string brittleness when verifier diagnostics change. Signals are accept results for supported sleepable classes and rejection with the expected unsupported raw-tracepoint message.
