## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-perf.c

Purpose: this file registers a perf PMU for DFL FME global performance counters. It exposes basic clock, cache, fabric, VT-d, and VT-d SIP events depending on whether the hardware feature is global IPERF or DPERF.

Important APIs and functions: `struct fme_perf_priv` stores device, MMIO base, PMU, feature ID, fabric mode state, active CPU, and CPU hotplug node. Event config fields are `event`, `evtype`, and `portid`. Event init functions validate per-counter constraints: basic clock is root-only, cache and VT-d/SIP are IPERF-only, fabric allows root or one port and filters unavailable DPERF events. Read functions program the event selector and poll counter event tags before reading. PMU callbacks implement init, add, del, start, stop, read, and destroy.

Control flow: feature init allocates private state, binds to the current CPU, sets up a dynamic CPU hotplug state, registers an instance, initializes fabric mode from hardware, registers a PMU named `dfl_fme<id>`, and stores private data on the feature. On CPU offline, the PMU context migrates to another online CPU. Uinit unregisters PMU and hotplug state.

State and persistence: PMU state includes active CPU and fabric counter mode. Fabric counters can operate in either root or one-port mode; `fab_users`, `fab_port_id`, and `fab_lock` prevent conflicting simultaneous fabric events. Hardware counters are free-running or selected through control registers. Perf event counts use deltas from previous hardware readings.

Dependencies and integration: it depends on Linux perf PMU APIs, CPU hotplug, DFL feature lifecycle, and FME MMIO. `dfl-fme-main.c` includes this feature ops table in the FME driver.

Risks: PMU supports only system-wide counting on the selected CPU; per-task and sampling events are rejected. Fabric mode sharing can reject otherwise valid events when another fabric event uses a different port mode. `PERF_MAX_PORT_NUM` is one, so multi-port hardware would need updates. Counter read helpers return zero on event-tag timeout, which can hide hardware failures as low counts. CPU hotplug state is dynamically allocated per feature instance.

Test signals: verify PMU sysfs format/events/cpumask, IPERF versus DPERF event visibility, per-task and sampling rejection, wrong CPU rejection, fabric root/port conflict handling, CPU offline migration, counter tag timeout logging, and event count deltas across repeated reads.
