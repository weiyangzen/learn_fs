<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_cpucores.c -->
# sources/compression/xz/src/common/tuklib_cpucores.c

Purpose: detects the number of online CPU cores/threads.

Important APIs/types/functions: `tuklib_cpucores(void)` with platform paths for Windows `GetSystemInfo`, Linux `sched_getaffinity`, FreeBSD `cpuset_getaffinity`, BSD `sysctl`, POSIX `sysconf`, and HP-UX `pstat_getdynamic`.

Control flow: initialize return to zero, execute the first compile-time selected method, validate positive counts, and return zero if unknown.

State and persistence: no state beyond local variables.

Dependencies and integration: selected by `TUKLIB_CPUCORES_*` macros from configure; used by threaded compression defaults and hardware reporting.

Risks: CPU affinity APIs can report a constrained set rather than physical cores, which is usually desired. Fixed `cpu_set_t` may undercount on systems with very large CPU sets.

Test signals: compare to OS tools under normal and affinity-restricted execution; test unknown-method fallback returns zero.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_cpucores.c -->
