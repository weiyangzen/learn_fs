<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/drm_pmu.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/drm_pmu.sh

## Purpose

This shell test validates that raw DRM PMU events listed by perf can be used with `perf stat` against the current process.

## Research

The script opens every character device under `/dev/dri` with major 226, stores fds in an associative array, and prints each `/proc/$$/fdinfo/$fd` so DRM statistics exist for the process. If no DRM devices are found it skips. It iterates `perf list --raw-dump drm-`, runs `perf stat -e "$p" --pid=$$ true`, and checks the event name appears in output. It closes all opened fds at the end. State includes live device file descriptors and one temporary output file. Dependencies are DRM devices, readable device nodes, fdinfo statistics, perf DRM PMU support, and Bash associative arrays. Risks include permission failures opening render/card nodes, empty raw-dump output, event names that require active GPU work, and leaking fds if interrupted before cleanup. Passing signal is every listed DRM event visible in perf stat output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/drm_pmu.sh -->
