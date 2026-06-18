# sources/distributed-fs/ceph-client/kernel/bpf/Makefile

Purpose: defines the BPF subsystem object composition and per-object compiler flags.

Important APIs/types/functions: always builds `core.o`; conditionally includes syscall/verifier/map/helper/iterator/BTF/JIT/network/perf/cgroup/LSM/preload objects based on Kconfig. It removes ftrace instrumentation from selected low-level allocator/list/ringbuf objects and disables GCC GCSE for `core.o` on x86 when the interpreter remains.

Control flow: object lists are appended for `CONFIG_BPF_SYSCALL`, `CONFIG_BPF_JIT`, `CONFIG_BPF_LSM`, networking, perf events, cgroups, inet, sysfs, crypto, DMA-buf, and MMU+64-bit arena support. LSM prototype object ordering deliberately precedes `bpf_lsm.o` for BTF dedup behavior.

State and persistence: affects build artifacts only, determining which BPF features are compiled into the kernel.

Dependencies and integration: integrates with top-level kbuild and the Kconfig symbols in this folder. It ties source files in this research subset into the build: `arena.o`, `arraymap.o`, `backtrack.o`, `bloom_filter.o`, `bpf_cgrp_storage.o`, `bpf_inode_storage.o`, `bpf_insn_array.o`, `bpf_iter.o`, and `bpf_local_storage.o`.

Risks: object ordering and conditional inclusion are behaviorally significant. Missing `CONFIG_MMU && CONFIG_64BIT` around arena would break unsupported architectures; incorrect LSM ordering can produce wrong BTF prototypes; accidental ftrace instrumentation in lock-sensitive BPF internals can recurse or perturb timing.

Test signals: build matrix across BPF syscall/JIT/LSM/net/perf/cgroup configs, pahole/BTF generation, and boot/runtime BPF selftests.
