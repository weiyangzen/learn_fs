# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_cpp.cpp

## Research

This C++ smoke test verifies that libbpf public headers, BTF APIs, generated skeletons, and selected C APIs are usable from C++ translation units. It includes `<bpf/libbpf.h>`, `<bpf/bpf.h>`, `<bpf/btf.h>`, Linux UAPI headers, and generated skeleton headers `test_core_extern.skel.h` and `struct_ops_module.skel.h`.

The key local abstraction is `template <typename T> class Skeleton`, an RAII wrapper around generated skeleton types. It stores a `T *`, destroys it in the destructor with `T::destroy()`, and exposes `open()`, `load()`, `attach()`, `detach()`, `operator->()`, and `get()`. `try_skeleton_template()` opens `test_core_extern`, edits data variables, loads and attaches it, checks a kconfig field, validates the program name `handle_sys_enter`, manually replaces a link, and detaches.

`main()` then exercises representative libbpf entry points: `libbpf_set_print()`, `bpf_prog_get_fd_by_id()`, `btf__new()`, `btf_dump__new()`, generated `open_and_load()`/`destroy()` helpers for two skeletons, and `bpf_enable_stats(BPF_STATS_RUN_TIME)`. State is limited to skeleton object lifetimes, a BTF object pointer, link replacement, and an optional stats FD closed on success. The program prints failures for smoke-test diagnostics and `DONE!` at the end.

Dependencies include C++ compilation, generated skeleton headers, kernel BPF support, and libbpf symbols with C++-safe declarations. Risks are mostly compile/link regressions, null skeleton handling after failed loads, and runtime privilege/configuration differences for stats or attach operations. Test signals are successful compilation and execution without crashes, expected stderr messages for unavailable kernel features, and the final `DONE!`.
