# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/utils.c

Purpose: common userspace utility implementation for powerpc selftests, covering file I/O, auxv/HWCAP support, CPU affinity, debugfs/sysfs helpers, perf counters, MMU detection, and signal-handler stacking.

Important APIs/types/functions: key functions include `read_file()`, `read_file_alloc()`, `write_file()`, `read_auxv()`, `get_auxv_entry()`, `read_debugfs_int()`, `write_debugfs_int()`, `read_sysfs_file()`, `pick_online_cpu()`, `bind_to_cpu()`, `is_ppc64le()`, `perf_event_open_counter()`, `perf_event_enable/disable/reset()`, `using_hash_mmu()`, `push_signal_handler()`, and `pop_signal_handler()`.

Control flow: file helpers open/read/write with negative errno returns and parse helpers validate complete numeric input. CPU helpers inspect current affinity and prefer primary SMT threads. Perf helpers configure disabled group-capable counters excluding kernel/hypervisor/guest. Signal helpers install SA_SIGINFO handlers and return previous dispositions.

State and persistence behavior: static `auxv[4096]` caches raw auxiliary-vector reads only per call path; debugfs/sysfs write helpers can mutate kernel runtime state for callers. Affinity helpers can change process CPU mask.

Dependencies and integration points: used throughout powerpc selftests and depends on Linux UAPI, `utils.h`, and `FAIL_IF` style macros for some helper paths.

Risks and test signals: `read_file_alloc()` does not NUL-terminate buffers by itself, so callers parsing strings need care. Utility functions generally return negative errno, while some test-facing helpers call harness failure macros directly.
