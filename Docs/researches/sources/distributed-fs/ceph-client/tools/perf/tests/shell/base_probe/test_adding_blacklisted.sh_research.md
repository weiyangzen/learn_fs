<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_adding_blacklisted.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_adding_blacklisted.sh

## Purpose

This exclusive perf-probe test verifies blacklisted kernel functions cannot be added as kprobes and do not appear in `perf list`.

## Research

The script sources `common/init.sh`, reads the first blacklist functions from `/sys/kernel/debug/kprobes/blacklist`, skips if none are available, detects vmlinux used for symbols, and clears existing probes. It iterates blacklisted functions, runs `perf probe`, expects failure, and validates stderr against skip, not-found, invalid-argument, symbol-fail, out-of-section, or broken-DWARF patterns. A special path identifies MIPS assembler DWARF pollution. It then runs `perf list probe:*` and requires only empty/header/metric-group lines. State includes kernel tracing probe files and logs under `LOGS_DIR`. Dependencies are debugfs tracing, kprobe blacklist, perf probe, readelf for the MIPS check, and shared regex checkers. Risks include destructive clearing of user probes, architecture-specific DWARF noise, and blacklist content variability. Test signals are failed add attempts with whitelisted diagnostics and no listed probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_adding_blacklisted.sh -->
