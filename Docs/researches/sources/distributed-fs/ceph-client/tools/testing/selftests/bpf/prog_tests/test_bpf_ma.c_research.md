# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_bpf_ma.c

Purpose: `test_bpf_ma.c` validates BPF memory allocator behavior in generated BPF programs, including batch allocation/free and freeing through map destruction for regular and per-CPU allocations. It prepares BTF type ids for allocator data shapes before loading each selected BPF program.

Important APIs/types/functions: `do_bpf_ma_test()` opens `test_bpf_ma.skel.h`, obtains object BTF with `bpf_object__btf()`, finds struct ids named `bin_data_<size>` and `percpu_bin_data_<size>` for sizes listed in skeleton rodata arrays, writes those ids back into rodata arrays, selects one BPF program by name with `bpf_object__find_program_by_name()`, enables autoload only for that program, loads and attaches the skeleton, sets `skel->bss->pid` to the current process, sleeps briefly, and checks `skel->bss->err`. `test_test_bpf_ma()` runs four subtests.

Control flow: each subtest opens a fresh skeleton so rodata and autoload choices are isolated. The BTF lookup loops must complete before load because rodata carries the type ids the BPF program will use. After attach, setting the PID gates BPF-side work to the current process; `usleep(1)` gives the attached program a chance to run; then `err` is asserted as zero and the skeleton is destroyed.

State and persistence: state is in the opened BPF object, rodata type-id arrays, autoload flags, attached BPF program, and BSS `pid`/`err`. There is no filesystem state. Any kernel allocator objects are created and freed by the BPF-side test logic and should be released by map/free paths or skeleton teardown.

Dependencies: depends on generated `test_bpf_ma.skel.h`, libbpf BTF APIs, BTF names emitted by the BPF object, allocator helper support in the kernel, and whatever attach points the selected skeleton programs use.

Integration points: the userspace file supplies dynamic BTF ids and subtest selection for BPF allocator programs compiled elsewhere. It is an integration harness between libbpf skeleton loading, BTF metadata, and allocator runtime behavior.

Risks: BTF name construction must match BPF-side struct naming exactly. `usleep(1)` is a minimal wait and assumes the attached program runs promptly after `pid` is set. Only one program is autoloaded per skeleton instance, so missing or renamed program names lead to early failure. The test reports only aggregate `err` from BSS, so deeper allocator failure details must be encoded by the BPF program.

Test signals: each subtest passes when all expected BTF struct ids are found, the named program exists, load and attach succeed, and `skel->bss->err` remains zero after triggering the current-PID path.
