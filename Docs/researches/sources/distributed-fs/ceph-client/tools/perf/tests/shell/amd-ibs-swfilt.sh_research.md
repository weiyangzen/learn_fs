<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/amd-ibs-swfilt.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/amd-ibs-swfilt.sh

## Purpose

This shell test validates AMD IBS PMU software filtering (`swfilt`) behavior for user/kernel exclude modifiers and sample classification.

## Research

`ParanoidAndNotRoot` combines uid and `/proc/sys/kernel/perf_event_paranoid` checks. The script skips if `/sys/bus/event_source/devices/ibs_op` or its `format/swfilt` file is absent. It expects `ibs_op//u` with a modifier but no swfilt to fail, then verifies `ibs_op/swfilt/u`, `ibs_op/swfilt=1/k`, `ibs_fetch/swfilt/u`, and system-wide `ibs_op/swfilt/k` where permissions allow. It pipes recording output to `perf script -F misc` and counts unexpected kernel or user samples. State is kernel PMU/sysfs and perf output streams only. Dependencies are AMD IBS hardware, perf paranoid policy, root privileges for some paths, and sample misc classification. Risks include skip-heavy behavior on non-AMD systems, zero samples reducing confidence, and permission-dependent partial skips. Test signals are correct reject/accept behavior and zero excluded-domain samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/amd-ibs-swfilt.sh -->
