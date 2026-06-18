<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-sloppy-logic-analyzer.sh -->
# sources/distributed-fs/ceph-client/tools/gpio/gpio-sloppy-logic-analyzer.sh

Purpose: Shell helper for the kernel sloppy GPIO logic analyzer debugfs interface; configures sampling, optional CPU isolation, optional triggers, and packages captures as Sigrok `.sr` archives.

Important APIs/types/functions: Functions include `parse_si()` for SI-number parsing, `init_cpu()` for cpuset/IRQ/workqueue/task affinity isolation, `parse_triggerdat()` for trigger string encoding, `do_capture()` for capture and archive generation, and helpers `fail()`/`set_newmask()`. CLI options cover CPU, duration, instance, debugfs path, list instances, sample count/frequency, output directory, and trigger patterns.

Control flow: The script validates required commands, finds or mounts cpuset cgroups, locates `/sys/kernel/debug/gpio-sloppy-logic-analyzer/<instance>`, optionally isolates a CPU, writes delay/buffer/trigger sysfs attributes, computes an isolated CPU mask, and launches `do_capture()` in the background.

State and persistence: Mutates system state: cpuset directories, IRQ affinities, workqueue masks, task CPU affinities, RCU stall suppression, and CPU frequency governor. Persistent capture output is a timestamped `.sr` zip containing metadata and binary sample data.

Dependencies/integration: Depends on root/debugfs access, kernel sloppy logic analyzer debugfs files, cpuset cgroup support, `taskset`, `zip`, `awk`, `find`, `ps`, and shell arithmetic.

Risks/tests: Risks are significant because it changes global CPU/IRQ/workqueue affinity and does not restore it, uses background capture after the parent exits, and writes debugfs/sysfs attributes directly. Test signals are `--list-instances`, dry validation on a test instance, trigger encoding for levels/edges, sample frequency capping output, `.sr` archive load in PulseView, and post-run CPU affinity audits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/gpio-sloppy-logic-analyzer.sh -->
