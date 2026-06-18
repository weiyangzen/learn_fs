# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verifier_log.c

## Purpose

Detailed verifier and BTF log buffer regression test. It checks fixed and rolling log modes, `log_true_size`, exact-size and too-short buffers, NULL log-size queries, load success/failure handling, and accidental writes past user-provided log buffers. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_prog_load()`, `bpf_btf_load()`, `bpf_prog_load_opts`, `bpf_btf_load_opts`, `BPF_LOG_FIXED`, `btf__new_empty()`, `btf__add_int()`, `btf__raw_data()`, skeleton instruction accessors, and `ASSERT_STRNEQ`/`ASSERT_STREQ` checks over guarded buffers.

## Control Flow

`verif_log_subtest()` selects a good or bad skeleton program, captures a full reference log, then iterates every shorter buffer size in rolling and fixed modes to verify truncation contents and untouched tail bytes. It then validates `log_true_size` for real and NULL buffers and boundary cases. `verif_btf_log_subtest()` builds good or intentionally invalid BTF and repeats the same log-size/truncation logic. `test_verifier_log()` runs good/bad program and BTF subtests.

## State and Persistence Behavior

Global `logs` contains filler, active buffer, and reference buffer arranged to catch overrun/corruption. Global `insns`, `insn_cnt`, `btf_data`, and `btf_data_sz` point at the currently tested program/BTF. No state survives test exit.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It also depends on libbpf BTF construction APIs and kernel support for rolling verifier logs and `log_true_size`.

## Risks and Edge Cases

The test is sensitive to verifier log text length and mode semantics; kernel changes to emitted stats/log ordering can change expected sizes. It deliberately mutates a BTF type size through an internal pointer, so libbpf representation changes can affect the bad-BTF path.

## Test Signals

Important signals are `-ENOSPC` for too-short logs, exact prefix/suffix content for fixed/rolling modes, unchanged filler tails, equal fixed/rolling true sizes, valid NULL-buffer size queries, and expected good/bad load outcomes.
