# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/attach_probe.c

Purpose: comprehensive userspace attach API test for kprobes, kretprobes, uprobes, uretprobes, auto-attach, sleepable probe restrictions, duplicate symbols, long event names, reference counters, library symbol uprobes, and kprobe context write restrictions.

Important APIs/types/functions: uses skeletons `test_attach_probe_manual`, `test_attach_probe`, `test_attach_kprobe_sleepable`, and `kprobe_write_ctx`. Local trigger functions provide uprobe targets; `uprobe_ref_ctr` emulates a USDT semaphore. Important helpers include `test_attach_probe_manual`, `test_attach_kprobe_by_addr`, `test_attach_kprobe_legacy_by_addr_reject`, `test_attach_probe_dup_sym`, long-name tests, `test_attach_probe_auto`, `test_uprobe_lib`, `test_uprobe_ref_ctr`, `test_kprobe_sleepable`, `test_uprobe_sleepable`, and x86-only kprobe write/freplace tests.

Control flow: top-level loads the auto-attach skeleton then runs named subtests. Manual mode attaches kprobe/kretprobe and uprobe/uretprobe in default/legacy/perf/link modes, triggers `usleep` and local functions, then checks BSS result counters. Address mode resolves `SYS_NANOSLEEP_KPROBE_NAME` from kallsyms and attaches by address for perf/link while rejecting legacy. Duplicate-symbol tests attach both unqualified vmlinux and module-qualified names. Auto and sleepable tests exercise `bpf_program__attach` behavior. Library/ref-counter tests attach by symbol or offset and validate trigger counters/ref counter cleanup.

State and persistence behavior: BPF links are stored in skeleton link slots or local pointers and destroyed with skeleton cleanup. BSS result fields accumulate trigger observations. The global `uprobe_ref_ctr` should return to zero after skeleton destruction. No persistent files are created.

Dependencies and integration points: depends on libbpf probe attach APIs, kallsyms helpers, `/proc/self/exe`, `libc.so.6` resolution, testmod symbols for duplicate/long-name cases, x86-specific behavior for context write tests, and `test_progs.h`.

Risks: kernel config, architecture, module availability, and symbol names affect coverage. Some subtests verify attach success without triggering when duplicate module symbols are only attach/detach checks. Reference counter cleanup is global and checked once at the end, so earlier failed cleanup can affect later subtests.

Test signals: exact BSS counters for kprobe/uprobe results, expected `-EOPNOTSUPP` or attach failure in negative cases, successful link creation/destruction, and final `uprobe_ref_ctr == 0`.
