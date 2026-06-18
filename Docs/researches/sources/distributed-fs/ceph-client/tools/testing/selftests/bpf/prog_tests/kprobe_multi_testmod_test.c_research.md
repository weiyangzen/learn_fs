
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kprobe_multi_testmod_test.c

## Purpose

`kprobe_multi_testmod_test.c` validates kprobe-multi attachment to symbols exported by `bpf_testmod`, using both symbol names and module-local addresses.

## Important APIs, Types, and Functions

The harness reuses `kprobe_multi.skel.h`, `trace_helpers.h`, local kallsyms via `load_kallsyms_local()`, `ksym_get_addr_local()`, `bpf_program__attach_kprobe_multi_opts()`, and `trigger_module_test_read()`.

## Control Flow and Data Flow

The serial test loads local kallsyms, runs symbol and address subtests. Each subtest opens the skeleton, sets current PID, attaches entry probes to three `bpf_testmod_fentry_test*` functions, flips `retprobe`, attaches return probes, triggers module read, and checks six BSS result flags.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is local kallsyms cache and kprobe links. Dependencies include loaded/available `bpf_testmod`, module kallsyms visibility, and kprobe-multi support for module symbols. Integration is module symbol resolution by name and address. Risks are missing test module, symbol renames, and return-probe option mutation. Test signals are all three entry and all three return result fields equal to one.
