<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/settings.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/settings.sh

## Purpose

This shared shell file defines perf testsuite defaults for command paths, workloads, runmodes, logging, locale, colors, directory layout, and optional parametrization.

## Research

It exports `CMD_PERF`, common sleep/true workloads, runmode constants, default runmode, verbosity, color flags, `LC_ALL=C`, terminal color escape variables, `TEST_NAME`, architecture, and run directories. When `PERFSUITE_RUN_DIR` is set, it creates per-test `CURRENT_TEST_DIR`, `MAKE_TARGET_DIR`, `LOGS_DIR`, and `HEADER_TAR_DIR`; otherwise it uses the current directory. It then sources runmode-specific and default parametrization files from `../common` when applicable. State is exported environment and created directories. Dependencies are `which perf`, `readlink`, `arch`, shell path layout, and optional parametrization files. Integration provides stable configuration for all tests sourcing `init.sh`. Risks include global locale override, default `which perf` picking the wrong binary, directory creation in shared paths, and `$0`-based path inference failing when sourced unconventionally. Test signal is consistent environment for downstream scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/settings.sh -->
