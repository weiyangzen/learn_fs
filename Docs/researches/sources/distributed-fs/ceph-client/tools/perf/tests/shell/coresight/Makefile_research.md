<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/Makefile

## Purpose

This Makefile orchestrates building, installing, and cleaning CoreSight shell-test workload subdirectories.

## Research

It includes shared kernel tool make fragments, defines `SUBDIRS` as `asm_pure_loop`, `memcpy_thread`, `thread_loop`, and `unroll_loop_thread`, and delegates `all`, `install-tests`, and `clean` to each subdirectory. `INSTALLDIRS` and `CLEANDIRS` are generated from `SUBDIRS`; clean uses `QUIET_CLEAN`. State is build artifacts in child directories and installed test binaries under perf's install tree. Dependencies are the parent tools make infrastructure, architecture detection, and each child Makefile's `CORESIGHT`/`ARCH` gates. Integration ensures CoreSight workload binaries are available for shell wrappers. Risks include silent child build output hiding details, failure when shared make includes move, and no build on non-arm64/non-CoreSight configurations. Test signal is successful delegation to all child targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/Makefile -->
