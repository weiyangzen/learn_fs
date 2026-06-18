
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/find_vma.c

## Purpose

`find_vma.c` verifies the `bpf_find_vma()` helper from both perf-event and kprobe contexts and checks verifier rejection for illegal writes through returned VMA/task pointers.

## Important APIs, Types, and Functions

The file uses `find_vma.skel.h`, `find_vma_fail1.skel.h`, and `find_vma_fail2.skel.h`. Core functions are `open_pe()`, `find_vma_pe_condition()`, `test_find_vma_pe()`, `test_find_vma_kprobe()`, `test_illegal_write_vma()`, and `test_illegal_write_task()`. It uses `perf_event_open`, `bpf_program__attach_perf_event()`, skeleton attach, and BSS/data fields such as `found_vm_exec`, `find_addr_ret`, `find_zero_ret`, and `d_iname`.

## Control Flow and Data Flow

`serial_test_find_vma()` loads the valid skeleton, conditionally runs perf-event coverage when hardware CPU-cycle events work, always runs the kprobe path, then loads two expected-fail skeletons. Each positive path triggers a BPF program and calls `test_and_reset_skel()` to assert successful VMA lookup for the test binary and expected failure or success for zero address.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is BSS/data counters in the skeleton and transient perf links. Dependencies include perf hardware events, kprobes, process VMAs, `/proc` executable naming, and the verifier's pointer write protections. Integration points are helper semantics and verifier enforcement around VMA/task pointers. Risks include unsupported PMU events, naming assumptions around `test_progs`, and kernel changes in zero-address lookup behavior. Test signals are positive VMA discovery, reset BSS state between triggers, and load rejection for both illegal write variants.
