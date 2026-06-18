# sources/distributed-fs/ceph-client/tools/perf/util/bpf_counter.h

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_counter.h

Purpose: this header declares the perf BPF counter abstraction used by `evsel` code. It exposes a small lifecycle/install/read API while hiding whether the implementation is program profiling, shared bperf counters, cgroup bperf, or a no-op build without BPF skeleton support.

Important APIs and types: `struct bpf_counter_ops` holds `load`, `enable`, `disable`, `read`, `destroy`, and `install_pe` callbacks. Public functions mirror those callbacks: `bpf_counter__load()`, `bpf_counter__enable()`, `bpf_counter__disable()`, `bpf_counter__read()`, `bpf_counter__destroy()`, and `bpf_counter__install_pe()`. `bperf_trigger_reading()` and `set_max_rlimit()` are also exported for cgroup counter code.

Control flow and state: when `HAVE_BPF_SKEL` is defined, the header declares real functions implemented in `bpf_counter.c` and `bpf_counter_cgroup.c`. Otherwise, inline stubs allow the rest of perf to compile and degrade cleanly: load/enable/disable/install succeed, reads return `-EAGAIN`, and destroy is empty.

Dependencies and integration: the header forward declares `struct evsel` and `struct target`, uses `linux/err.h` for the non-BPF stub read result, and is included by perf stat/BPF utility files that should not depend on concrete skeleton types.

Risks: callers must treat `-EAGAIN` as a signal to use normal perf reading or to report unavailable BPF data. New counter backends must fill every callback or wrapper calls will dereference null function pointers once `evsel->bpf_counter_ops` is set.

Test signals: build perf with and without `HAVE_BPF_SKEL`; verify normal perf stat still works without BPF skeleton support; and compile any new backend with strict warnings to catch signature drift.
