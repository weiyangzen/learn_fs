
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_stackid_cannot_attach.c

## Purpose

`get_stackid_cannot_attach.c` checks that a perf-event BPF program using stack/build-id collection can attach only to perf events with compatible callchain sampling.

## Important APIs, Types, and Functions

The test uses `test_stacktrace_build_id.skel.h`, overrides program type to `BPF_PROG_TYPE_PERF_EVENT`, opens hardware CPU-cycle perf events with branch-stack sampling, and attaches with `bpf_program__attach_perf_event()`.

## Control Flow and Data Flow

It loads the skeleton, opens a precise CPU-cycle event without `PERF_SAMPLE_CALLCHAIN`, and expects attach failure. It then adds `PERF_SAMPLE_CALLCHAIN` and expects attach success. Finally it sets `exclude_callchain_kernel` and expects attach failure again.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is perf event FDs and a perf-event link. Dependencies include hardware PMU support for precise CPU cycles, branch stacks, and callchains; unsupported PMUs are skipped. Integration is kernel validation between perf event sample type and BPF stack helper needs. Risks are PMU permission/support differences and exact attach error behavior. Test signals are fail/succeed/fail attach sequence for no-callchain, callchain, and kernel-callchain-excluded configurations.
