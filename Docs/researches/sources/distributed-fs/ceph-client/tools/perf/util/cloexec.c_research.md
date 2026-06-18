# sources/distributed-fs/ceph-client/tools/perf/util/cloexec.c

Purpose: probes whether `perf_event_open` supports `PERF_FLAG_FD_CLOEXEC` and returns the correct flag for the current kernel.

Important APIs/functions: exports `perf_event_open_cloexec_flag`; internal `perf_flag_probe` opens a safe software event with and without the flag.

Control flow: first caller triggers the probe. The probe uses current CPU, tries pid `-1`, retries pid `0` on access errors, treats a successful fd as support, and confirms fallback behavior by opening without the flag.

State and persistence: static `flag` and `probed` cache the result for the process.

Dependencies and integration: depends on perf syscall wrapper, `perf_event_attr`, scheduling helper, errno handling, warning macros, and error-string formatting.

Risks: cached result assumes kernel support will not change. Permission errors can mask support but are treated nonfatally. Unsynchronized first-call races are possible.

Test signals: old/new kernels, restrictive `perf_event_paranoid`, EACCES paths, EBUSY paths, and close-on-exec fd verification.
