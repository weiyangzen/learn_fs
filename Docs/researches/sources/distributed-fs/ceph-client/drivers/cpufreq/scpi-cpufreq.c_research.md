<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/scpi-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/scpi-cpufreq.c

## Purpose

Implements cpufreq over the older ARM SCPI firmware interface, using SCPI-created OPPs and a firmware-backed CPU clock.

## APIs, Types, And Functions

`struct scpi_data` stores the CPU clock and CPU device. `scpi_cpufreq_init()` adds OPPs, determines sharing CPUs, builds a cpufreq table, gets the CPU clock, and configures policy state. `scpi_cpufreq_set_target()` calls `clk_set_rate()` and verifies the resulting rate. Probe gets `scpi_ops` and registers cpufreq.

## Control Flow

Platform probe obtains global SCPI ops, then registers the cpufreq driver. Policy init asks firmware to add OPPs for the CPU device, builds a shared policy mask from SCPI domain ids, marks OPPs shared, defers if OPPs are unavailable, allocates state, creates the frequency table, gets the CPU clock, sets any-CPU DVFS, latency, and disables fast switching. Exit releases clock, table, dynamic OPPs, and state.

## State And Persistence

Global `scpi_ops` is valid while the platform driver is registered. Per-policy `scpi_data` owns the clock reference and CPU device pointer. Firmware owns actual rate control state.

## Dependencies And Integration Points

Depends on `get_scpi_ops()`, SCPI domain ids, OPP framework, common clock, cpufreq energy-model registration with OPP, and platform-device binding `scpi-cpufreq`.

## Risks And Test Signals

Failure cleanup in init removes all dynamic OPPs, so partial policy setup must be tested. Target returns `-EIO` if the clock rate does not match the requested table frequency. Test signals include SCPI OPP creation, shared CPU mask, transition latency, clock get/set/readback, and successful cpufreq unregister on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/scpi-cpufreq.c -->
