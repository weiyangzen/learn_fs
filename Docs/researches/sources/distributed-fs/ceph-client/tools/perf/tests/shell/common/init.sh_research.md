<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/init.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/init.sh

## Purpose

This shared shell initializer provides result reporting, environment detection, runmode skipping, kprobe/uprobe cleanup helpers, and SDT support checks for the perf shell testsuite.

## Research

It sources `settings.sh` and `patterns.sh`, derives `THIS_TEST_NAME`, and defines `_echo`, `print_results`, `print_overall_results`, skip/warn printers, and `consider_skipping`. Detection helpers include `detect_baremetal`, `detect_intel`, and `detect_amd`. Probe helpers check debugfs tracing files, clear all kprobes/uprobes by disabling tracing and emptying probe event files, and test SDT presence with `perf list sdt`. State is primarily exported variables from sourced settings plus mutations to `/sys/kernel/debug/tracing` when clearing probes. Dependencies include systemd-detect-virt, `/proc/cpuinfo`, debugfs tracing, and the configured `CMD_PERF`. Integration is central for base_probe and base_report scripts. Risks include destructive probe cleanup, sourcing path assumptions based on `$0`, and result functions treating any nonzero check as failure even for expected skip unless caller handles it. Test signal is standardized PASS/FAIL/SKIP output and exit status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/init.sh -->
