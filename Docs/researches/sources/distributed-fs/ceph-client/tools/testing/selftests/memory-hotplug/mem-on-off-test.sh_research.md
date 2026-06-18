# sources/distributed-fs/ceph-client/tools/testing/selftests/memory-hotplug/mem-on-off-test.sh

Purpose: exercises memory block online/offline transitions and notifier error-injection failure paths.

Important APIs/types/functions: discovers sysfs mount, scans `$SYSFS/devices/system/memory/memory*`, reads `removable` and `state`, writes `online`/`offline`, loads `memory-notifier-error-inject`, and writes debugfs action error values for `MEM_GOING_ONLINE` and `MEM_GOING_OFFLINE`.

Control flow: parses `-e`, `-p`, and `-r`; requires root, sysfs, hotpluggable memory, and removable blocks. It onlines all offline memory, attempts to offline a target percentage, onlines all again, loads error-injection module, randomly offlines blocks, verifies online failures under injected error, restores, verifies offline failures under injected error, removes the module, restores all memory online, and exits accumulated status.

State and persistence: mutates real memory block state and module/debugfs settings. It attempts restoration via `online_all_offline_memory` and clearing injected errors.

Dependencies and integration points: root, memory hotplug hardware/config, sysfs, debugfs, `memory-notifier-error-inject`, `bc`.

Risks: operating on live memory blocks is disruptive and can fail due to busy blocks. No trap means interruption can leave memory offline or module loaded.

Test signals: skip for missing prerequisites; pass/fail through `retval` and printed transition diagnostics.
