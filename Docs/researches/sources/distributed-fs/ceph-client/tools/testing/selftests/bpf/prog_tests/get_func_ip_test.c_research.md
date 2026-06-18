
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_func_ip_test.c

## Purpose

`get_func_ip_test.c` validates `bpf_get_func_ip()` for function entry, function body offsets, uprobes, kprobes, and fprobe sessions.

## Important APIs, Types, and Functions

The file uses `get_func_ip_test.skel.h`, `get_func_ip_uprobe_test.skel.h`, and `get_func_ip_fsession_test.skel.h`. It attaches skeleton probes, manually attaches an x86_64 kprobe with `bpf_kprobe_opts.offset`, defines an assembly `uprobe_trigger_body`, and runs trigger programs with `bpf_prog_test_run_opts()`.

## Control Flow and Data Flow

Entry tests load/attach the skeleton, store the address of a local noinline trigger, run BPF trigger programs, call the local uprobe trigger, and assert result flags. On x86_64, body tests enable a disabled program, choose an offset adjusted for IBT, attach a kprobe to `bpf_fentry_test6`, run trigger code, then run the uprobe-body skeleton and call the assembly function. The fsession test checks entry and exit results.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is BSS fields holding trigger addresses and result flags. Dependencies include fentry, fexit, kprobe, uprobe, fprobe sessions, x86_64-specific body tests, and kconfig `CONFIG_X86_KERNEL_IBT`. Integration is IP reporting across probe types and offsets. Risks are instruction offset drift, compiler treatment of noinline triggers, and architecture skips. Test signals are all expected result fields equal to one and clean attach/run across entry, body, and session paths.
